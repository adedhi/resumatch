from keybert import KeyBERT

kw_model = KeyBERT()

def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1,2),
        stop_words="english",
        top_n=top_n,
    )
    return [kw for kw, score in keywords]

def find_missing_keywords(resume_text: str, jd_text: str, top_n: int = 10) -> list[str]:
    jd_keywords = extract_keywords(jd_text, top_n=top_n)
    resume_lower = resume_text.lower()
    missing = [kw for kw in jd_keywords if kw.lower() not in resume_lower]
    return missing

if __name__ == "__main__":
    resume = "Built REST APIs using Node.js and Express, worked with PostgreSQL"
    jd = "Looking for a backend developer with experience in server-side development, Docker, and relational databases like PostgreSQL"

    print("JD keywords:", extract_keywords(jd))
    print("Missing from resume:", find_missing_keywords(resume, jd))
