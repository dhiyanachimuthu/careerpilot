import json
import sqlite3
from pathlib import Path
import streamlit as st
from database import (create_tables, create_candidate, candidates, candidate,
                      update_candidate, add_resume, resumes, save_extraction)
from resume_parser import extract_text, store_file
from llm_extractor import extract_profile, MODEL

st.set_page_config(page_title='CareerPilot', page_icon='🎓', layout='wide')
create_tables()
st.title('🎓 CareerPilot')
st.caption('Infosys Virtual Internship • Milestone 1: Foundation & Candidate Understanding')
page = st.sidebar.radio('Navigation', ['Dashboard','Create Profile','View / Edit Profiles',
                                       'Upload Resume','AI Resume Extraction','Architecture & Research'])

def selector(label='Choose student'):
    people = candidates()
    if not people:
        st.warning('Create a student profile first.')
        return None
    options = {f"{p['full_name']} (ID {p['id']})":p['id'] for p in people}
    return options[st.selectbox(label, list(options))]

if page == 'Dashboard':
    a,b,c = st.columns(3)
    a.metric('Student profiles',len(candidates()))
    b.metric('LLM provider','Groq')
    c.metric('Database','SQLite')
    st.markdown("""### Implemented in Milestone 1
    - Student profile creation and editing
    - Resume upload, file storage and metadata persistence
    - PDF, DOCX and TXT text extraction
    - Hosted LLM extraction, Pydantic validation and candidate profile persistence

    ### Designed for later milestones
    Job-Resume Matching, Skill Gap, Resume, Cover Letter, Interview and Career Assistant agents;
    RAG job-posting knowledge base and application tracking.""")

elif page == 'Create Profile':
    st.subheader('Create student profile')
    with st.form('create'):
        name = st.text_input('Full name')
        email = st.text_input('Email')
        phone = st.text_input('Phone')
        location = st.text_input('Location')
        submit = st.form_submit_button('Create profile')
    if submit:
        if not name.strip() or '@' not in email or '.' not in email.split('@')[-1]:
            st.error('Enter a name and valid-looking email address.')
        else:
            try:
                cid = create_candidate(name,email,phone,location)
                st.success(f'Created candidate ID {cid}')
            except sqlite3.IntegrityError:
                st.error('This email is already registered.')

elif page == 'View / Edit Profiles':
    st.subheader('View and edit student profiles')
    cid = selector()
    if cid is not None:
        p = candidate(cid)
        with st.form('edit'):
            name = st.text_input('Full name',p['full_name'])
            email = st.text_input('Email',p['email'])
            phone = st.text_input('Phone',p['phone'] or '')
            location = st.text_input('Location',p['location'] or '')
            submit = st.form_submit_button('Save changes')
        if submit:
            if not name.strip() or '@' not in email:
                st.error('Name and valid email are required.')
            else:
                try:
                    update_candidate(cid,name,email,phone,location)
                    st.success('Profile updated')
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error('That email belongs to another profile.')
        st.subheader('Extracted candidate information')
        st.write('**Summary:**',p['summary'] or 'Not extracted yet')
        for field in ('skills','education','experience','projects','certifications'):
            with st.expander(field.title(), expanded=field=='skills'):
                st.json(json.loads(p[field] or '[]'))
        st.subheader('Uploaded resume metadata')
        records = resumes(cid)
        if records:
            for r in records:
                    st.json(r)
        else:
            st.info('No resumes stored yet.')

elif page == 'Upload Resume':
    st.subheader('Upload and save a resume')
    cid = selector()
    if cid is not None:
        uploaded = st.file_uploader('Choose PDF, DOCX or TXT',type=['pdf','docx','txt'])
        if uploaded and st.button('Save resume'):
            try:
                content = uploaded.getvalue()
                text = extract_text(uploaded.name,content)
                metadata = store_file(uploaded.name,content)
                add_resume(cid,metadata)
                st.success('Resume file and metadata saved')
                st.json(metadata)
                st.text_area('Extracted text preview',text,height=200)
            except Exception as e:
                st.error(f'Upload failed: {e}')

elif page == 'AI Resume Extraction':
    st.subheader('Extract structured candidate data with an LLM')
    st.caption(f'Hosted model: {MODEL} via Groq. Resume text is sent to Groq for processing.')
    cid = selector()
    if cid is not None:
        key = st.text_input('Groq API key (not saved)',type='password')
        uploaded = st.file_uploader('Select a resume',type=['pdf','docx','txt'],key='ai_upload')
        if st.button('Extract and save profile'):
            if not key or not uploaded:
                st.warning('Enter an API key and select a resume.')
            else:
                try:
                    with st.spinner('Extracting with hosted LLM...'):
                        text = extract_text(uploaded.name,uploaded.getvalue())
                        result = extract_profile(text,key)
                        save_extraction(cid,result)
                    st.success('LLM extraction validated and saved to candidate profile')
                    st.json(result)
                    st.info('Open View / Edit Profiles to verify the saved information. '
                            'Use Upload Resume separately to retain the original file.')
                except Exception as e:
                    st.error(str(e))

else:
    st.subheader('Architecture and technical research')
    for filename in ['docs/ARCHITECTURE.md','docs/RESEARCH.md','docs/TECH_STACK.md']:
        with st.expander(filename,expanded=filename.endswith('ARCHITECTURE.md')):
            st.markdown((Path(__file__).resolve().parent/filename).read_text(encoding='utf-8'))
