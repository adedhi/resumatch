from keybert import KeyBERT
from matcher.embeddings import best_match, chunk_resume, embed_texts
import re

kw_model = KeyBERT()

MATCH_THRESHOLD = 0.4 # Subject to change
MIN_KEYWORD_SCORE = 0.15 # Subject to change

GENERIC_TERMS = {"looking", "like", "experience", "seeking", "need", "needs"}

def is_generic(keyword: str) -> bool:
    words = keyword.lower().split()
    return any(word in GENERIC_TERMS for word in words)

def remove_substring_duplicates(keywords: list[str]) -> list[str]:
    """Drop shorter keywords that are just a substring of longer, existing ones."""
    result = []
    for kw in keywords:
        if not any(kw.lower() in other.lower() and kw.lower() != other.lower() for other in keywords):
            result.append(kw)
    return result

def split_into_clauses(text: str) -> list[str]:
    """Split on punctuation so keyword phrases can never span unrelated clauses."""
    clauses = re.split(r"[,.;]", text)
    return [c.strip() for c in clauses if len(c.strip()) > 2]

def extract_keywords(text: str, top_n: int = 10) -> list[tuple[str, float]]:
    clauses = split_into_clauses(text)
    if not clauses:
        clauses = [text]

    all_keywords = []
    for clause in clauses:
        keywords = kw_model.extract_keywords(
            clause,
            keyphrase_ngram_range=(1,2),
            stop_words="english",
            top_n=top_n,
        )
        all_keywords.extend(keywords)
    best_scores = {}
    for kw, score in all_keywords:
        kw_lower = kw.lower()
        if kw_lower not in best_scores or score > best_scores[kw_lower][1]:
            best_scores[kw_lower] = (kw, score)

    sorted_keywords = sorted(best_scores.values(), key=lambda x: x[1], reverse=True)
    filtered_keywords = [(kw, score) for kw, score in sorted_keywords if not is_generic(kw) and score >= MIN_KEYWORD_SCORE]
    deduped_keywords_list = remove_substring_duplicates([kw for kw, score in filtered_keywords])
    final_keywords = [(kw, score) for kw, score in filtered_keywords if kw in deduped_keywords_list]
    return final_keywords[:top_n]

def semantic_keyword_analysis(resume_text: str, jd_text: str, top_n: int = 10) -> list[dict]:
    jd_keywords = extract_keywords(jd_text, top_n=top_n)
    chunks = chunk_resume(resume_text)

    if not chunks:
        return [{"keyword": kw, "matched": False, "best_chunk": None, "score": 0.0} for kw in jd_keywords]

    chunk_embeddings = embed_texts(chunks)

    results = []
    for kw, importance in jd_keywords:
        chunk, score = best_match(kw, chunk_embeddings, chunks)
        results.append({
            "keyword": kw,
            "importance": importance,
            "matched": score >= MATCH_THRESHOLD,
            "best_chunk": chunk,
            "score": score,
        })
    return results

def compute_match_report(resume_text: str, jd_text: str, top_n: int = 10) -> dict:
    results = semantic_keyword_analysis(resume_text, jd_text, top_n=top_n)

    if not results:
        return {"overall_score": 0.0, "matched": [], "missing": [], "keyword_results": []}

    matched = [r for r in results if r["matched"]]
    missing = [r for r in results if not r["matched"]]

    total_importance = sum(r["importance"] for r in results)

    # overall score = fraction of job description keywords matched, weighed slightly by how strong each match is
    coverage = sum(r["importance"] for r in matched) / total_importance if total_importance > 0 else 0.0
    avg_strength = sum(r["score"] for r in results) / len(results)
    overall_score = (coverage * 0.7) + (avg_strength * 0.3)

    return {
        "overall_score": overall_score,
        "matched": matched,
        "missing": missing,
        "keyword_results": results,
    }

if __name__ == "__main__":
    resume = """Built REST APIs using Node.js and Express
    Containerized services for deployment across environments
    Worked with PostgreSQL for relational data storage"""
    jd = """Looking for a backend developer with experience in server-side development,
Docker, dynamic programming, Seinfeld, and relational databases like PostgreSQL."""

    print("JD keywords:", extract_keywords(jd))
    for result in semantic_keyword_analysis(resume, jd, 15):
        print(result)
