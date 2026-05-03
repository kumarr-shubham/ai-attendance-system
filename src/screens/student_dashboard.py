import streamlit as st
from src.database.db import get_student_subjects, get_student_attendance, unenroll_student_to_subject
from src.components.subject_card import subject_card
from src.components.dialog_enroll import enroll_dialog


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
            <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/app_logo.png"
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
 
    # guard — if no valid student data, go back to home
    if not student_data or not student_data.get('student_id'):
        st.session_state['login_type'] = None
        st.rerun()
        return
 
    student_id   = student_data['student_id']
    student_name = student_data.get('name', 'Student')
 
    # ── shared UI ──
    _render_navbar(student_name)
    _render_welcome_banner(student_name)
 
    # ── logout ──
    _, logout_col = st.columns([8, 2])
    with logout_col:
        if st.button("⏻  Logout", type='secondary', use_container_width=True):
            for key in ['student_data', 'student', 'is_logged_in', 'user_role']:
                st.session_state.pop(key, None)
            st.session_state['login_type'] = None
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
                    type='secondary',
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