"""CareerPilot — refined Streamlit interface. Drop-in replacement for app.py."""
import json
import sqlite3
from pathlib import Path
from html import escape

import streamlit as st
from database import (create_tables, create_candidate, candidates, candidate,
                      update_candidate, add_resume, resumes, save_extraction)
from resume_parser import extract_text, store_file
from llm_extractor import extract_profile, MODEL

st.set_page_config(page_title="CareerPilot | Student workspace", page_icon="🌿", layout="wide", initial_sidebar_state="expanded")
create_tables()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {--paper:#f7f4f0;--white:#fffdfa;--ink:#303c3a;--muted:#78817e;--rose:#d9a9af;--teal:#8daFAA;--line:#e7e4de;}
html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans',sans-serif;}
[data-testid="stAppViewContainer"] {background:#f7f4f0;color:#303c3a;}
[data-testid="stHeader"] {background:transparent;}
.block-container {padding-top:2.1rem;max-width:1120px;padding-bottom:4rem;}
h1,h2,h3 {font-family:'Manrope',sans-serif!important;letter-spacing:-.035em!important;color:#303c3a!important;}
h1 {font-weight:800!important;font-size:2.15rem!important;}
h2 {font-weight:750!important;font-size:1.45rem!important;}
h3 {font-weight:700!important;font-size:1.06rem!important;}
[data-testid="stSidebar"] {background:#efeee9;border-right:1px solid #e4e0da;}
[data-testid="stSidebar"] .block-container {padding-top:2rem;}
[data-testid="stSidebar"] [role="radiogroup"] label {padding:.45rem .65rem;border-radius:9px;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {background:#dfe9e4;}
[data-testid="stSidebar"] hr {border-color:#deded8;}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"] {background:#456e67!important;color:white!important;border:1px solid #456e67!important;}
.stButton>button,.stFormSubmitButton>button {border-radius:10px!important;padding:.55rem 1.2rem!important;font-weight:650!important;border:1px solid #d5dad4!important;background:#fffdfa;color:#34514d;}
.stButton>button:hover,.stFormSubmitButton>button:hover {border-color:#7eaaa1!important;color:#2c6157!important;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stSelectbox"]>div>div,[data-testid="stFileUploader"] section {border-radius:10px!important;border-color:#d9ded8!important;background:#fffdfa!important;}
[data-testid="stForm"], [data-testid="stExpander"] {background:#fffdfa;border:1px solid #e8e4df!important;border-radius:14px!important;padding:12px 17px;}
[data-testid="stAlert"] {border-radius:11px;}
[data-testid="stMetric"] {background:#fffdfa;border:1px solid #e8e4df;padding:18px;border-radius:14px;}
[data-testid="stMetricValue"] {font-size:1.65rem!important;color:#303c3a;}
[data-testid="stMetricLabel"] {color:#78817e;}
.cp-eyebrow {font-size:.71rem;letter-spacing:.16em;text-transform:uppercase;color:#8d757b;font-weight:800;margin:0 0 10px;}
.cp-intro {color:#78817e;font-size:1rem;line-height:1.7;max-width:760px;margin:0 0 28px;}
.cp-hero {background:#fffdfa;border:1px solid #e8e4df;border-radius:18px;padding:30px 34px;margin-bottom:24px;position:relative;overflow:hidden;}
.cp-hero:before {content:'';position:absolute;right:0;top:0;width:7px;height:100%;background:#cda3aa;}
.cp-hero h1 {margin:0 0 9px;font-size:2rem;}
.cp-hero p {color:#76817e;margin:0;line-height:1.65;}
.cp-card {background:#fffdfa;border:1px solid #e8e4df;border-radius:15px;padding:23px;margin:8px 0 15px;min-height:140px;}
.cp-card h3 {margin:0 0 9px;font-size:1rem!important;}
.cp-card p {color:#77817d;font-size:.91rem;line-height:1.6;margin:0;}
.cp-pill {display:inline-block;background:#e4eeea;color:#4d746c;border-radius:99px;font-size:.72rem;font-weight:750;padding:5px 10px;margin:0 0 12px;}
.cp-meta {border:1px solid #e8e4df;background:#fffdfa;padding:15px 18px;border-radius:12px;margin:9px 0;}
.cp-meta strong {font-size:.95rem;color:#354440;}
.cp-meta small {display:block;color:#7e8580;margin-top:5px;}
.cp-divider {border-top:1px solid #e7e4de;margin:23px 0;}
.cp-section {font-weight:750;color:#354440;margin:22px 0 12px;font-size:1.1rem;}
.cp-empty {color:#85908a;font-size:.92rem;padding:15px 0;}
</style>
""", unsafe_allow_html=True)

NAV = ["Overview", "Create profile", "Student profiles", "Resume upload", "AI extraction", "Architecture & research"]
st.sidebar.markdown('<div class="cp-eyebrow">STUDENT WORKSPACE</div>',unsafe_allow_html=True)
st.sidebar.markdown('## CareerPilot')
st.sidebar.caption('Candidate intelligence platform')
st.sidebar.divider()
page = st.sidebar.radio("WORKSPACE", NAV, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("INFOSYS VIRTUAL INTERNSHIP")
st.sidebar.markdown("**Milestone 01**  ·  Foundation & candidate understanding")
st.sidebar.caption("Private local workspace · Groq-hosted AI")

def heading(kicker,title,description):
    st.markdown(f'<div class="cp-eyebrow">{escape(kicker)}</div><h1>{escape(title)}</h1><p class="cp-intro">{escape(description)}</p>',unsafe_allow_html=True)

def select_candidate():
    people = candidates()
    if not people:
        st.info("No profiles yet. Create a student profile to continue.")
        return None
    choices = {f"{p['full_name']} · #{p['id']}":p['id'] for p in people}
    return choices[st.selectbox("Student",list(choices))]

def safe_list(raw):
    try:
        val=json.loads(raw or '[]')
        return val if isinstance(val,list) else []
    except (ValueError,TypeError):
        return []

def show_details(items):
    if not items:
        st.caption("No information extracted yet.")
        return
    for item in items:
        if isinstance(item,dict):
            title=(item.get('name') or item.get('role') or item.get('degree') or item.get('institution') or 'Entry')
            st.markdown(f"**{escape(str(title))}**")
            for key,value in item.items():
                if key in ('name','role','degree') or not value: continue
                st.caption(f"{key.replace('_',' ').title()}: {', '.join(map(str,value)) if isinstance(value,list) else value}")
        else:
            st.markdown(f"• {escape(str(item))}")

if page == "Overview":
    st.markdown('<div class="cp-hero"><div class="cp-eyebrow">YOUR CAREER WORKSPACE</div><h1>A clearer picture of your next step.</h1><p>Organize your student profile, understand your resume, and prepare for future internship opportunities — all in one place.</p></div>',unsafe_allow_html=True)
    people=candidates()
    count=sum(len(resumes(p['id'])) for p in people)
    a,b,c=st.columns(3)
    a.metric("Student profiles",len(people))
    b.metric("Uploaded resumes",count)
    c.metric("AI extraction","Available")
    st.markdown('<div class="cp-section">Your workspace</div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        st.markdown('<div class="cp-card"><span class="cp-pill">01 · Profile</span><h3>Keep your story organized</h3><p>Create and update candidate details, education, skills, and experience in a structured record.</p></div>',unsafe_allow_html=True)
        st.markdown('<div class="cp-card"><span class="cp-pill">03 · Understand</span><h3>Extract resume insights</h3><p>Use a hosted language model to identify skills, education, projects and experience from your resume.</p></div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="cp-card"><span class="cp-pill">02 · Documents</span><h3>Keep resumes together</h3><p>Upload PDF, DOCX or TXT resumes and retain file metadata in your local database.</p></div>',unsafe_allow_html=True)
        st.markdown('<div class="cp-card"><span class="cp-pill">04 · Roadmap</span><h3>Built to grow with you</h3><p>Six specialized agents, RAG job retrieval and application tracking are designed for later milestones.</p></div>',unsafe_allow_html=True)

elif page == "Create profile":
    heading("01 / PROFILE","Create a student profile","Start with the essentials. You can update these details whenever you need.")
    with st.form("create_profile"):
        left,right=st.columns(2)
        with left:
            name=st.text_input("Full name",placeholder="Your full name")
            email=st.text_input("Email address",placeholder="name@example.com")
        with right:
            phone=st.text_input("Phone number",placeholder="Optional")
            location=st.text_input("Location",placeholder="City, state")
        submit=st.form_submit_button("Create profile",type="primary")
    if submit:
        if not name.strip() or '@' not in email or '.' not in email.split('@')[-1]:
            st.error("Please enter a full name and valid-looking email address.")
        else:
            try:
                cid=create_candidate(name,email,phone,location)
                st.success(f"Profile created successfully · Student ID {cid}")
            except sqlite3.IntegrityError:
                st.error("A profile already exists with this email address.")

elif page == "Student profiles":
    heading("02 / CANDIDATES","Student profiles","Review saved candidate details, resume insights, and uploaded document records.")
    cid=select_candidate()
    if cid is not None:
        p=candidate(cid)
        st.markdown('<div class="cp-section">Personal information</div>',unsafe_allow_html=True)
        with st.form("edit_profile"):
            left,right=st.columns(2)
            with left:
                name=st.text_input("Full name",p['full_name'])
                email=st.text_input("Email address",p['email'])
            with right:
                phone=st.text_input("Phone number",p['phone'] or '')
                location=st.text_input("Location",p['location'] or '')
            submit=st.form_submit_button("Save changes",type="primary")
        if submit:
            if not name.strip() or '@' not in email:
                st.error("A name and valid email address are required.")
            else:
                try:
                    update_candidate(cid,name,email,phone,location)
                    st.success("Changes saved.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That email belongs to another profile.")
        st.markdown('<div class="cp-section">Resume insights</div>',unsafe_allow_html=True)
        st.markdown("**Professional summary**")
        st.write(p['summary'] or 'No summary extracted yet.')
        tabs=st.tabs(["Skills","Education","Experience","Projects","Certifications"])
        for tab,field in zip(tabs,['skills','education','experience','projects','certifications']):
            with tab:
                show_details(safe_list(p.get(field)))
        st.markdown('<div class="cp-section">Uploaded resume metadata</div>',unsafe_allow_html=True)
        records=resumes(cid)
        if records:
            for record in records:
                fname=escape(str(record.get('filename','Resume')))
                ftype=escape(str(record.get('file_type','')))
                fsize=record.get('file_size',0)
                when=escape(str(record.get('uploaded_at','')))
                st.markdown(f'<div class="cp-meta"><strong>{fname}</strong><small>{ftype.upper()} · {fsize/1024:.1f} KB · Uploaded {when}</small></div>',unsafe_allow_html=True)
                with st.expander(f"Technical metadata · Resume #{record.get('id','')}"):
                    st.json(record)
        else:
            st.caption("No resumes uploaded for this student yet.")

elif page == "Resume upload":
    heading("03 / DOCUMENTS","Upload a resume","Store a resume and its metadata securely in your local CareerPilot workspace.")
    cid=select_candidate()
    if cid is not None:
        uploaded=st.file_uploader("Choose a resume",type=['pdf','docx','txt'],help="PDF, DOCX or TXT · Maximum 5 MB")
        if uploaded:
            st.caption(f"Selected: {uploaded.name} · {uploaded.size/1024:.1f} KB")
        if st.button("Save resume",type="primary",disabled=uploaded is None):
            try:
                content=uploaded.getvalue()
                text=extract_text(uploaded.name,content)
                metadata=store_file(uploaded.name,content)
                add_resume(cid,metadata)
                st.success("Resume and metadata saved successfully.")
                with st.expander("Preview extracted text"):
                    st.text_area("Resume text",text,height=240,label_visibility="collapsed")
            except Exception as e:
                st.error(f"Could not upload resume: {e}")

elif page == "AI extraction":
    heading("04 / INTELLIGENCE","Understand your resume","Turn resume text into a structured candidate profile using a hosted language model.")
    st.caption(f"Model: {MODEL} · Provider: Groq · Resume text is sent to Groq for analysis")
    cid=select_candidate()
    if cid is not None:
        key=st.text_input("Groq API key",type="password",help="Entered for this session; do not include your key in GitHub.")
        uploaded=st.file_uploader("Resume to analyze",type=['pdf','docx','txt'],key='ai_resume')
        if st.button("Extract and save profile",type="primary",disabled=uploaded is None):
            if not key.strip():
                st.warning("Enter your Groq API key to continue.")
            else:
                try:
                    with st.spinner("Reading and analyzing your resume..."):
                        text=extract_text(uploaded.name,uploaded.getvalue())
                        result=extract_profile(text,key)
                        save_extraction(cid,result)
                    st.success("Extraction completed. Candidate profile updated.")
                    st.markdown('<div class="cp-section">Extracted information</div>',unsafe_allow_html=True)
                    st.json(result)
                    st.caption("Review the details under Student profiles. Upload the resume separately if you want to store the original file.")
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

else:
    heading("05 / PROJECT","Architecture & research","Technical foundations, candidate data flow, and the planned multi-agent system.")
    for filename,title in [('docs/ARCHITECTURE.md','System architecture'),('docs/RESEARCH.md','Research findings'),('docs/TECH_STACK.md','Technology stack')]:
        with st.expander(title,expanded=filename.endswith('ARCHITECTURE.md')):
            path=Path(__file__).resolve().parent/filename
            if path.exists():
                st.markdown(path.read_text(encoding='utf-8'))
            else:
                st.info(f"Documentation not found: {filename}")
