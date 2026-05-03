import streamlit as st
import numpy as np
from PIL import Image
from src.ui.base_layout import style_base_layout, style_background_home
from src.database.db import create_student, get_all_students
from src.pipelines.face_pipeline import get_face_embeddings, get_trained_model

import streamlit as st
import numpy as np
from PIL import Image
from src.ui.base_layout import style_base_layout, style_background_home
from src.database.db import create_student, get_all_students
from src.pipelines.face_pipeline import get_face_embeddings, get_trained_model


def student_screen():

    style_background_home()
    style_base_layout()

    if "portal" in st.query_params:
        val = st.query_params["portal"]
        if val == "home":
            st.session_state['login_type'] = None
            st.session_state['show_register'] = False
            st.query_params.clear()
            st.rerun()

    if 'show_register' not in st.session_state:
        st.session_state['show_register'] = False

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a4fd6 0%, #2563eb 50%, #1e40af 100%) !important;
    }
    [data-testid="stMain"] { background: transparent !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 1.5rem !important;
        max-width: 720px !important;
    }

    .back-btn {
        display: inline-flex; align-items: center; gap: 8px;
        color: white !important; font-size: 14px; font-weight: 500;
        text-decoration: none !important;
        background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 50px; padding: 8px 16px;
    }

    .page-title { text-align: center; margin: 16px 0 20px 0; }
    .page-title h1 {
        color: white !important; font-size: 34px !important;
        font-weight: 800 !important; margin: 0 0 6px 0 !important;
    }
    .page-title p { color: rgba(255,255,255,0.75); font-size: 15px; margin: 0; }

    /* Camera input — handled separately below */

    /* All buttons */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(90deg, #1d4ed8, #2563eb) !important;
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 13px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        margin-top: 0 !important;
    }

    /* Alert */
    .info-alert {
        background: #eef1fb;
        border-radius: 14px;
        padding: 14px 18px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        color: #3b5bdb;
        font-size: 15px;
        font-weight: 500;
        border: 1px solid #c5cef5;
    }

    /* Register card */
    .reg-card {
        background: white;
        border-radius: 20px;
        padding: 24px 24px 24px 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        margin-bottom: 16px;
    }
    .reg-card h2 {
        color: #1a2a4a !important;
        font-size: 24px !important;
        font-weight: 800 !important;
        margin: 0 0 16px 0 !important;
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
        padding: 12px 16px !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #2563eb !important;
        box-shadow: none !important;
    }

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
        <div style="display:flex;align-items:center;gap:12px;">
            <img src="https://raw.githubusercontent.com/kumarr-shubham/ai-attendance-system/main/app_logo.png"
                 style="width:50px;border-radius:12px;" onerror="this.style.display='none';">
            <div>
                <div style="color:white;font-size:20px;font-weight:800;">SmartAttend <span style="color:#7dd3fc;">AI</span></div>
                <div style="color:rgba(255,255,255,0.7);font-size:12px;">Smart Attendance System using Face Recognition</div>
            </div>
        </div>
        <a href="?portal=home" class="back-btn">← Go back to Home</a>
    </div>
    """, unsafe_allow_html=True)

    # ---- PAGE TITLE ----
    st.markdown("""
    <div class="page-title">
        <h1>Verify Your Photo</h1>
        <p>Position your face in the center</p>
    </div>
    """, unsafe_allow_html=True)

    # ---- CAMERA ----
    st.markdown("""
    <style>
    [data-testid="stCameraInput"] {
        background: white;
        border-radius: 20px;
        padding: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        margin-bottom: 16px;
    }
    [data-testid="stCameraInput"] label { display: none !important; }
    [data-testid="stCameraInput"] > div {
        border-radius: 12px !important;
        overflow: hidden !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    photo = st.camera_input(".", label_visibility="collapsed", key="student_cam")

    if st.button("🛡️  Verify Photo", key="verify_btn"):
        if not photo:
            st.error("Please take a photo first.")
        else:
            with st.spinner("Analyzing your face..."):
                image = Image.open(photo).convert("RGB")
                image_np = np.array(image)
                encodings = get_face_embeddings(image_np)

                if not encodings:
                    st.error("No face detected. Please try again in better lighting.")
                else:
                    encoding = encodings[0]
                    model_data = get_trained_model()
                    recognized = False

                    if model_data:
                        clf = model_data['clf']
                        X_train = model_data['X']
                        y_train = model_data['y']
                        all_students = sorted(list(set(y_train)))

                        if len(all_students) >= 2:
                            predicted_id = int(clf.predict([encoding])[0])
                        else:
                            predicted_id = int(all_students[0])

                        student_embedding = X_train[y_train.index(predicted_id)]
                        distance = np.linalg.norm(student_embedding - encoding)

                        if distance <= 0.6:
                            recognized = True
                            students = get_all_students()
                            matched = next((s for s in students if s['student_id'] == predicted_id), None)
                            st.session_state['student'] = matched
                            st.session_state['student_data'] = matched
                            st.session_state['is_logged_in'] = True
                            st.session_state['user_role'] = 'student'
                            st.session_state['login_type'] = 'student_dashboard'
                            st.rerun()

                    if not recognized:
                        st.session_state['face_embedding'] = encoding.tolist()
                        st.session_state['show_register'] = True
                        st.rerun()

    # ---- NOT RECOGNIZED — REGISTER ----
    if st.session_state.get('show_register'):

        st.markdown("""
        <div class="info-alert">
            <span style="font-size:20px;">ℹ️</span>
            Face not recognized. You might be a new student!
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="reg-card">
            <h2>Register New Profile</h2>
        </div>
        """, unsafe_allow_html=True)

        new_name = st.text_input("name", placeholder="Enter your full name",
                                  key="new_student_name", label_visibility="collapsed")

        if st.button("👤  Add New Profile", key="add_profile_btn"):
            if not new_name.strip():
                st.error("Please enter your name.")
            else:
                embedding = st.session_state.get('face_embedding')
                result = create_student(new_name.strip(), embedding)
                if result:
                    st.session_state['student'] = result[0]
                    st.session_state['student_data'] = result[0]
                    st.session_state['show_register'] = False
                    st.session_state['face_embedding'] = None
                    st.session_state['is_logged_in'] = True
                    st.session_state['user_role'] = 'student'
                    st.session_state['login_type'] = 'student_dashboard'
                    st.rerun()
                else:
                    st.error("Something went wrong. Please try again.")

    # ---- FOOTER ----
    st.markdown("""
    <div class="sa-footer">
        <div class="sa-footer-badge">🛡️ &nbsp; Powered by AI Face Recognition</div>
    </div>
    """, unsafe_allow_html=True)