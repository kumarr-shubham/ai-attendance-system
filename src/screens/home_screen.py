import streamlit as st
from src.components.header import header_home
from src.ui.base_layout import style_base_layout, style_background_home

def home_screen():

    style_background_home()
    style_base_layout()

    # Check if a portal was selected via query param
    params = st.query_params
    if "portal" in params:
        st.session_state['login_type'] = params["portal"]
        st.query_params.clear()
        st.rerun()

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a4fd6 0%, #2563eb 50%, #1e40af 100%) !important;
    }
    [data-testid="stMain"] { background: transparent !important; }
    #MainMenu, footer, header { visibility: hidden; }

    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 700px !important;
    }

    .portal-card {
        background: white;
        border-radius: 20px;
        padding: 36px 28px 32px 28px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    .icon-circle {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: #e8edf8;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px auto;
        overflow: hidden;
    }

    .icon-circle img {
        width: 58px;
        height: 58px;
        object-fit: contain;
    }

    .portal-title {
        font-size: 22px;
        font-weight: 700;
        color: #1a2a4a;
        margin: 0 0 10px 0;
        font-family: 'Segoe UI', sans-serif;
    }

    .portal-desc {
        font-size: 15px;
        color: #6b7a99;
        margin: 0 0 24px 0;
        line-height: 1.6;
    }

    .portal-btn {
        display: block;
        width: 100%;
        padding: 13px 0;
        background: linear-gradient(90deg, #1d4ed8, #2563eb);
        color: white !important;
        border-radius: 10px;
        text-decoration: none !important;
        font-size: 16px;
        font-weight: 600;
        text-align: center;
        cursor: pointer;
        border: none;
        letter-spacing: 0.02em;
    }

    .portal-btn:hover {
        opacity: 0.9;
    }

    .sa-footer {
        text-align: center;
        margin-top: 2.5rem;
    }

    .sa-footer-badge {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 50px;
        padding: 12px 28px;
        color: white;
        font-size: 15px;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)

   # ---- LOGO ----
    st.markdown("""
        <div style="text-align:center; margin-top:10px; margin-bottom:5px;">
            <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/app_logo.png"
                 style="width:100px; border-radius:22px;"
                 onerror="this.style.display='none';">
        </div>
    """, unsafe_allow_html=True)

    # ---- HEADER ----
    header_home()

    # ---- PORTAL CARDS ----
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="portal-card">
            <div class="icon-circle">
                <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/assets/student_icon.png"
                     style="width:150px; height:150px; object-fit:contain;"
                     onerror="this.src='https://cdn-icons-png.flaticon.com/512/4140/4140048.png';">
            </div>
            <p class="portal-title">Student Portal</p>
            <p class="portal-desc">Mark your attendance<br>and view your records.</p>
            <a href="?portal=student" class="portal-btn">Enter Portal &nbsp;→</a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="portal-card">
            <div class="icon-circle">
                <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/assets/teacher_icon.png"
                     style="width:150px; height:150px; object-fit:contain;"
                     onerror="this.src='https://cdn-icons-png.flaticon.com/512/4140/4140051.png';">
            </div>
            <p class="portal-title">Teacher Portal</p>
            <p class="portal-desc">Take attendance<br>and manage records.</p>
            <a href="?portal=teacher" class="portal-btn">Enter Portal &nbsp;→</a>
        </div>
        """, unsafe_allow_html=True)

    # ---- FOOTER ----
    st.markdown("""
    <div class="sa-footer">
        <div class="sa-footer-badge">
            🛡️ &nbsp; Powered by AI Face Recognition
        </div>
    </div>
    """, unsafe_allow_html=True)