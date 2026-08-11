import io
import streamlit as st
from matcher.keywords import compute_match_report
from matcher.parser import extract_text, ParsingError

@st.cache_data
def cached_extract_text(file_bytes: bytes, filename: str) -> str:
    class _BytesFile:
        def __init__(self, data: bytes, name: str):
            self.name = name
            self._buffer = io.BytesIO(data)

        def __getattr__(self, attr):
            return getattr(self._buffer, attr)

    fake_file = _BytesFile(file_bytes, filename)
    return extract_text(fake_file)

@st.cache_data
def cached_compute_match_report(resume_text: str, jd_text: str, top_n: int = 10) -> dict:
    return compute_match_report(resume_text, jd_text, top_n)

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
                resume_text = cached_extract_text(resume_file.getvalue(), resume_file.name)
                report = cached_compute_match_report(resume_text, jd_text, 15)
        except ParsingError as e:
            st.error(str(e))
        else:
            st.metric("Match Score", f"{report["overall_score"]:.0%}")

            matched_sorted = sorted(report["matched"], key=lambda r: r["importance"], reverse=True)
            missing_sorted = sorted(report["missing"], key=lambda r: r["importance"], reverse=True)

            if report["keyword_results"]:
                st.subheader(f"Matched keywords ({len(report["matched"])/len(report["keyword_results"]):.2f})")
            else:
                st.subheader("Matched keywords (0/0)")
            for r in matched_sorted:
                st.markdown(f"**{r['keyword']}** — matched via: *\"{r['best_chunk']}\"* (score: {r['score']:.2f})")

            if missing_sorted:
                st.subheader("Keywords not well covered by your resume")
                for r in missing_sorted:
                    urgency = "🔴" if r["importance"] > 0.6 else "🟡"
                    st.markdown(f"{urgency} **{r['keyword']}** (closest line scored {r['score']:.2f})")
            else:
                st.success("No major keyword gaps found!")

            with st.expander("Extracted resume text (for debugging)"):
                st.text(resume_text)
