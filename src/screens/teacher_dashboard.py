import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

from src.database.db import get_teacher_subjects, get_attendance_for_teacher
from src.database.config import supabase
from src.pipelines.face_pipeline import predict_attendance
from src.components.subject_card import subject_card
from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.database.teacher_auth import teacher_login, check_teacher_exists, create_teacher


def _inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
 
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 50%, #f5f7ff 100%) !important;
        background-attachment: fixed !important;
    }
    [data-testid="stMain"] { background: transparent !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 0 !important;
        max-width: 1100px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
 
    /* NAVBAR */
    .t-navbar {
        background: white;
        border-radius: 0 0 20px 20px;
        padding: 14px 28px;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 4px 20px rgba(37,99,235,0.10);
        margin-bottom: 28px;
    }
    .t-navbar-brand { display: flex; align-items: center; gap: 12px; }
    .t-navbar-brand-name { font-size: 22px; font-weight: 800; color: #1a2a4a; }
    .t-navbar-brand-name span { color: #2563eb; }
    .t-navbar-brand-sub { font-size: 11px; color: #8896b3; font-weight: 500; }
    .t-navbar-user { display: flex; align-items: center; gap: 10px; }
    .t-navbar-user-avatar {
        width: 40px; height: 40px; border-radius: 50%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 16px; font-weight: 700;
    }
    .t-navbar-user-name { font-size: 15px; font-weight: 700; color: #1a2a4a; }
    .t-navbar-user-role { font-size: 12px; color: #8896b3; }
 
    /* WELCOME BANNER */
    .t-welcome-banner {
        background: linear-gradient(135deg, #1a4fd6 0%, #2563eb 60%, #1e40af 100%);
        border-radius: 20px; padding: 32px 36px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(37,99,235,0.35);
        position: relative; overflow: hidden;
    }
    .t-welcome-banner::before {
        content: ''; position: absolute; top: -40px; right: -40px;
        width: 200px; height: 200px;
        background: rgba(255,255,255,0.07); border-radius: 50%;
    }
    .t-welcome-banner::after {
        content: ''; position: absolute; bottom: -60px; right: 120px;
        width: 160px; height: 160px;
        background: rgba(255,255,255,0.05); border-radius: 50%;
    }
    .t-welcome-text h2 {
        color: white; font-size: 26px; font-weight: 800;
        margin: 0 0 6px 0; line-height: 1.2;
    }
    .t-welcome-text p { color: rgba(255,255,255,0.75); font-size: 15px; margin: 0; }
 
    /* CARD BUTTONS */
    div[data-testid="stHorizontalBlock"]:has(
        button[kind="secondary"][data-testid="baseButton-secondary"]
    ) > div .stButton > button {
        background: white !important;
        border: 2px solid #eef2ff !important;
        border-radius: 20px !important;
        width: 100% !important;
        height: 260px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0px !important;
        padding: 32px 28px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.07) !important;
        color: #1a2a4a !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        cursor: pointer !important;
        transition: all 0.25s ease !important;
        white-space: pre-wrap !important;
        line-height: 1.8 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        text-align: center !important;
    }
    div[data-testid="stHorizontalBlock"]:has(
        button[kind="secondary"][data-testid="baseButton-secondary"]
    ) > div .stButton > button:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 16px 40px rgba(37,99,235,0.22) !important;
        border-color: #2563eb !important;
        background: white !important;
        color: #1a2a4a !important;
    }
    div[data-testid="stHorizontalBlock"]:has(
        button[kind="secondary"][data-testid="baseButton-secondary"]
    ) > div .stButton > button:focus:not(:active) {
        box-shadow: 0 4px 20px rgba(0,0,0,0.07) !important;
        border-color: #eef2ff !important;
        outline: none !important;
    }
 
    /* FOOTER */
    .t-footer { text-align: center; margin-top: 2rem; padding-bottom: 2rem; }
    .t-footer-badge {
        display: inline-flex; align-items: center; gap: 10px;
        background: rgba(37,99,235,0.08); border: 1px solid rgba(37,99,235,0.15);
        border-radius: 50px; padding: 10px 24px;
        color: #2563eb; font-size: 14px; font-weight: 600;
    }
 
    div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
    </style>
    """, unsafe_allow_html=True)
 
 
def _render_navbar(teacher_name: str):
    initials = ''.join([w[0].upper() for w in teacher_name.split()[:2]])
    st.markdown(f"""
    <div class="t-navbar">
        <div class="t-navbar-brand">
            <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/app_logo.png"
                 style="width:44px;border-radius:10px;" onerror="this.style.display='none';">
            <div>
                <div class="t-navbar-brand-name">SmartAttend <span>AI</span></div>
                <div class="t-navbar-brand-sub">Smart Attendance System using Face Recognition</div>
            </div>
        </div>
        <div class="t-navbar-user">
            <div class="t-navbar-user-avatar">{initials}</div>
            <div>
                <div class="t-navbar-user-name">{teacher_name}</div>
                <div class="t-navbar-user-role">Teacher</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
 
def _render_welcome_banner(teacher_name: str):
    hour = datetime.now().hour
    greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")
    st.markdown(f"""
    <div class="t-welcome-banner">
        <div class="t-welcome-text">
            <h2>{greeting}, {teacher_name}! 👋</h2>
            <p>Here's a summary of your attendance activity today.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
 
def _render_home_cards():
    # ── tab button styles ──
    st.markdown("""
    <style>
    /* all 3 nav buttons default state */
    [data-testid="stHorizontalBlock"]:has([data-testid="baseButton-secondary"]) > div .stButton > button {
        background: white !important;
        border: 1.5px solid #d1d9f0 !important;
        border-radius: 12px !important;
        color: #6b7a99 !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        padding: 14px 10px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    [data-testid="stHorizontalBlock"]:has([data-testid="baseButton-secondary"]) > div .stButton > button:hover {
        border-color: #2563eb !important;
        color: #2563eb !important;
        background: #f0f4ff !important;
    }
    /* active / primary button = black */
    [data-testid="stHorizontalBlock"]:has([data-testid="baseButton-secondary"]) > div .stButton > button[kind="primary"],
    [data-testid="stHorizontalBlock"]:has([data-testid="baseButton-secondary"]) > div .stButton > button[data-testid="baseButton-primary"] {
        background: #1a2a4a !important;
        border-color: #1a2a4a !important;
        color: white !important;
        box-shadow: 0 4px 14px rgba(26,42,74,0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
 
    tab = st.session_state.get('current_teacher_tab', 'home')
    c1, c2, c3 = st.columns(3)
 
    with c1:
        btn_type = "primary" if tab == "take_attendance" else "secondary"
        if st.button("📷  Take Attendance", key="card_take_attendance",
                     use_container_width=True, type=btn_type):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()
 
    with c2:
        btn_type = "primary" if tab == "manage_subjects" else "secondary"
        if st.button("📖  Manage Subjects", key="card_manage_subjects",
                     use_container_width=True, type=btn_type):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()
 
    with c3:
        btn_type = "primary" if tab == "attendance_records" else "secondary"
        if st.button("📊  Attendance Records", key="card_attendance_records",
                     use_container_width=True, type=btn_type):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()
 
    st.divider()
 
    # ── render selected feature inline below buttons ──
    if tab == 'take_attendance':
        teacher_tab_take_attendance(show_back=False)
    elif tab == 'manage_subjects':
        teacher_tab_manage_subjects(show_back=False)
    elif tab == 'attendance_records':
        teacher_tab_attendance_records(show_back=False)
 
 
def _back_button():
    if st.button("← Back to Dashboard", key="back_btn", type='secondary',
                 icon=':material/arrow_back:'):
        st.session_state.current_teacher_tab = 'home'
        st.rerun()
 
 
def teacher_tab_take_attendance(show_back=True):
    teacher_id = st.session_state.teacher_data['teacher_id']
    if show_back:
        _back_button()
    st.header('Take AI Attendance')
 
    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []
 
    subjects = get_teacher_subjects(teacher_id)
    if not subjects:
        st.warning("You haven't created any subjects yet! Please create one to begin!")
        return
 
    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}
 
    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')
    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))
    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', use_container_width=True):
            add_photos_dialog()
 
    selected_subject_id = subject_options[selected_subject_label]
    st.divider()
 
    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, use_container_width=True, caption=f'Photo {idx + 1}')
 
    has_photos = bool(st.session_state.attendance_images)
    c1, c2 = st.columns(2)
 
    with c1:
        if st.button('Clear all photos', use_container_width=True, type='secondary',
                     icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()
 
    with c2:
        if st.button('Run Face Analysis', use_container_width=True, type='primary',
                     icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}
                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected = predict_attendance(img_np)
                    if detected:
                        for item in detected:
                           sid = item['student_id']
                           all_detected_ids.setdefault(int(sid), []).append(f"Photo {idx + 1}")
                enrolled_res = (
                    supabase.table('subject_students')
                    .select("*, students(*)")
                    .eq('subject_id', selected_subject_id)
                    .execute()
                )
                enrolled_students = enrolled_res.data
 
                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:
                    results, attendance_to_log = [], []
                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
 
                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0
                        results.append({
                            "Name":   student['name'],
                            "ID":     student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })
                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp':  current_timestamp,
                            'is_present': bool(is_present)
                        })
                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)
 
 
def teacher_tab_manage_subjects(show_back=True):
    teacher_id = st.session_state.teacher_data['teacher_id']
    if show_back:
        _back_button()
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects')
    with col2:
        if st.button('Create New Subject', use_container_width=True, type='primary'):
            create_subject_dialog(teacher_id)
 
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes",  sub['total_classes']),
            ]
            def share_btn(sub=sub):
                if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}",
                             icon=":material/share:"):
                    share_subject_dialog(sub['name'], sub['subject_code'])
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=share_btn,
            )
    else:
        st.info("No subjects found. Create one above.")
 
 
