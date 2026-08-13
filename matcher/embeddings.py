import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

model = SentenceTransformer("all-mpnet-base-v2")
nlp = spacy.load("en_core_web_sm")

BULLET_PATTERN = re.compile(r"^[•\-\*\u2022\u25AA\u25E6\u2023]\s*")

def get_similarity(text1: str, text2: str) -> float:
    embeddings = model.encode([text1, text2])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(score)

def chunk_resume(resume_text: str) -> list[str]:
    """Splits resume text into individual lines/points"""
    raw_lines = [line.strip() for line in resume_text.split("\n") if line.strip()]

    has_bullet_markers = any(BULLET_PATTERN.match(line) for line in raw_lines)

    if not has_bullet_markers:
        merged = [line for line in raw_lines if len(line) > 15]
    else:
        merged = []
        current_line = ""
        for line in raw_lines:
            is_bullet_start = bool(BULLET_PATTERN.match(line))
            if is_bullet_start:
                if current_line:
                    merged.append(current_line)
                current_line = BULLET_PATTERN.sub("", line)
            else:
                current_line = f"{current_line} {line}".strip() if current_line else line

        if current_line:
            merged.append(current_line)

        merged = [c for c in merged if len(c) > 15]

    chunks = []
    for bullet in merged:
        doc = nlp(bullet)
        for sentence in doc.sents:
            sentence_text = sentence.text.strip()
            if len(sentence_text) > 15:
                chunks.append(sentence_text)

    return chunks

def embed_texts(texts: list[str]):
    return model.encode(texts) # Batches all chunks in one call

def best_match(keyword: str, chunk_embeddings, chunks: list[str]):
    keyword_embedding = model.encode([keyword])
    sims = cosine_similarity(keyword_embedding, chunk_embeddings)[0]
    best_idx = sims.argmax()
    return chunks[best_idx], float(sims[best_idx])

if __name__ == "__main__":
    resume = "Built REST APIs using Node.js and Express, worked with PostgreSQL"
    jd = "Looking for a backend developer with experience in server-side development and relational databases"
    print(get_similarity(resume, jd))
