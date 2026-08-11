from matcher.keywords import extract_keywords, semantic_keyword_analysis, compute_match_report

SAMPLE_JD = """Looking for a backend developer with experience in server-side development,
Docker, dynamic programming, Seinfeld, and relational databases like PostgreSQL."""

SAMPLE_RESUME = """Built REST APIs using Node.js and Express
Containerized services for deployment across environments
Worked with PostgreSQL for relational data storage"""

def test_extract_keywords_does_not_merge_across_clauses():
    keywords = extract_keywords(SAMPLE_JD)
    lowered = [kw.lower() for kw, importance in keywords]
    assert "docker dynamic" not in lowered
    assert "seinfeld relational" not in lowered
    
def test_extract_keywords_finds_real_multiword_terms():
    keywords = extract_keywords(SAMPLE_JD)
    print(keywords)
    assert any("dynamic programming" in kw.lower() for kw, importance in keywords)

def test_extract_keywords_drops_generic_filler_terms():
    keywords = extract_keywords(SAMPLE_JD)
    lowered = [kw.lower() for kw, importance in keywords]
    for generic in ["looking", "like", "experience"]:
        assert generic not in lowered

def test_extract_keywords_removes_substring_duplicates():
    keywords = extract_keywords(SAMPLE_JD)
    lowered = [kw.lower() for kw, importance in keywords]
    assert not ("databases" in lowered and "relational databases" in lowered)

def test_compute_match_report_matched_and_missing_cover_all_keywords():
    report = compute_match_report(SAMPLE_RESUME, SAMPLE_JD)
    assert len(report["matched"]) + len(report["missing"]) == len(report["keyword_results"])
