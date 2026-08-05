from matcher.embeddings import get_similarity, chunk_resume

def test_similar_texts_score_higher_than_unrelated():
    related_score = get_similarity(
        "Built REST APIs using Node.js and Express",
        "Looking for a backend developer with API experience"
    )
    unrelated_score = get_similarity(
        "Built REST APIs using Node.js and Express",
        "A recipe for chocolate chip cookies"
    )
    assert related_score > unrelated_score

def test_chunk_resume_drops_short_lines():
    resume_text = "Skills:\nBuilt REST APIs using Node.js and Express\n\n123-456-7890"
    chunks = chunk_resume(resume_text)
    assert "Skills:" not in chunks
    assert any("REST APIs" in c for c in chunks)
