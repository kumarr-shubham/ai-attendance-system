import streamlit as st

def style_background_home():
    st.markdown("""
        <style>
            .stApp {
                background: linear-gradient(135deg, #1a4fd6 0%, #2563eb 40%, #1d4ed8 70%, #1e40af 100%) !important;
            }
            .stApp div[data-testid="stColumn"] {
                background-color: transparent !important;
                padding: 0 !important;
                border-radius: 0 !important;
            }
        </style>
    """, unsafe_allow_html=True)

def style_background_dashboard():
    st.markdown("""
        <style>
            .stApp {
                background: #E0E3FF !important;
            }
        </style>
    """, unsafe_allow_html=True)

def style_base_layout():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

            #MainMenu, footer, header { visibility: hidden; }

            .block-container {
                padding-top: 1.5rem !important;
            }

            h1, h3, h4, p {
                font-family: 'Poppins', sans-serif !important;
            }
        </style>
    """, unsafe_allow_html=True)