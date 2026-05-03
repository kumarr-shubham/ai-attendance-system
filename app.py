import streamlit as st
from src.screens.home_screen import home_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.teacher_login_screen import teacher_login_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_dashboard import teacher_dashboard_screen
from src.screens.student_dashboard import student_dashboard


def main():
    st.set_page_config(
        page_title='Smart Attend AI – AI Powered Attendance System',
        page_icon='📚'
    )
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

        elif val == "teacher_login":
            st.session_state['login_type'] = 'teacher_login'
            st.query_params.clear()
            st.rerun()

        elif val == "student":
            st.session_state['login_type'] = 'student'
            st.query_params.clear()
            st.rerun()

    # handle auto-enroll join code from QR / shared link
    if "join-code" in st.query_params:
        join_code = st.query_params["join-code"]
        if st.session_state.get('is_logged_in') and st.session_state.get('user_role') == 'student':
            from src.components.dialog_auto_enroll import auto_enroll_dialog
            auto_enroll_dialog(join_code)
        else:
            # not logged in — go to student screen first, code will be handled after login
            st.session_state['login_type'] = 'student'
            st.query_params.clear()
            st.rerun()

    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    login_type = st.session_state['login_type']

    # ── Teacher flow ──
    if login_type == 'teacher':
        teacher_screen()

    elif login_type == 'teacher_login':
        teacher_login_screen()

    elif login_type == 'teacher_dashboard':
        teacher_dashboard_screen()

    # ── Student flow ──
    elif login_type == 'student':
        student_screen()

    elif login_type == 'student_dashboard':
        student_dashboard()

    # ── Home ──
    else:
        home_screen()


main()