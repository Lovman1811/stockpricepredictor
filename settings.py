import streamlit as st
from database import verify_user, reset_password, get_user_details, update_user_details, delete_user


def show_settings_page():
    st.markdown("<h1 class='page-title'>⚙️ Account Settings</h1>", unsafe_allow_html=True)

    if st.session_state.user_id:
        # Create tabs for different settings
        tab1, tab2 = st.tabs(["Password", "Account"])

        with tab1:
            st.markdown("<div class='settings-panel'>", unsafe_allow_html=True)
            with st.form("settings_form"):
                st.subheader("Change Password")
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")

                if st.form_submit_button("Update Password"):
                    if new_password != confirm_password:
                        st.error("New passwords don't match")
                    else:
                        user_id = verify_user(st.session_state.username, current_password)
                        if user_id:
                            reset_password(st.session_state.username, new_password)
                            st.success("Password updated successfully!")
                        else:
                            st.error("Current password is incorrect")
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:  # Fixed indentation (now at same level as tab1)
            st.markdown("<div class='settings-panel'>", unsafe_allow_html=True)
            st.subheader("Account Information")

            user_details_list = get_user_details(st.session_state.username)

            if user_details_list:
                user = user_details_list[0]

                # Display non-editable fields
                # st.markdown(f"**Username:** {user['username']}")
                st.markdown(f"**Aadhar ID:** {user['aadhar_id']}")
                st.markdown(f"**Email:** {user['email']}")

                # Editable fields form
                with st.form("account_info_form"):
                    full_name = st.text_input("Full Name *", value=user['full_name'])
                    age = st.number_input("Age *", min_value=1, max_value=150, value=user['age'])
                    phone_no = st.text_input("Phone Number *", value=user['phone_no'])
                    address = st.text_area("Address *", value=user['address'])

                    update_clicked = st.form_submit_button("Update Information")
                    if update_clicked:
                        if not full_name.strip() or not phone_no.strip() or not address.strip():
                            st.error("Please fill all required fields")
                        else:
                            if update_user_details(
                                    username=st.session_state.username,
                                    full_name=full_name.strip(),
                                    age=age,
                                    phone_no=phone_no.strip(),
                                    address=address.strip()
                            ):
                                st.success("Account information updated successfully!")
                            else:
                                st.error("Failed to update account information")

                # Danger zone
                st.markdown("<div class='danger-zone'>", unsafe_allow_html=True)
                st.markdown("<h4>Danger Zone</h4>", unsafe_allow_html=True)

                if st.button("Delete Account", type="secondary", key="delete_init"):
                    st.warning("This action cannot be undone!")

                    confirm_delete = st.checkbox("I understand this will permanently delete my account and all my data")
                    if confirm_delete:
                        if st.button("Permanently Delete My Account", key="delete_confirm"):
                            if delete_user(st.session_state.username):
                                # Clear session state
                                st.session_state.clear()
                                st.success("Account deleted successfully!")
                                # Refresh the page
                                st.rerun()
                            else:
                                st.error("Failed to delete account")
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("No user details found.")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Please login to access settings")