import streamlit as st
from parser import extract_text_from_file, extract_entities
from scorer import score_resume
from utils import display_entities, check_ats_compliance
import streamlit_lottie as st_lottie
import requests
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Load Lottie Animation ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://lottie.host/804a3a69-2be3-4ff9-8265-8f67c182ae4a/2a1X9H6Y0Y.json"
lottie_json = load_lottieurl(lottie_url)

# --- Email Function ---
def send_email(to_email, report_content):
    msg = MIMEMultipart()
    msg["From"] = st.secrets["email"]["username"]
    msg["To"] = to_email
    msg["Subject"] = "Resume Analysis Report"
    
    body = MIMEText(report_content, "plain")
    msg.attach(body)
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(st.secrets["email"]["username"], st.secrets["email"]["password"])
            server.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Failed to send email: {str(e)}")
        return False

# --- Custom Futuristic UI Style ---
def apply_futuristic_style():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&family=Roboto+Mono&display=swap');
            
            /* Main background and text */
            html, body, [class*="css"] {
                font-family: 'Roboto Mono', monospace;
                background: linear-gradient(315deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
                color: #ffffff;
            }
            
            /* Headers */
            h1, h2, h3, h4 {
                color: #00ffff;
                font-family: 'Orbitron', sans-serif;
                text-shadow: 0 0 8px #0ff, 0 0 12px #0ff;
            }
            
            /* Buttons */
            .stButton>button {
                background: linear-gradient(135deg, #00ffff, #00ff99);
                color: #000;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-weight: bold;
                box-shadow: 0 0 10px #00ffff;
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 20px #00ffcc;
            }
            
            /* Input fields */
            .stTextInput>div>input, 
            .stTextArea>div>textarea {
                background-color: #1e1e1e;
                color: #00ffff;
                border: 1px solid #00ffff;
            }
            
            /* File uploader */
            .stFileUploader {
                background-color: #1b1f23;
                border-radius: 10px;
                padding: 1em;
                border: 1px solid #00ffff;
            }
            
            /* Progress bar */
            .progress-container {
                background: #1a1a1a;
                border-radius: 25px;
                padding: 5px;
                margin: 15px 0;
                box-shadow: 0 0 12px #00ffff80;
            }
            .progress-fill {
                background: linear-gradient(90deg, #00ffff, #00ff99);
                height: 20px;
                border-radius: 20px;
                transition: width 0.5s ease;
                animation: glow 1.5s infinite alternate;
            }
            @keyframes glow {
                from { box-shadow: 0 0 10px #00ffff; }
                to { box-shadow: 0 0 20px #00ffff; }
            }
            
            /* Skill match boxes */
            .skill-match {
                background-color: rgba(0, 255, 255, 0.1);
                border: 1px solid #00ffff;
                border-radius: 15px;
                padding: 15px;
                margin-bottom: 15px;
            }
            .skill-item {
                margin: 5px 0;
                padding: 8px 12px;
                border-radius: 8px;
            }
            .matched {
                background-color: rgba(0, 255, 0, 0.1);
                border-left: 4px solid #00ff99;
            }
            .missing {
                background-color: rgba(255, 0, 0, 0.1);
                border-left: 4px solid #ff5555;
            }
            
            /* Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-thumb {
                background: #00ffff;
                border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

apply_futuristic_style()

# --- Session State ---
if 'page' not in st.session_state:
    st.session_state.page = "landing"

# --- Landing Page ---
if st.session_state.page == "landing":
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🚀 AI Resume Analyzer</h1>", unsafe_allow_html=True)
    st_lottie.st_lottie(lottie_json, height=350, key="landing")
    st.markdown("<p style='text-align: center; font-size: 1.2rem;'>Make your resume smarter using AI & NLP</p>", unsafe_allow_html=True)

    if st.button("🔍 Get Started"):
        st.session_state.page = "analyzer"
        st.rerun()

# --- Analyzer Page ---
elif st.session_state.page == "analyzer":
    st.title("📄 Resume Analyzer")

    uploaded_file = st.file_uploader("📎 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
    job_skills_input = st.text_input("💼 Job Requirement Skills (comma-separated)", 
                                   value="python, machine learning, sql, html, css, javascript")

    if uploaded_file:
        file_ext = uploaded_file.name.split('.')[-1]
        with open(f"temp_resume.{file_ext}", "wb") as f:
            f.write(uploaded_file.read())

        with st.spinner("🔍 Analyzing Resume..."):
            text = extract_text_from_file(f"temp_resume.{file_ext}")
            entities = extract_entities(text)
            job_skills = [skill.strip().lower() for skill in job_skills_input.split(",")]
            
            result = score_resume(entities, job_skills, raw_text=text)
            ats_warnings = check_ats_compliance(text)

        # --- Results ---
        st.subheader("🔎 Extracted Information")
        st.markdown(display_entities(entities), unsafe_allow_html=True)

        if ats_warnings:
            for warning in ats_warnings:
                st.warning(warning)

        st.subheader("📊 Skill Matching Results")
        
        # Progress bar with percentage
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-fill" style="width: {result['score']}%"></div>
        </div>
        <p style="text-align: center; font-size: 1.5rem;"><strong>{result['score']}% Match</strong></p>
        """, unsafe_allow_html=True)

        # Skills breakdown
        st.markdown("""
        <div class="skill-match">
            <h4 style="color: #00ffff; margin-bottom: 15px;">Skills Breakdown</h4>
        """, unsafe_allow_html=True)
        
        if result['matched_skills']:
            st.markdown("✅ **Matched Skills**")
            for skill in result['matched_skills']:
                st.markdown(f"""
                <div class="skill-item matched">
                    {skill.capitalize()}
                </div>
                """, unsafe_allow_html=True)
        
        if result['missing_skills']:
            st.markdown("❌ **Missing Skills**")
            for skill in result['missing_skills']:
                st.markdown(f"""
                <div class="skill-item missing">
                    {skill.capitalize()}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Report Generation ---
        report_content = f"""Resume Analysis Report

Name: {entities['name']}
Email: {entities['email'][0] if entities['email'] else 'N/A'}
Phone: {entities['phone'][0] if entities['phone'] else 'N/A'}

SKILL ANALYSIS
Required Skills: {', '.join(job_skills)}
Resume Skills: {', '.join(entities['skills']) or "None"}
Matched Skills: {', '.join(result['matched_skills']) or "None"}
Missing Skills: {', '.join(result['missing_skills']) or "None"}
Match Percentage: {result['score']}%

ATS COMPLIANCE CHECK:
{chr(10).join(ats_warnings) if ats_warnings else "No issues found"}
"""

        # --- Export Options ---
        st.subheader("📥 Export Options")
        
        col1, col2 = st.columns(2)
        with col1:
            # CSV Export
            if st.button("💾 Save to CSV"):
                df = pd.DataFrame({
                    "Name": [entities["name"]],
                    "Email": [entities["email"][0] if entities["email"] else "N/A"],
                    "Phone": [entities["phone"][0] if entities["phone"] else "N/A"],
                    "Match_Percentage": [result["score"]],
                    "Matched_Skills": [", ".join(result["matched_skills"])],
                    "Missing_Skills": [", ".join(result["missing_skills"])],
                    "ATS_Warnings": [", ".join(ats_warnings) if ats_warnings else "None"]
                })
                df.to_csv("resume_report.csv", index=False)
                st.success("Report saved as CSV!")
        
        with col2:
            # Email Report
            email_address = st.text_input("Enter email address:")
            if st.button("📧 Email Report") and email_address:
                if send_email(email_address, report_content):
                    st.success("Report sent successfully!")
                else:
                    st.error("Failed to send email. Check credentials.")

        # Text Download
        st.download_button(
            label="📄 Download Text Report",
            data=report_content,
            file_name="resume_report.txt",
            mime="text/plain"
        )

        # Debug view
        if st.checkbox("Show debug information"):
            st.subheader("Debug View")
            col1, col2 = st.columns(2)
            with col1:
                st.text_area("Extracted Text", text, height=300)
            with col2:
                st.json(entities)