def teacher_tab_attendance_records(show_back=True):
    if show_back:
        _back_button()
    st.header('Attendance Records')
    teacher_id = st.session_state.teacher_data['teacher_id']
    records = get_attendance_for_teacher(teacher_id)
 
    if not records:
        st.info("No attendance records found yet.")
        return
 
    data = []
    for r in records:
        ts = r.get('timestamp')
        data.append({
            "ts_group":     ts.split(".")[0] if ts else None,
            "Time":         datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N/A",
            "Subject":      r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "is_present":   bool(r.get('is_present', False))
        })
 
    df = pd.DataFrame(data)
    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(Present_Count=('is_present', 'sum'), Total_Count=('is_present', 'count'))
        .reset_index()
    )
    summary['Attendance Stats'] = (
        "✅ " + summary['Present_Count'].astype(str)
        + " / " + summary['Total_Count'].astype(str) + ' Students'
    )
    display_df = (
        summary.sort_values(by='ts_group', ascending=False)
        [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
    )
    st.dataframe(display_df, use_container_width=True, hide_index=True)
 
 
def login_teacher(username, password):
    if not username or not password:
        return False
    teacher = teacher_login(username, password)
    if teacher:
        st.session_state.user_role    = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    return False
 
 
def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Passwords don't match"
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Successfully created! Login now."
    except Exception:
        return False, "Unexpected error!"
 
 
def teacher_dashboard_screen():
    _inject_styles()
 
    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab = 'home'
 
    teacher_data = st.session_state.get('teacher_data') or st.session_state.get('teacher', {})
    teacher_name = teacher_data.get('name', 'Teacher') if teacher_data else 'Teacher'
 
    # guard — if no valid teacher data, go back to home
    if not teacher_data or not teacher_data.get('teacher_id'):
        st.session_state['login_type'] = None
        st.rerun()
        return
 
    if 'teacher_data' not in st.session_state and teacher_data:
        st.session_state.teacher_data = teacher_data
 
    _render_navbar(teacher_name)
    _render_welcome_banner(teacher_name)
 
    # Logout button
    _, logout_col = st.columns([8, 2])
    with logout_col:
        if st.button("⏻  Logout", type='secondary', use_container_width=True):
            for key in ['teacher_data', 'teacher', 'attendance_images',
                        'is_logged_in', 'user_role', 'current_teacher_tab']:
                st.session_state.pop(key, None)
            st.session_state['login_type'] = None
            st.rerun()
 
    st.divider()
 
    # Always show the 3 nav buttons; selected one highlights dark and content renders below
    _render_home_cards()
 
    st.markdown("""
    <div class="t-footer">
        <div class="t-footer-badge">🛡️ &nbsp; Powered by AI Face Recognition</div>
    </div>
    """, unsafe_allow_html=True)