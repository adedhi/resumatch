import streamlit as st
from matcher.embeddings import get_similarity
from matcher.keywords import find_missing_keywords
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
            missing = find_missing_keywords(resume_text, jd_text)

        st.metric("Match Score", f"{score:.2f}")

        if missing:
            st.subheader("Keywords in the job posting but missing from your resume")
            for kw in missing:
                st.markdown(f"- {kw}")
        else:
            st.success("No major keyword gaps found!")

        with st.expander("Extracted resume text (for debugging)"):
            st.text(resume_text)
