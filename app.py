import streamlit as st
from matcher.keywords import compute_match_report
from matcher.parser import extract_text, ParsingError

st.title("resumatch")
st.write("Upload your resume and paste a job description to see how well they match.")

resume_file = st.file_uploader("Upload your resume", type=["pdf", "docx"])
jd_text = st.text_area("Paste the job description", height=250)

if st.button("Analyze"):
    if not resume_file or not jd_text.strip():
        st.warning("Please upload a resume and paste a job description.")
    else:
        try:
            with st.spinner("Analyzing..."):
                resume_text = extract_text(resume_file)
                report = compute_match_report(resume_text, jd_text, 15)
        except ParsingError as e:
            st.error(str(e))
        else:
            st.metric("Match Score", f"{report["overall_score"]:.0%}")

            st.subheader(f"Matched keywords ({len(report["matched"])/len(report["keyword_results"])})")
            for r in report["matched"]:
                st.markdown(f"**{r['keyword']}** — matched via: *\"{r['best_chunk']}\"* (score: {r['score']:.2f})")

            if report["missing"]:
                st.subheader("Keywords not well covered by your resume")
                for r in report["missing"]:
                    st.markdown(f"- **{r['keyword']}** (closest line scored {r['score']:.2f})")
            else:
                st.success("No major keyword gaps found!")

            with st.expander("Extracted resume text (for debugging)"):
                st.text(resume_text)
