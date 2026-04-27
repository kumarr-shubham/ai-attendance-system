import streamlit as st

def header_home():
    st.markdown("""
        <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; margin-bottom:20px; margin-top:10px;">
            <h1 style="text-align:center; color:white; font-size:42px; font-weight:800; margin:0; font-family:'Segoe UI',sans-serif;">
                SmartAttend <span style="color:#7dd3fc;">AI</span>
            </h1>
            <p style="color:rgba(255,255,255,0.75); font-size:16px; margin:8px 0 0 0; text-align:center;">
                Smart Attendance System using Face Recognition
            </p>
        </div>
    """, unsafe_allow_html=True)