import streamlit as st
from src.ui.base_layout import style_base_layout, style_background_home
from src.database.teacher_auth import teacher_login

def teacher_login_screen():

    style_background_home()
    style_base_layout()

    if "portal" in st.query_params:
        val = st.query_params["portal"]
        if val == "home":
            st.session_state['login_type'] = None
            st.query_params.clear()
            st.rerun()
        elif val == "teacher":
            st.session_state['login_type'] = 'teacher'
            st.query_params.clear()
            st.rerun()

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a4fd6 0%, #2563eb 50%, #1e40af 100%) !important;
    }
    [data-testid="stMain"] { background: transparent !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem !important; max-width: 1000px !important; }

    .back-btn {
        display: inline-flex; align-items: center; gap: 8px;
        color: white !important; font-size: 15px; font-weight: 500;
        text-decoration: none !important;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 50px; padding: 8px 18px;
    }

    .page-title { text-align: center; margin: 20px 0 24px 0; }
    .page-title h1 {
        color: white !important; font-size: 36px !important;
        font-weight: 800 !important; margin: 0 0 6px 0 !important;
        line-height: 1.2 !important;
    }
    .page-title p { color: rgba(255,255,255,0.75); font-size: 16px; margin: 0; }

    div[data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        background: white !important;
        border-radius: 20px !important;
        overflow: hidden !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.2) !important;
    }

    div[data-testid="stHorizontalBlock"] > div:first-child {
        background: #eef1fb !important;
        border-radius: 20px 0 0 20px !important;
    }

    div[data-testid="stHorizontalBlock"] > div:last-child {
        background: white !important;
        border-radius: 0 20px 20px 0 !important;
        padding: 36px 36px 28px 36px !important;
    }

    div[data-testid="stHorizontalBlock"] > div > div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stHorizontalBlock"] > div > div[data-testid="stVerticalBlockBorderWrapper"] > div,
    div[data-testid="stHorizontalBlock"] > div > div[data-testid="stVerticalBlockBorderWrapper"] > div > div {
        padding: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    .avatar-circle {
        width: 160px; height: 160px; border-radius: 50%;
        background: #d4daf5;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 24px auto; overflow: hidden;
    }
    .avatar-circle img { width: 130px; }

    .info-box {
        background: white; border-radius: 14px;
        padding: 16px 18px;
        display: flex; align-items: flex-start; gap: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .info-box h4 { color: #1a2a4a; font-size: 15px; font-weight: 700; margin: 0 0 4px 0; }
    .info-box p { color: #6b7a99; font-size: 13px; margin: 0; line-height: 1.5; }

    .form-label {
        font-size: 14px; font-weight: 600;
        color: #1a2a4a; margin: 0 0 4px 0; display: block;
    }

    div[data-testid="stTextInput"] > div {
        border: none !important; box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input {
        border: 1.5px solid #e0e4ef !important;
        border-radius: 10px !important;
        font-size: 15px !important;
        color: #1a2a4a !important;
        background: white !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #2563eb !important;
        box-shadow: none !important;
    }

    .stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #1d4ed8, #2563eb) !important;
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
    }

    .bottom-link { text-align: center; margin-top: 12px; font-size: 14px; color: #6b7a99; }
    .bottom-link a { color: #2563eb; font-weight: 600; text-decoration: none; }

    .sa-footer { text-align: center; margin-top: 2rem; }
    .sa-footer-badge {
        display: inline-flex; align-items: center; gap: 10px;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 50px; padding: 12px 28px;
        color: white; font-size: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---- TOP NAV ----
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
        <a href="?portal=home" class="back-btn">← Back to Home</a>
        <div style="display:flex;align-items:center;gap:12px;">
            <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/app_logo.png"
                 style="width:52px;border-radius:12px;" onerror="this.style.display='none';">
            <div>
                <div style="color:white;font-size:22px;font-weight:800;">SmartAttend <span style="color:#7dd3fc;">AI</span></div>
                <div style="color:rgba(255,255,255,0.7);font-size:12px;">Smart Attendance System using Face Recognition</div>
            </div>
        </div>
        <div style="width:140px;"></div>
    </div>
    """, unsafe_allow_html=True)

    # ---- PAGE TITLE ----
    st.markdown("""
    <div class="page-title">
        <h1>Login using Password</h1>
        <p>Login to your teacher account</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- COLUMNS ----
    col_left, col_right = st.columns([4, 6])

    with col_left:
        st.markdown("""
        <div style="padding:40px 24px; display:flex; flex-direction:column;
                    align-items:center; justify-content:center; height:100%;">
            <div class="avatar-circle">
                <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/assets/teacher_icon.png">
            </div>
            <div class="info-box">
                <div style="font-size:26px;flex-shrink:0;">🛡️</div>
                <div>
                    <h4>Welcome Back!</h4>
                    <p>Login to mark attendance, manage students and view reports seamlessly.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<p class="form-label">Username</p>', unsafe_allow_html=True)
        username = st.text_input("u", placeholder="Enter your username", key="login_username", label_visibility="collapsed")

        st.markdown('<p class="form-label">Password</p>', unsafe_allow_html=True)
        password = st.text_input("p", placeholder="Enter your password", key="login_password", type="password", label_visibility="collapsed")

        if st.button("👤  Login", key="login_btn"):
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                teacher = teacher_login(username, password)
                if teacher:
                    st.session_state['teacher'] = teacher
                    st.session_state['login_type'] = 'teacher_dashboard'
                    st.success(f"✅ Welcome back, {teacher['name']}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")

        st.markdown("""
        <div class="bottom-link">
            Don't have an account? <a href="?portal=teacher">Register instead</a>
        </div>
        """, unsafe_allow_html=True)

    # ---- FOOTER ----
    st.markdown("""
    <div class="sa-footer">
        <div class="sa-footer-badge">🛡️ &nbsp; Powered by AI Face Recognition</div>
    </div>
    """, unsafe_allow_html=True)