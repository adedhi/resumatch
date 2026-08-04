from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_similarity(text1: str, text2: str) -> float:
    embeddings = model.encode([text1, text2])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(score)

def chunk_resume(resume_text: str) -> list[str]:
    """Splits resume text into individual lines/points"""
    lines = resume_text.split("\n")
    chunks = [line.strip() for line in lines if len(line.strip()) > 15] # Drops lines under 16 characters
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
