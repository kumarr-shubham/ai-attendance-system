import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

from src.ui.base_layout import style_base_layout, style_background_home
from src.database.teacher_auth import teacher_login, check_teacher_exists, create_teacher
from src.database.subjects import get_teacher_subjects
from src.database.attendance import get_attendance_for_teacher
from src.ml.face_recognition import predict_attendance
from src.database.supabase_client import supabase
from src.ui.dialogs import (
    add_photos_dialog,
    attendance_result_dialog,
    voice_attendance_dialog,
    create_subject_dialog,
    share_subject_dialog,
)
from src.ui.components import subject_card


# ──────────────────────────────────────────────
#  SHARED CSS
# ──────────────────────────────────────────────
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

    /* ── NAVBAR ── */
    .navbar {
        background: white;
        border-radius: 0 0 20px 20px;
        padding: 14px 28px;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 4px 20px rgba(37,99,235,0.10);
        margin-bottom: 28px;
    }
    .navbar-brand { display: flex; align-items: center; gap: 12px; }
    .navbar-brand-name { font-size: 22px; font-weight: 800; color: #1a2a4a; }
    .navbar-brand-name span { color: #2563eb; }
    .navbar-brand-sub { font-size: 11px; color: #8896b3; font-weight: 500; letter-spacing: 0.3px; }
    .navbar-user { display: flex; align-items: center; gap: 10px; }
    .navbar-user-avatar {
        width: 40px; height: 40px; border-radius: 50%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 16px; font-weight: 700;
    }
    .navbar-user-name { font-size: 15px; font-weight: 700; color: #1a2a4a; }
    .navbar-user-role { font-size: 12px; color: #8896b3; }
    .logout-btn {
        display: inline-flex; align-items: center; gap: 6px;
        background: #fef2f2; color: #dc2626 !important;
        border: 1.5px solid #fecaca; border-radius: 50px; padding: 8px 18px;
        font-size: 13px; font-weight: 600; text-decoration: none !important;
    }
    .logout-btn:hover { background: #fee2e2; }

    /* ── WELCOME BANNER ── */
    .welcome-banner {
        background: linear-gradient(135deg, #1a4fd6 0%, #2563eb 60%, #1e40af 100%);
        border-radius: 20px; padding: 32px 36px;
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(37,99,235,0.35);
        position: relative; overflow: hidden;
    }
    .welcome-banner::before {
        content: ''; position: absolute; top: -40px; right: -40px;
        width: 200px; height: 200px;
        background: rgba(255,255,255,0.07); border-radius: 50%;
    }
    .welcome-banner::after {
        content: ''; position: absolute; bottom: -60px; right: 120px;
        width: 160px; height: 160px;
        background: rgba(255,255,255,0.05); border-radius: 50%;
    }
    .welcome-text h2 {
        color: white; font-size: 26px; font-weight: 800;
        margin: 0 0 6px 0; line-height: 1.2;
    }
    .welcome-text p { color: rgba(255,255,255,0.75); font-size: 15px; margin: 0; }

    /* ── ACTION CARDS (home tab) ── */
    .actions-grid {
        display: grid; grid-template-columns: repeat(3, 1fr);
        gap: 20px; margin-bottom: 28px;
    }
    .action-card {
        background: white; border-radius: 20px; padding: 28px 24px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        text-align: center; text-decoration: none !important; display: block;
        transition: transform 0.25s, box-shadow 0.25s;
        border: 2px solid transparent; cursor: pointer;
    }
    .action-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(37,99,235,0.18);
        border-color: #2563eb; text-decoration: none !important;
    }
    .action-card-icon {
        width: 72px; height: 72px; border-radius: 20px;
        background: linear-gradient(135deg, #1a4fd6, #2563eb);
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; margin: 0 auto 16px auto;
        box-shadow: 0 6px 18px rgba(37,99,235,0.35);
    }
    .action-card h3 { color: #1a2a4a; font-size: 17px; font-weight: 700; margin: 0 0 8px 0; }
    .action-card p { color: #8896b3; font-size: 13px; margin: 0; line-height: 1.5; }
    .action-card-arrow {
        display: inline-flex; align-items: center; gap: 6px;
        background: #eff6ff; color: #2563eb;
        border-radius: 50px; padding: 6px 14px;
        font-size: 13px; font-weight: 600; margin-top: 14px;
    }

    /* ── TAB NAV ── */
    .tab-nav {
        display: flex; gap: 6px; margin-bottom: 24px;
        background: white; border-radius: 14px; padding: 6px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    }
    .tab-btn {
        flex: 1; text-align: center; padding: 10px 14px;
        border-radius: 10px; font-size: 14px; font-weight: 600;
        cursor: pointer; text-decoration: none !important;
        color: #6b7a99 !important; transition: all 0.2s;
    }
    .tab-btn:hover { background: #f0f4ff; color: #2563eb !important; text-decoration: none !important; }
    .tab-btn.active {
        background: linear-gradient(135deg, #1a4fd6, #2563eb) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
        text-decoration: none !important;
    }

    /* ── FOOTER ── */
    .sa-footer { text-align: center; margin-top: 2rem; padding-bottom: 2rem; }
    .sa-footer-badge {
        display: inline-flex; align-items: center; gap: 10px;
        background: rgba(37,99,235,0.08); border: 1px solid rgba(37,99,235,0.15);
        border-radius: 50px; padding: 10px 24px;
        color: #2563eb; font-size: 14px; font-weight: 600;
    }

    div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
    </style>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  NAVBAR
# ──────────────────────────────────────────────
def _render_navbar(teacher_name: str):
    initials = ''.join([w[0].upper() for w in teacher_name.split()[:2]])
    st.markdown(f"""
    <div class="navbar">
        <div class="navbar-brand">
            <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/assets/app_logo.png"
                 style="width:44px;border-radius:10px;" onerror="this.style.display='none';">
            <div>
                <div class="navbar-brand-name">SmartAttend <span>AI</span></div>
                <div class="navbar-brand-sub">Smart Attendance System using Face Recognition</div>
            </div>
        </div>
        <div class="navbar-user">
            <div class="navbar-user-avatar">{initials}</div>
            <div>
                <div class="navbar-user-name">{teacher_name}</div>
                <div class="navbar-user-role">Teacher</div>
            </div>
            <a href="?portal=logout" class="logout-btn">⏻ Logout</a>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  WELCOME BANNER
# ──────────────────────────────────────────────
def _render_welcome_banner(teacher_name: str):
    hour = datetime.now().hour
    greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")
    st.markdown(f"""
    <div class="welcome-banner">
        <div class="welcome-text">
            <h2>{greeting}, {teacher_name}! 👋</h2>
            <p>Here's a summary of your attendance activity today.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  TAB NAV
# ──────────────────────────────────────────────
def _render_tab_nav(active_tab: str):
    tabs = [
        ("🏠", "Home",               "home"),
        ("📷", "Take Attendance",    "take_attendance"),
        ("📖", "Manage Subjects",    "manage_subjects"),
        ("📊", "Attendance Records", "attendance_records"),
    ]
    items = ""
    for icon, label, key in tabs:
        cls = "tab-btn active" if active_tab == key else "tab-btn"
        items += f'<a href="?tab={key}" class="{cls}">{icon} {label}</a>'
    st.markdown(f'<div class="tab-nav">{items}</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  HOME TAB
# ──────────────────────────────────────────────
def _render_home_tab():
    st.markdown("""
    <div class="actions-grid">
        <a href="?tab=take_attendance" class="action-card">
            <div class="action-card-icon">📷</div>
            <h3>Take Attendance</h3>
            <p>Use AI face recognition to mark student attendance instantly.</p>
            <div class="action-card-arrow">Start Session →</div>
        </a>
        <a href="?tab=manage_subjects" class="action-card">
            <div class="action-card-icon">📖</div>
            <h3>Manage Subjects</h3>
            <p>Add, edit or remove subjects and enroll students.</p>
            <div class="action-card-arrow">Manage →</div>
        </a>
        <a href="?tab=attendance_records" class="action-card">
            <div class="action-card-icon">📊</div>
            <h3>Attendance Records</h3>
            <p>View detailed logs, export reports and track trends.</p>
            <div class="action-card-arrow">View Records →</div>
        </a>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  TAKE ATTENDANCE TAB
# ──────────────────────────────────────────────
def _render_take_attendance_tab(teacher_id):
    st.header("📷 Take AI Attendance")

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
        st.subheader("Added Photos")
        gallery_cols = st.columns(4)
        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, use_container_width=True, caption=f'Photo {idx + 1}')

    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', use_container_width=True, type='tertiary',
                     icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:
        if st.button('Run Face Analysis', use_container_width=True, type='secondary',
                     icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}
                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)
                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx + 1}")

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
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })
                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', use_container_width=True, icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)


# ──────────────────────────────────────────────
#  MANAGE SUBJECTS TAB
# ──────────────────────────────────────────────
def _render_manage_subjects_tab(teacher_id):
    col1, col2 = st.columns(2)
    with col1:
        st.header("📖 Manage Subjects")
    with col2:
        if st.button('➕ Create New Subject', use_container_width=True, type='primary'):
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


# ──────────────────────────────────────────────
#  ATTENDANCE RECORDS TAB
# ──────────────────────────────────────────────
def _render_attendance_records_tab(teacher_id):
    st.header("📊 Attendance Records")

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


# ──────────────────────────────────────────────
#  MAIN ENTRY POINT
# ──────────────────────────────────────────────
def teacher_dashboard_screen():
    style_background_home()
    style_base_layout()
    _inject_styles()

    # handle logout
    if st.query_params.get("portal") == "logout":
        st.session_state['login_type'] = None
        st.session_state.pop('teacher', None)
        st.query_params.clear()
        st.rerun()

    # resolve active tab
    tab = st.query_params.get("tab", "home")
    if tab not in ("home", "take_attendance", "manage_subjects", "attendance_records"):
        tab = "home"

    # teacher info
    teacher      = st.session_state.get('teacher', {})
    teacher_name = teacher.get('name', 'Teacher') if teacher else 'Teacher'
    teacher_id   = teacher.get('teacher_id')       if teacher else None

    # shared UI
    _render_navbar(teacher_name)
    _render_welcome_banner(teacher_name)
    _render_tab_nav(tab)

    # active tab content
    if tab == "home":
        _render_home_tab()
    elif tab == "take_attendance":
        _render_take_attendance_tab(teacher_id) if teacher_id else st.error("Please log in again.")
    elif tab == "manage_subjects":
        _render_manage_subjects_tab(teacher_id) if teacher_id else st.error("Please log in again.")
    elif tab == "attendance_records":
        _render_attendance_records_tab(teacher_id) if teacher_id else st.error("Please log in again.")

    # footer
    st.markdown("""
    <div class="sa-footer">
        <div class="sa-footer-badge">🛡️ &nbsp; Powered by AI Face Recognition</div>
    </div>
    """, unsafe_allow_html=True)






    import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

from src.database.db import get_teacher_subjects, get_attendance_for_teacher
from src.database.config import supabase
from src.pipelines.face_pipeline import predict_attendance
from src.ui.components.subject_card import subject_card
from src.ui.components.dialog_add_photo import add_photos_dialog
from src.ui.components.dialog_attendance_results import attendance_result_dialog
from src.ui.components.dialog_create_subject import create_subject_dialog
from src.ui.components.dialog_share_subject import share_subject_dialog
from src.database.teacher_auth import teacher_login, check_teacher_exists, create_teacher


# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
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

    /* ── NAVBAR ── */
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
    .t-navbar-brand-sub { font-size: 11px; color: #8896b3; font-weight: 500; letter-spacing: 0.3px; }
    .t-navbar-user { display: flex; align-items: center; gap: 10px; }
    .t-navbar-user-avatar {
        width: 40px; height: 40px; border-radius: 50%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 16px; font-weight: 700;
    }
    .t-navbar-user-name { font-size: 15px; font-weight: 700; color: #1a2a4a; }
    .t-navbar-user-role { font-size: 12px; color: #8896b3; }

    /* ── WELCOME BANNER ── */
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

    /* ── HOME ACTION CARDS ── */
    .t-actions-grid {
        display: grid; grid-template-columns: repeat(3, 1fr);
        gap: 20px; margin-bottom: 28px;
    }
    .t-action-card {
        background: white; border-radius: 20px; padding: 28px 24px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        text-align: center;
        border: 2px solid transparent;
    }
    .t-action-card-icon {
        width: 72px; height: 72px; border-radius: 20px;
        background: linear-gradient(135deg, #1a4fd6, #2563eb);
        display: flex; align-items: center; justify-content: center;
        font-size: 32px; margin: 0 auto 16px auto;
        box-shadow: 0 6px 18px rgba(37,99,235,0.35);
    }
    .t-action-card h3 { color: #1a2a4a; font-size: 17px; font-weight: 700; margin: 0 0 8px 0; }
    .t-action-card p  { color: #8896b3; font-size: 13px; margin: 0; line-height: 1.5; }

    /* ── FOOTER ── */
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


# ─────────────────────────────────────────────
#  NAVBAR
# ─────────────────────────────────────────────
def _render_navbar(teacher_name: str):
    initials = ''.join([w[0].upper() for w in teacher_name.split()[:2]])
    st.markdown(f"""
    <div class="t-navbar">
        <div class="t-navbar-brand">
            <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/assets/app_logo.png"
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


# ─────────────────────────────────────────────
#  WELCOME BANNER
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  TAB BUTTONS  (session_state driven)
# ─────────────────────────────────────────────
def _render_tab_buttons():
    tabs = [
        ("🏠", "Home",               "home"),
        ("📷", "Take Attendance",    "take_attendance"),
        ("📖", "Manage Subjects",    "manage_subjects"),
        ("📊", "Attendance Records", "attendance_records"),
    ]
    active = st.session_state.get("current_teacher_tab", "home")
    cols = st.columns(len(tabs))
    for col, (icon, label, key) in zip(cols, tabs):
        with col:
            btn_type = "primary" if active == key else "secondary"
            if st.button(f"{icon}  {label}", key=f"tab_btn_{key}",
                         type=btn_type, use_container_width=True):
                st.session_state.current_teacher_tab = key
                st.rerun()
    st.divider()


# ─────────────────────────────────────────────
#  HOME TAB
# ─────────────────────────────────────────────
def _render_home_tab():
    st.markdown("""
    <div class="t-actions-grid">
        <div class="t-action-card">
            <div class="t-action-card-icon">📷</div>
            <h3>Take Attendance</h3>
            <p>Use AI face recognition to mark student attendance instantly.</p>
        </div>
        <div class="t-action-card">
            <div class="t-action-card-icon">📖</div>
            <h3>Manage Subjects</h3>
            <p>Add, edit or remove subjects and enroll students.</p>
        </div>
        <div class="t-action-card">
            <div class="t-action-card-icon">📊</div>
            <h3>Attendance Records</h3>
            <p>View detailed logs, export reports and track trends.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("👆 Use the tabs above to navigate between features.")


# ─────────────────────────────────────────────
#  TAKE ATTENDANCE TAB
# ─────────────────────────────────────────────
def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
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
        if st.button('Clear all photos', use_container_width=True, type='tertiary',
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
                    detected, _, _ = predict_attendance(img_np)
                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)
                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx + 1}")

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


# ─────────────────────────────────────────────
#  MANAGE SUBJECTS TAB
# ─────────────────────────────────────────────
def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']

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


# ─────────────────────────────────────────────
#  ATTENDANCE RECORDS TAB
# ─────────────────────────────────────────────
def teacher_tab_attendance_records():
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


# ─────────────────────────────────────────────
#  LOGIN HELPERS  (used by teacher_screen.py)
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────
def teacher_dashboard_screen():
    _inject_styles()

    # init tab state
    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab = 'home'

    # support both session key names used across the codebase
    teacher_data = st.session_state.get('teacher_data') or st.session_state.get('teacher', {})
    teacher_name = teacher_data.get('name', 'Teacher') if teacher_data else 'Teacher'

    # ensure teacher_data key is always set (some screens use this key)
    if 'teacher_data' not in st.session_state and teacher_data:
        st.session_state.teacher_data = teacher_data

    # ── shared UI ──
    _render_navbar(teacher_name)
    _render_welcome_banner(teacher_name)

    # ── logout ──
    _, logout_col = st.columns([8, 2])
    with logout_col:
        if st.button("⏻  Logout", type='secondary', use_container_width=True,
                     shortcut="ctrl+backspace"):
            st.session_state.is_logged_in = False
            st.session_state.current_teacher_tab = 'home'
            for key in ['teacher_data', 'teacher', 'attendance_images']:
                st.session_state.pop(key, None)
            st.rerun()

    # ── tab nav ──
    _render_tab_buttons()

    # ── active tab content ──
    tab = st.session_state.current_teacher_tab
    if tab == 'home':
        _render_home_tab()
    elif tab == 'take_attendance':
        teacher_tab_take_attendance()
    elif tab == 'manage_subjects':
        teacher_tab_manage_subjects()
    elif tab == 'attendance_records':
        teacher_tab_attendance_records()

    # ── footer ──
    st.markdown("""
    <div class="t-footer">
        <div class="t-footer-badge">🛡️ &nbsp; Powered by AI Face Recognition</div>
    </div>
    """, unsafe_allow_html=True)




    import streamlit as st
from src.database.db import get_student_subjects, get_student_attendance, unenroll_student_to_subject
from src.ui.components.subject_card import subject_card
from src.ui.components.dialog_enroll import enroll_dialog


# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
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

    /* ── NAVBAR ── */
    .s-navbar {
        background: white;
        border-radius: 0 0 20px 20px;
        padding: 14px 28px;
        display: flex; align-items: center; justify-content: space-between;
        box-shadow: 0 4px 20px rgba(37,99,235,0.10);
        margin-bottom: 28px;
    }
    .s-navbar-brand { display: flex; align-items: center; gap: 12px; }
    .s-navbar-brand-name { font-size: 22px; font-weight: 800; color: #1a2a4a; }
    .s-navbar-brand-name span { color: #2563eb; }
    .s-navbar-brand-sub { font-size: 11px; color: #8896b3; font-weight: 500; letter-spacing: 0.3px; }
    .s-navbar-user { display: flex; align-items: center; gap: 10px; }
    .s-navbar-user-avatar {
        width: 40px; height: 40px; border-radius: 50%;
        background: linear-gradient(135deg, #7c3aed, #6d28d9);
        display: flex; align-items: center; justify-content: center;
        color: white; font-size: 16px; font-weight: 700;
    }
    .s-navbar-user-name { font-size: 15px; font-weight: 700; color: #1a2a4a; }
    .s-navbar-user-role { font-size: 12px; color: #8896b3; }

    /* ── WELCOME BANNER ── */
    .s-welcome-banner {
        background: linear-gradient(135deg, #5b21b6 0%, #7c3aed 60%, #4c1d95 100%);
        border-radius: 20px; padding: 32px 36px;
        margin-bottom: 24px;
        box-shadow: 0 8px 30px rgba(109,40,217,0.35);
        position: relative; overflow: hidden;
    }
    .s-welcome-banner::before {
        content: ''; position: absolute; top: -40px; right: -40px;
        width: 200px; height: 200px;
        background: rgba(255,255,255,0.07); border-radius: 50%;
    }
    .s-welcome-banner::after {
        content: ''; position: absolute; bottom: -60px; right: 120px;
        width: 160px; height: 160px;
        background: rgba(255,255,255,0.05); border-radius: 50%;
    }
    .s-welcome-text h2 {
        color: white; font-size: 26px; font-weight: 800;
        margin: 0 0 6px 0; line-height: 1.2;
    }
    .s-welcome-text p { color: rgba(255,255,255,0.75); font-size: 15px; margin: 0; }

    /* ── STATS ROW ── */
    .s-stats-row {
        display: grid; grid-template-columns: repeat(3, 1fr);
        gap: 16px; margin-bottom: 24px;
    }
    .s-stat-card {
        background: white; border-radius: 16px; padding: 18px 20px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
        display: flex; align-items: center; gap: 14px;
    }
    .s-stat-icon {
        width: 48px; height: 48px; border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px; flex-shrink: 0;
    }
    .s-stat-icon.purple { background: #f5f3ff; }
    .s-stat-icon.green  { background: #f0fdf4; }
    .s-stat-icon.blue   { background: #eff6ff; }
    .s-stat-num  { font-size: 24px; font-weight: 800; color: #1a2a4a; line-height: 1; }
    .s-stat-label{ font-size: 12px; color: #8896b3; margin-top: 3px; }

    /* ── SECTION HEADER ── */
    .s-section-header {
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 16px;
    }
    .s-section-title { font-size: 20px; font-weight: 800; color: #1a2a4a; margin: 0; }

    /* ── EMPTY STATE ── */
    .s-empty {
        background: white; border-radius: 20px; padding: 48px 24px;
        text-align: center; box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }
    .s-empty-icon { font-size: 48px; margin-bottom: 12px; }
    .s-empty h3 { color: #1a2a4a; font-size: 18px; font-weight: 700; margin: 0 0 6px 0; }
    .s-empty p  { color: #8896b3; font-size: 14px; margin: 0; }

    /* ── FOOTER ── */
    .s-footer { text-align: center; margin-top: 2rem; padding-bottom: 2rem; }
    .s-footer-badge {
        display: inline-flex; align-items: center; gap: 10px;
        background: rgba(109,40,217,0.08); border: 1px solid rgba(109,40,217,0.15);
        border-radius: 50px; padding: 10px 24px;
        color: #7c3aed; font-size: 14px; font-weight: 600;
    }

    div[data-testid="stHorizontalBlock"] { gap: 0 !important; }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  NAVBAR
# ─────────────────────────────────────────────
def _render_navbar(student_name: str):
    initials = ''.join([w[0].upper() for w in student_name.split()[:2]])
    st.markdown(f"""
    <div class="s-navbar">
        <div class="s-navbar-brand">
            <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/assets/app_logo.png"
                 style="width:44px;border-radius:10px;" onerror="this.style.display='none';">
            <div>
                <div class="s-navbar-brand-name">SmartAttend <span>AI</span></div>
                <div class="s-navbar-brand-sub">Smart Attendance System using Face Recognition</div>
            </div>
        </div>
        <div class="s-navbar-user">
            <div class="s-navbar-user-avatar">{initials}</div>
            <div>
                <div class="s-navbar-user-name">{student_name}</div>
                <div class="s-navbar-user-role">Student</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  WELCOME BANNER
# ─────────────────────────────────────────────
def _render_welcome_banner(student_name: str):
    from datetime import datetime
    hour = datetime.now().hour
    greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")
    st.markdown(f"""
    <div class="s-welcome-banner">
        <div class="s-welcome-text">
            <h2>{greeting}, {student_name}! 🎓</h2>
            <p>Track your attendance and enrolled subjects below.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  STATS ROW
# ─────────────────────────────────────────────
def _render_stats(subjects, stats_map):
    total_subjects = len(subjects)

    total_classes  = sum(v['total']    for v in stats_map.values()) if stats_map else 0
    total_attended = sum(v['attended'] for v in stats_map.values()) if stats_map else 0

    pct = round((total_attended / total_classes) * 100) if total_classes > 0 else 0

    st.markdown(f"""
    <div class="s-stats-row">
        <div class="s-stat-card">
            <div class="s-stat-icon purple">📚</div>
            <div>
                <div class="s-stat-num">{total_subjects}</div>
                <div class="s-stat-label">Enrolled Subjects</div>
            </div>
        </div>
        <div class="s-stat-card">
            <div class="s-stat-icon green">✅</div>
            <div>
                <div class="s-stat-num">{total_attended}</div>
                <div class="s-stat-label">Classes Attended</div>
            </div>
        </div>
        <div class="s-stat-card">
            <div class="s-stat-icon blue">📊</div>
            <div>
                <div class="s-stat-num">{pct}%</div>
                <div class="s-stat-label">Overall Attendance</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────
def student_dashboard():
    _inject_styles()

    # support both session key names
    student_data = st.session_state.get('student_data') or st.session_state.get('student', {})
    student_id   = student_data['student_id']
    student_name = student_data.get('name', 'Student')

    # ── shared UI ──
    _render_navbar(student_name)
    _render_welcome_banner(student_name)

    # ── logout ──
    _, logout_col = st.columns([8, 2])
    with logout_col:
        if st.button("⏻  Logout", type='secondary', use_container_width=True,
                     shortcut="ctrl+backspace"):
            st.session_state['is_logged_in'] = False
            for key in ['student_data', 'student']:
                st.session_state.pop(key, None)
            st.rerun()

    st.divider()

    # ── fetch data ──
    with st.spinner('Loading your subjects...'):
        subjects = get_student_subjects(student_id)
        logs     = get_student_attendance(student_id)

    # ── build stats map ──
    stats_map = {}
    for log in logs:
        sid = log['subject_id']
        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}
        stats_map[sid]['total'] += 1
        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    # ── stats row ──
    _render_stats(subjects, stats_map)

    # ── section header ──
    h_col, btn_col = st.columns([6, 2])
    with h_col:
        st.markdown('<div class="s-section-title">📖 Your Enrolled Subjects</div>',
                    unsafe_allow_html=True)
    with btn_col:
        if st.button('➕  Enroll in Subject', type='primary', use_container_width=True):
            enroll_dialog()

    st.divider()

    # ── subjects grid ──
    if not subjects:
        st.markdown("""
        <div class="s-empty">
            <div class="s-empty-icon">📭</div>
            <h3>No subjects yet</h3>
            <p>Use the "Enroll in Subject" button above to join a class.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, sub_node in enumerate(subjects):
            sub = sub_node['subjects']
            sid = sub['subject_id']
            s   = stats_map.get(sid, {"total": 0, "attended": 0})

            # attendance percentage pill
            pct = round((s['attended'] / s['total']) * 100) if s['total'] > 0 else 0

            def unenroll_button(sub=sub, sid=sid):
                if st.button(
                    "Unenroll from this course",
                    key=f"unenroll_{sid}",
                    type='tertiary',
                    use_container_width=True,
                    icon=':material/delete_forever:'
                ):
                    unenroll_student_to_subject(student_id, sid)
                    st.toast(f"Unenrolled from {sub['name']} successfully!")
                    st.rerun()

            with cols[i % 2]:
                subject_card(
                    name=sub['name'],
                    code=sub['subject_code'],
                    section=sub['section'],
                    stats=[
                        ('📅', 'Total Classes', s['total']),
                        ('✅', 'Attended',       s['attended']),
                        ('📊', 'Attendance',     f"{pct}%"),
                    ],
                    footer_callback=unenroll_button,
                )

    # ── footer ──
    st.markdown("""
    <div class="s-footer">
        <div class="s-footer-badge">🛡️ &nbsp; Powered by AI Face Recognition</div>
    </div>
    """, unsafe_allow_html=True) 