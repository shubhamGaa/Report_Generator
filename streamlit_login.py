import streamlit as st
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import bcrypt
from datetime import datetime
import time
import os
from dotenv import load_dotenv
# Initialize MongoDB connection

load_dotenv()

def get_db_connection():
    try:
        # Replace with your actual connection string and password
        connection_string = os.getenv("MONGO_URI")
        client = MongoClient(connection_string)
        db = client['user_authentication']
        return db
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        return None

# Initialize collections
def init_db():
    db = get_db_connection()
    if db is not None:
        users = db['users']
        users.create_index("username", unique=True)
        return users
    return None

# Hash password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verify password
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

# Register new user
def register_user(username, password, email):
    users = init_db()
    if users is not None:
        try:
            hashed = hash_password(password)
            user_data = {
                "username": username,
                "password": hashed,
                "email": email,
                "created_at": datetime.utcnow(),
                "last_login": None
            }
            users.insert_one(user_data)
            return True
        except DuplicateKeyError:
            st.error("Username already exists!")
            return False
        except Exception as e:
            st.error(f"Registration failed: {e}")
            return False
    return False

# Authenticate user
def authenticate_user(username, password):
    users = init_db()
    if users is not None:
        user = users.find_one({"username": username})
        if user and verify_password(password, user['password']):
            # Update last login time
            users.update_one(
                {"_id": user['_id']},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            return user
    return None

# Dashboard page
def dashboard_page():
    st.title("Welcome to Your Dashboard")
    st.write(f"Hello, {st.session_state['username']}!")
    
    st.subheader("Your Account Information")
    col1, col2 = st.columns(2)
    with col1:
        st.info("Username: " + st.session_state['username'])
    with col2:
        st.info("Email: " + st.session_state['email'])
    
    st.subheader("Recent Activity")
    st.write("Last login: " + str(st.session_state.get('last_login', 'First time login!')))
    
    st.subheader("Quick Actions")
    if st.button("Refresh Data"):
        st.success("Data refreshed successfully!")
    
    if st.button("Logout", key="logout_button"):
        st.session_state.clear()
        st.rerun()

# Login page
def login_page():
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            if username and password:
                user = authenticate_user(username, password)
                if user:
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = user['username']
                    st.session_state['email'] = user.get('email', '')
                    st.session_state['last_login'] = user.get('last_login', '')
                    st.success("Login successful!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            else:
                st.warning("Please enter both username and password")

# Registration page
def register_page():
    st.title("Register")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_button = st.form_submit_button("Register")
        
        if submit_button:
            if password == confirm_password:
                if len(password) >= 6:
                    if register_user(username, password, email):
                        st.success("Registration successful! Please login.")
                        time.sleep(2)
                        st.session_state['page'] = 'login'
                        st.rerun()
                else:
                    st.error("Password must be at least 6 characters long")
            else:
                st.error("Passwords do not match")

# Main app
def main():
    st.set_page_config(
        page_title="Auth System",
        page_icon="🔒",
        layout="wide"
    )
    
    # Custom CSS for better UI
    st.markdown("""
    <style>
        .stTextInput input, .stTextInput input:focus {
            border: 1px solid #4a4a4a;
            border-radius: 5px;
        }
        .stButton button {
            width: 100%;
            border-radius: 5px;
            border: 1px solid #4a4a4a;
            background-color: #4a4a4a;
            color: white;
        }
        .stButton button:hover {
            background-color: #5a5a5a;
            border: 1px solid #5a5a5a;
        }
        .css-1aumxhk {
            background-color: #f0f2f6;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # Navigation
    if st.session_state['authenticated']:
        dashboard_page()
    else:
        if st.session_state['page'] == 'login':
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                login_page()
            st.markdown("---")
            st.write("Don't have an account?")
            if st.button("Register here"):
                st.session_state['page'] = 'register'
                st.rerun()
        else:
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                register_page()
            st.markdown("---")
            st.write("Already have an account?")
            if st.button("Login here"):
                st.session_state['page'] = 'login'
                st.rerun()

if __name__ == "__main__":
    main()