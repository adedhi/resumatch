import streamlit as st
from matcher.embeddings import get_similarity
from matcher.keywords import semantic_keyword_analysis
from matcher.parser import extract_text

st.title("resumatch")
st.write("Upload your resume and paste a job description to see how well they match.")

resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
jd_text = st.text_area("Paste the job description", height=250)

if st.button("Analyze"):
    if not resume_file or not jd_text.strip():
        st.warning("Please upload a resume and paste a job description.")
    else:
        with st.spinner("Analyzing..."):
            resume_text = extract_text(resume_file)
            score = get_similarity(resume_text, jd_text)
            keyword_results = semantic_keyword_analysis(resume_text, jd_text)

        st.metric("Match Score", f"{score:.2f}")

        matched = [r for r in keyword_results if r["matched"]]
        missing = [r for r in keyword_results if not r["matched"]]

        st.subheader(f"Matched keywords ({len(matched)}/{len(keyword_results)})")
        for r in matched:
            st.markdown(f"**{r['keyword']}** — matched via: *\"{r['best_chunk']}\"* (score: {r['score']:.2f})")

        if missing:
            st.subheader("Keywords not well covered by your resume")
            for r in missing:
                st.markdown(f"- **{r['keyword']}** (closest line scored {r['score']:.2f})")
        else:
            st.success("No major keyword gaps found!")

        with st.expander("Extracted resume text (for debugging)"):
            st.text(resume_text)
