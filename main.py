import streamlit as st
from datetime import date, datetime
import time

# Import from other modules
from auth import login_page, register_page, forgot_password_page
from database import initialize_db
from ui_components import set_png_as_page_bg, local_css, create_horizontal_menu
from prediction import show_prediction_page
from news import show_news_page
from favorites import show_favorites_page
from history import show_history_page
from settings import show_settings_page

# Configure page settings
st.set_page_config(
    page_title="Stock Price Predictor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add this right after your imports (replace any existing CSS code)
st.markdown(f"""
    <style>
        /* Main background and text */
        [data-testid="stAppViewContainer"] > .main {{
            background-color: #bfeff1;
            color: #000000;
        }}
        
    
        }}
        /* All text elements */
        body, .stTextInput>label, .stSelectbox>label, .stSlider>label,
        .stButton>button, .st-bb, .st-at, .st-ae, .st-af, .st-ag {{
            color: #000000 !important;
        }}

        /* Button animations */
        .stButton>button {{
            transition: all 0.3s ease;
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
            border: 1px solid #00000030;
        }}
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        /* User info card */
        .user-info {{
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid #00000020 !important;
        }}

        /* Menu divider animation */
        hr.menu-divider {{
            height: 2px;
            background: linear-gradient(90deg, transparent, #000000, transparent);
            margin: 1rem 0;
            border: none;
        }}

        /* Fade-in animation */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .fade-in {{
            animation: fadeIn 0.5s ease-out;
        }}


        /* Input fields */
        .stTextInput>div>div>input, .stSelectbox>div>select {{
            background-color: #ffffff80 !important;
            color: #000000 !important;
        }}
    </style>
""", unsafe_allow_html=True)

# Initialize Database
initialize_db()

# User Session Management
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_login' not in st.session_state:
    st.session_state.show_login = True
if 'show_forgot_password' not in st.session_state:
    st.session_state.show_forgot_password = False
if 'show_register' not in st.session_state:
    st.session_state.show_register = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "📊 Stock Prediction"


# Dashboard Layout
def dashboard():
    # Replace sidebar with horizontal menu
    menu_items = [
        "📊 Stock Prediction",
        "📰 News",
        "⭐ Favorites",
        "📚 History",
        "⚙️ Settings"
    ]
    st.markdown("""
        <style>
            div[data-testid="stHorizontalBlock"]:first-child {
                background-color: #415d80 !important;
                padding: 10px 20px !important;
                border-radius: 8px !important;
                margin: -35px -20px 20px -20px !important;
            }
            div[data-testid="stHorizontalBlock"]:first-child button {
                color: white !important;
                border: none !important;
                box-shadow: none !important;
                background: transparent !important;
                transition: all 0.3s !important;
            }
            div[data-testid="stHorizontalBlock"]:first-child button:hover {
                transform: translateY(-2px) !important;
                color: #ffd700 !important;
            }
        </style>
        """, unsafe_allow_html=True)
    # Display username and logout button in the top-right
    col1, col2 = st.columns([4, 1])
    with col2:
        # Create two columns within the right-side column
        user_info_col, logout_col = st.columns([2, 1])

        with user_info_col:
            st.markdown(f"""
                    <div class="user-info" style="display: flex; width: 130px; align-items: center; background: linear-gradient(to right, #f8f9fa, #e9ecef); padding: 5px 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 10px 0; position: relative; top: -6px;">
                    <span style="font-family: 'Segoe UI', Arial, sans-serif; font-weight: 500; color: #000000; max-width: 150px; overflow: hidden; text-overflow: ellipsis;">{st.session_state.username}</span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#007bff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        
                    </div>
                """, unsafe_allow_html=True)

        with logout_col:
            if st.button("Logout", key="logout_btn"):
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.show_login = True
                st.session_state.active_tab = "📊 Stock Prediction"
                st.rerun()
    # Create and render horizontal menu
    with col1:
        # Create menu items as buttons
        cols = st.columns(len(menu_items))
        for index, item in enumerate(menu_items):
            if cols[index].button(item, key=f"menu_{index}"):
                st.session_state.active_tab = item
                st.rerun()

    # Display divider
    st.markdown('<hr class="menu-divider">', unsafe_allow_html=True)

    # Display content based on active tab
    if st.session_state.active_tab == "📊 Stock Prediction":
        show_prediction_page()
    elif st.session_state.active_tab == "📰 News":
        show_news_page()
    elif st.session_state.active_tab == "⭐ Favorites":
        show_favorites_page()
    elif st.session_state.active_tab == "📚 History":
        show_history_page()
    elif st.session_state.active_tab == "⚙️ Settings":
        show_settings_page()


# Main App Flow
if st.session_state.show_login:
    login_page()
elif st.session_state.show_register:
    register_page()
elif st.session_state.show_forgot_password:
    forgot_password_page()
elif st.session_state.user_id:
    dashboard()


