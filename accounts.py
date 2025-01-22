from libraries import *


import re  # For email validation
def run():
    def is_valid_email(email):
        """Validate the email format."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

    def is_password_strong(password):
        """Check if password is strong enough."""
        return (
            len(password) >= 8 and
            any(char.isdigit() for char in password) and
            any(char.isalpha() for char in password) and
            any(char in "!@#$%^&*()-_" for char in password)
        )


    components()
    st.markdown(
        '''<div style='margin-top: 20px; text-align: left;'>
            <h4 style='color: #1d3557;'>Welcome To Resume Parser</h4>
        </div>''',
        unsafe_allow_html=True
    )

    choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])
    if choice == 'Login':
        email = st.text_input('Email')
        name = st.text_input('User Name')
        password = st.text_input('Password', type='password')
        
        if st.button('Login'):
            if not email or not password:
                st.error("Please fill in all fields.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            else:
                st.success("Login successful!")
    else:
        email = st.text_input('Email')
        name = st.text_input('User Name')
        password = st.text_input('Password', type='password')
        confirm_password = st.text_input('Confirm Password', type='password')
        
        if st.button('Create my account'):
            if not email or not name or not password or not confirm_password:
                st.error("Please fill in all fields.")
            elif not is_valid_email(email):
                st.error("Please enter a valid email address.")
            elif password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            elif not is_password_strong(password):
                st.error("Password must be at least 8 characters long, include letters, numbers, and a special character(!@#$%^&*()-_).")
            else:
                st.success("Account created successfully!")

