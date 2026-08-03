from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_similarity(text1: str, text2: str) -> float:
    embeddings = model.encode([text1, text2])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(score)

if __name__ == "__main__":
    resume = "Built REST APIs using Node.js and Express, worked with PostgreSQL"
    jd = "Looking for a backend developer with experience in server-side development and relational databases"
    print(get_similarity(resume, jd))
