import streamlit as st
import base64
from PIL import Image


# Custom CSS styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


# Animation and Image Handling
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    </style>
    ''' % bin_str

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return


# Create horizontal menu bar
def create_horizontal_menu(items, active_item):
    # Create columns for the menu items
    cols = st.columns(len(items) + 1)  # +1 for spacing

    # Add custom CSS for styling
    st.markdown("""
    <style>
    .menu-button {
        border: 1px solid #007bff;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        margin: 0 2px;
        cursor: pointer;
        transition: all 0.3s ease;
        background-color: transparent;
        color: #007bff;
    }
    .menu-button:hover {
        background-color: #007bff22;
    }
    .menu-button.active {
        background-color: #007bff;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Create buttons for each menu item
    for index, (col, item) in enumerate(zip(cols[:-1], items)):  # Exclude last column for spacing
        is_active = (item == active_item)
        button_style = "active" if is_active else ""

        # Create a unique key for each button
        button_key = f"menu_btn_{index}"

        # Use markdown to create styled buttons that look clickable
        col.markdown(f"""
            <div class="menu-button {button_style}" onclick="document.querySelector('button[id=\\'{button_key}\\']').click()">
                {item}
            </div>
        """, unsafe_allow_html=True)

        # Actual invisible button for handling clicks
        if col.button(item, key=button_key, label_visibility="collapsed"):
            st.session_state.active_tab = item
            st.rerun()

    return active_item

