import streamlit as st
import time
import random
import smtplib
import sqlite3
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ui_components import set_png_as_page_bg
from database import create_user, verify_user, reset_password, get_user_details

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_USER = "lds822001@gmail.com"
SMTP_PASSWORD = "mlczcsxnqitvaout"  # Update with app-specific password
OTP_VALIDITY = 300  # 5 minutes in seconds


def send_otp_email(receiver_email, otp):
    try:
        message = MIMEMultipart()
        message["From"] = SMTP_USER
        message["To"] = receiver_email
        message["Subject"] = "Your Verification OTP"

        body = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background: linear-gradient(to right, #f8f9fa, #e9ecef);">
            <h2 style="color: #333; text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 15px; margin-bottom: 20px;">Stock Price Predictor Verification</h2>
            <div style="background-color: white; padding: 20px; border-radius: 8px; text-align: center;">
                <p style="font-size: 16px; color: #555; margin-bottom: 15px;">Your One-Time Password (OTP) is:</p>
                <h1 style="color: #007bff; font-size: 42px; letter-spacing: 5px; font-weight: 700; margin: 25px 0; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">{otp}</h1>
                <p style="font-size: 14px; color: #666; background-color: #f8f9fa; padding: 10px; border-radius: 5px; display: inline-block;">This OTP is valid for <span style="font-weight: bold;">{OTP_VALIDITY // 60} minutes</span></p>
                <p style="font-size: 12px; color: #999; margin-top: 25px;">Please do not share this code with anyone. This OTP is for verification purposes only.</p>
            </div>
            <div style="text-align: center; margin-top: 20px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                <p style="color: #777; font-size: 12px;">© 2025 Stock Price Predictor. All rights reserved.</p>
            </div>
        </div>
        """
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, receiver_email, message.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send OTP: {str(e)}")
        return False


# Enhanced CSS for the application
def apply_custom_css():
    st.markdown("""
    <style>
        /* Global Styles */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        /* Custom Container for Forms */
        .auth-container {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 30px 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            animation: fadeIn 0.6s ease-out;
            border: 1px solid rgba(255, 255, 255, 0.18);
            max-width: 500px;
            margin: 20px auto;
            transition: all 0.3s ease;
        }

        .auth-container:hover {
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
            transform: translateY(-5px);
        }

        /* Heading Styles */
        .auth-header {
            text-align: center;
            margin-bottom: 30px;
            position: relative;
            padding-bottom: 10px;
        }

        .auth-header h2 {
            color: #1e3a8a;
            font-weight: 600;
            font-size: 28px;
            margin-bottom: 10px;
        }

        .auth-header p {
            color: #64748b;
            font-size: 15px;
            font-weight: 300;
        }

        .auth-header:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            height: 3px;
            width: 60px;
            background: linear-gradient(90deg, #3b82f6, #1e40af);
            border-radius: 2px;
        }

        /* Form Field Styling */
        .stTextInput > div > div > input, 
        .stTextInput > div > div[data-baseweb="input"] {
            background-color: #f8fafc !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-size: 15px !important;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        }

        .stTextInput > div > div > input:focus, 
        .stTextInput > div > div[data-baseweb="input"]:focus-within {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
            outline: none !important;
        }

        /* Button Styling */
        .stButton > button {
            background: linear-gradient(135deg, #3b82f6, #1e40af) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-size: 16px !important;
            font-weight: 500 !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 6px rgba(30, 64, 175, 0.25) !important;
            margin-top: 10px !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 12px rgba(30, 64, 175, 0.3) !important;
            background: linear-gradient(135deg, #2563eb, #1e3a8a) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
            box-shadow: 0 2px 4px rgba(30, 64, 175, 0.2) !important;
        }

        /* Secondary Button Styling */
        .secondary-button button {
            background: transparent !important;
            color: #3b82f6 !important;
            border: 1px solid #3b82f6 !important;
            box-shadow: none !important;
        }

        .secondary-button button:hover {
            background: rgba(59, 130, 246, 0.05) !important;
            transform: translateY(-2px) !important;
        }

        /* Form Layout */
        .form-row {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }

        /* Message Styling - Success, Error, Info */
        .info-message, .success-message, .error-message {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            display: flex;
            align-items: center;
            animation: slideIn 0.3s ease-out;
        }

        .info-message {
            background-color: #eff6ff;
            border-left: 4px solid #3b82f6;
            color: #1e40af;
        }

        .success-message {
            background-color: #f0fdf4;
            border-left: 4px solid #22c55e;
            color: #166534;
        }

        .error-message {
            background-color: #fef2f2;
            border-left: 4px solid #ef4444;
            color: #b91c1c;
        }

        /* Divider with Text */
        .divider {
            display: flex;
            align-items: center;
            text-align: center;
            margin: 20px 0;
            color: #94a3b8;
        }

        .divider::before, .divider::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid #e2e8f0;
        }

        .divider::before {
            margin-right: 10px;
        }

        .divider::after {
            margin-left: 10px;
        }

        /* OTP Input Styling */
        .otp-container {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 20px 0;
        }

        .otp-input input {
            width: 50px !important;
            height: 50px !important;
            text-align: center !important;
            font-size: 24px !important;
        }

        /* Link Styling */
        a.styled-link {
            color: #3b82f6;
            text-decoration: none;
            transition: color 0.2s;
        }

        a.styled-link:hover {
            color: #1e40af;
            text-decoration: underline;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }

        /* Custom Spinner */
        .custom-spinner {
            width: 40px;
            height: 40px;
            margin: 20px auto;
            border: 4px solid rgba(59, 130, 246, 0.2);
            border-radius: 50%;
            border-top-color: #3b82f6;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        /* OTP Timer */
        .otp-timer {
            font-size: 14px;
            color: #64748b;
            text-align: center;
            margin: 10px 0;
        }

        /* Brand Logo */
        .brand-logo {
            text-align: center;
            margin-bottom: 20px;
        }

        .brand-logo img {
            height: 60px;
            animation: floatAnimation 3s ease-in-out infinite;
        }

        @keyframes floatAnimation {
            0% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0); }
        }

        /* Footer */
        .auth-footer {
            text-align: center;
            font-size: 12px;
            color: #94a3b8;
            margin-top: 20px;
        }

        /* Media Queries for Responsiveness */
        @media (max-width: 768px) {
            .auth-container {
                padding: 20px;
                margin: 10px;
            }

            .auth-header h2 {
                font-size: 24px;
            }
        }
    </style>
    """, unsafe_allow_html=True)


# Login Page
def login_page():
    set_png_as_page_bg("trade.gif")
    apply_custom_css()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <h2>Stock Price Predictor</h2>
                <p>AI-powered market analysis and predictions </p>
                <p>Created By : Lovedeep singh </p>
            </div>
        """, unsafe_allow_html=True)

        login_form = st.form(key='login_form')
        with login_form:
            username = st.text_input("Username", key="login_username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_password",
                                     placeholder="Enter your password")
            login_button = st.form_submit_button("Sign In")

            if login_button:
                user_id = verify_user(username, password)
                if user_id:
                    st.markdown("""
                    <div class="success-message">
                        <span>Login successful! Redirecting to dashboard...</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.session_state.show_login = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.markdown("""
                    <div class="error-message">
                        <span>Invalid username or password. Please try again.</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("""
            <div class="divider">OR</div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""<div class="secondary-button">""", unsafe_allow_html=True)
            if st.button("Create Account"):
                st.session_state.show_login = False
                st.session_state.show_register = True
                st.rerun()
            st.markdown("""</div>""", unsafe_allow_html=True)

        with col_b:
            st.markdown("""<div class="secondary-button">""", unsafe_allow_html=True)
            if st.button("Forgot Password?"):
                st.session_state.show_login = False
                st.session_state.show_forgot_password = True
                st.rerun()
            st.markdown("""</div>""", unsafe_allow_html=True)

        st.markdown("""
            <div class="auth-footer">
                © 2025 Stock Price Predictor. By Lovedeep Singh.
            </div>
        </div>
        """, unsafe_allow_html=True)


# Registration Page
def register_page():
    set_png_as_page_bg("trade.gif")
    apply_custom_css()

    if 'reg_stage' not in st.session_state:
        st.session_state.reg_stage = 1
    if 'reg_data' not in st.session_state:
        st.session_state.reg_data = {}

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <h2>Create Account</h2>
                <p>Join our community of traders and investors</p>
            </div>
        """, unsafe_allow_html=True)

        if st.session_state.reg_stage == 1:
            with st.form(key='register_form'):
                # Split form into two columns
                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("**Personal Information**")
                    full_name = st.text_input("Full Name", placeholder="Enter your full name")
                    age = st.number_input("Age", min_value=18, max_value=100, value=18)
                    phone_no = st.text_input("Phone Number", placeholder="Enter 10-digit number",
                                             max_chars=10)
                    aadhar_id = st.text_input("Aadhar ID", placeholder="12-digit Aadhar number",
                                              max_chars=12)

                with col_b:
                    st.markdown("**Account Information**")
                    username = st.text_input("Username", placeholder="Choose a unique username")
                    email = st.text_input("Email Address", placeholder="Enter your email address")
                    password = st.text_input("Password", type="password",
                                             placeholder="Create a strong password")
                    confirm_password = st.text_input("Confirm Password", type="password",
                                                     placeholder="Re-enter your password")

                # Address field
                address = st.text_area("Residential Address",
                                       placeholder="Enter your complete address (House No., Street, City, State, PIN)",
                                       height=80)

                if st.form_submit_button("Send Verification Code"):
                    # Validate all fields
                    errors = []
                    if not full_name:
                        errors.append("Full name is required")
                    if len(phone_no) != 10 or not phone_no.isdigit():
                        errors.append("Invalid phone number (must be 10 digits)")
                    if age < 18:
                        errors.append("You must be at least 18 years old")
                    if len(aadhar_id) != 12 or not aadhar_id.isdigit():
                        errors.append("Invalid Aadhar ID (must be 12 digits)")
                    if not address:
                        errors.append("Address is required")
                    if password != confirm_password:
                        errors.append("Passwords do not match")

                    if errors:
                        error_html = "<div class='error-message'>" + \
                                     "".join([f"<span>• {error}</span><br>" for error in errors]) + \
                                     "</div>"
                        st.markdown(error_html, unsafe_allow_html=True)
                    else:
                        conn = sqlite3.connect("stock_predictions.db")
                        c = conn.cursor()
                        c.execute("SELECT username FROM users WHERE username = ?", (username,))
                        if c.fetchone():
                            st.markdown("""
                            <div class="error-message">
                                <span>Username already exists! Please choose another one.</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            otp = str(random.randint(100000, 999999))
                            if send_otp_email(email, otp):
                                st.markdown("""
                                <div class="success-message">
                                    <span>Verification code sent successfully!</span>
                                </div>
                                """, unsafe_allow_html=True)
                                st.session_state.reg_data = {
                                    'full_name': full_name,
                                    'age': age,
                                    'phone_no': phone_no,
                                    'aadhar_id': aadhar_id,
                                    'address': address,
                                    'username': username,
                                    'email': email,
                                    'password': password,
                                    'otp': otp,
                                    'otp_time': time.time()
                                }
                                st.session_state.reg_stage = 2
                                st.rerun()
                            else:
                                st.markdown("""
                                <div class="error-message">
                                    <span>Failed to send verification code. Please try again.</span>
                                </div>
                                """, unsafe_allow_html=True)

        elif st.session_state.reg_stage == 2:
            st.markdown(f"""
            <div class="info-message">
                <span>We've sent a verification code to {st.session_state.reg_data['email']}</span>
            </div>
            """, unsafe_allow_html=True)

            with st.form(key='otp_form'):
                st.markdown("""
                <div class="otp-timer">
                    Verification code expires in 5:00 minutes
                </div>
                """, unsafe_allow_html=True)

                otp_input = st.text_input("Enter 6-digit verification code", max_chars=6,
                                          placeholder="Enter code")

                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.form_submit_button("Verify & Create Account"):
                        if time.time() - st.session_state.reg_data['otp_time'] > OTP_VALIDITY:
                            st.markdown("""
                            <div class="error-message">
                                <span>Verification code has expired. Please request a new one.</span>
                            </div>
                            """, unsafe_allow_html=True)
                            st.session_state.reg_stage = 1
                            st.rerun()


                        elif otp_input == st.session_state.reg_data['otp']:

                            success = create_user(

                                username=st.session_state.reg_data['username'],

                                password=st.session_state.reg_data['password'],

                                email=st.session_state.reg_data['email'],

                                full_name=st.session_state.reg_data['full_name'],

                                age=st.session_state.reg_data['age'],

                                phone_no=st.session_state.reg_data['phone_no'],

                                aadhar_id=st.session_state.reg_data['aadhar_id'],

                                address=st.session_state.reg_data['address']

                            )

                            if success:
                                st.markdown("""
                                <div class="success-message">
                                    <span>Account created successfully! Please sign in.</span>
                                </div>
                                """, unsafe_allow_html=True)
                                st.session_state.reg_stage = 1
                                st.session_state.show_register = False
                                st.session_state.show_login = True
                                st.rerun()
                            else:
                                st.markdown("""
                                <div class="error-message">
                                    <span>Registration failed. Please try again.</span>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="error-message">
                                <span>Invalid verification code. Please try again.</span>
                            </div>
                            """, unsafe_allow_html=True)

                with col2:
                    if st.form_submit_button("Resend"):
                        new_otp = str(random.randint(100000, 999999))
                        if send_otp_email(st.session_state.reg_data['email'], new_otp):
                            st.session_state.reg_data['otp'] = new_otp
                            st.session_state.reg_data['otp_time'] = time.time()
                            st.markdown("""
                            <div class="success-message">
                                <span>New verification code sent!</span>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="error-message">
                                <span>Failed to resend. Please try again.</span>
                            </div>
                            """, unsafe_allow_html=True)

        st.markdown("""
            <div class="divider"></div>
        """, unsafe_allow_html=True)
        st.markdown("""<div class="secondary-button">""", unsafe_allow_html=True)
        if st.button("Back to Login"):
            st.session_state.reg_stage = 1
            st.session_state.show_register = False
            st.session_state.show_login = True
            st.rerun()
        st.markdown("""</div>""", unsafe_allow_html=True)

        st.markdown("""
            </div>
        """, unsafe_allow_html=True)


# Forgot Password Page
def forgot_password_page():
    set_png_as_page_bg("trade.gif")
    apply_custom_css()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="auth-container">
            <div class="auth-header">
                <h2>Reset Password</h2>
                <p>We'll help you get back into your account</p>
            </div>
        """, unsafe_allow_html=True)

        reset_form = st.form(key='reset_form')
        with reset_form:
            username = st.text_input("Username", key="reset_username", placeholder="Enter your username")
            email = st.text_input("Email", key="reset_email", placeholder="Enter your registered email")
            new_password = st.text_input("New Password", type="password", key="reset_password",
                                         placeholder="Create new password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reset_confirm_password",
                                             placeholder="Re-enter new password")
            reset_button = st.form_submit_button("Reset Password")

            if reset_button:
                user_email = get_user_details(username)
                if user_email != email:
                    st.markdown("""
                    <div class="error-message">
                        <span>Username and email don't match our records.</span>
                    </div>
                    """, unsafe_allow_html=True)
                elif new_password != confirm_password:
                    st.markdown("""
                    <div class="error-message">
                        <span>Passwords do not match. Please try again.</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    reset_password(username, new_password)
                    st.markdown("""
                    <div class="success-message">
                        <span>Password reset successfully! You can now login with your new password.</span>
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("""
            <div class="divider"></div>
        """, unsafe_allow_html=True)
        st.markdown("""<div class="secondary-button">""", unsafe_allow_html=True)
        if st.button("Back to Login"):
            st.session_state.show_forgot_password = False
            st.session_state.show_login = True
            st.rerun()
        st.markdown("""</div>""", unsafe_allow_html=True)

        st.markdown("""
            </div>
        """, unsafe_allow_html=True)
