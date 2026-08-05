from keybert import KeyBERT
from matcher.embeddings import best_match, chunk_resume, embed_texts

kw_model = KeyBERT()

MATCH_THRESHOLD = 0.45 # Subject to change

def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1,2),
        stop_words="english",
        top_n=top_n,
    )
    return [kw for kw, score in keywords]

def semantic_keyword_analysis(resume_text: str, jd_text: str, top_n: int = 10) -> list[dict]:
    jd_keywords = extract_keywords(jd_text, top_n=top_n)
    chunks = chunk_resume(resume_text)

    if not chunks:
        return [{"keyword": kw, "matched": False, "best_chunk": None, "score": 0.0} for kw in jd_keywords]

    chunk_embeddings = embed_texts(chunks)

    results = []
    for kw in jd_keywords:
        chunk, score = best_match(kw, chunk_embeddings, chunks)
        results.append({
            "keyword": kw,
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

    # overall score = fraction of job description keywords matched, weighed slightly by how strong each match is
    coverage = len(matched) / len(results)
    avg_strength = sum(r["score"] for r in results) / len(results)
    overall_score = (coverage * 0.7) + (avg_strength * 0.3)

    return {
        "overall_score": overall_score,
        "matched": matched,
        "missing": missing,
        "keyword_results": results,
    }

# def find_missing_keywords(resume_text: str, jd_text: str, top_n: int = 10) -> list[str]:
#     jd_keywords = extract_keywords(jd_text, top_n=top_n)
#     resume_lower = resume_text.lower()
#     missing = [kw for kw in jd_keywords if kw.lower() not in resume_lower]
#     return missing

if __name__ == "__main__":
    resume = """Built REST APIs using Node.js and Express
    Containerized services for deployment across environments
    Worked with PostgreSQL for relational data storage"""
    jd = "Looking for a backend developer with experience in server-side development, Docker, and relational databases like PostgreSQL"

    print("JD keywords:", extract_keywords(jd))
    for result in semantic_keyword_analysis(resume, jd):
        print(result)
