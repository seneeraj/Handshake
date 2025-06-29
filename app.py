import streamlit as st

import streamlit as st
st.title("✅ Rental Matchmaker App Running!")

import json
import os

USER_FILE = "users.json"
OWNER_FILE = "data_owner.json"
CANDIDATE_FILE = "data_candidate.json"

def load_data(file):
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)
    with open(file, 'r') as f:
        return json.load(f)

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

users = load_data(USER_FILE)
owner_data = load_data(OWNER_FILE)
candidate_data = load_data(CANDIDATE_FILE)

st.title("🏠 Rental Matchmaker App")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = ""
if 'role' not in st.session_state:
    st.session_state.role = ""
if 'registering' not in st.session_state:
    st.session_state.registering = False

def login():
    st.subheader("🔑 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.user_id = username
                st.session_state.role = users[username]["role"]
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password.")
    with col2:
        if st.button("New User? Register Here"):
            st.session_state.registering = True

def register():
    st.subheader("🔐 New User Registration")
    new_user = st.text_input("Create Username", key="reg_user")
    new_pass = st.text_input("Create Password", type="password", key="reg_pass")
    role = st.selectbox("You are a", ["Property Owner", "Candidate Looking for Rent"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Registration"):
            if new_user in users:
                st.warning("Username already exists.")
            elif not new_user or not new_pass:
                st.warning("Please fill in all fields.")
            else:
                users[new_user] = {"password": new_pass, "role": role}
                save_data(USER_FILE, users)
                st.success("Registration successful. Please login.")
                st.session_state.registering = False
    with col2:
        if st.button("Already Registered? Go to Login"):
            st.session_state.registering = False

def owner_page():
    st.subheader("🏘️ Property Owner Page")
    location = st.text_input("Location of Property")
    property_type = st.selectbox("Type of Property", ["Apartment", "House", "PG", "Other"])
    rent = st.number_input("Rent per month (INR)", min_value=0)

    if st.button("Save Property"):
        owner_data[st.session_state.user_id] = {
            "location": location,
            "type": property_type,
            "rent": rent
        }
        save_data(OWNER_FILE, owner_data)
        st.success("Property details saved.")

def candidate_page():
    st.subheader("👤 Candidate Preferences Page")
    location = st.text_input("Preferred Location")
    property_type = st.selectbox("Preferred Type", ["Apartment", "House", "PG", "Other"])
    can_pay = st.number_input("Can Pay per month (INR)", min_value=0)

    if st.button("Save Preferences"):
        candidate_data[st.session_state.user_id] = {
            "location": location,
            "type": property_type,
            "can_pay": can_pay
        }
        save_data(CANDIDATE_FILE, candidate_data)
        st.success("Preferences saved.")

def matching_page():
    st.subheader("🔍 Matching Owners and Candidates")
    matches = []
    for c_id, c_data in candidate_data.items():
        for o_id, o_data in owner_data.items():
            if (
                c_data["location"].lower() == o_data["location"].lower() and
                c_data["type"] == o_data["type"] and
                c_data["can_pay"] >= o_data["rent"]
            ):
                matches.append({
                    "Candidate": c_id,
                    "Owner": o_id,
                    "Location": o_data["location"],
                    "Type": o_data["type"],
                    "Rent": o_data["rent"]
                })

    if matches:
        st.success(f"Found {len(matches)} matches:")
        for match in matches:
            st.write(match)
    else:
        st.warning("No matches found yet.")

if not st.session_state.logged_in:
    if st.session_state.registering:
        register()
    else:
        login()
else:
    st.sidebar.success(f"Logged in as: {st.session_state.user_id} ({st.session_state.role})")
    nav = st.sidebar.radio("Navigation", ["Dashboard", "Matching Report", "Logout"])

    if nav == "Logout":
        st.session_state.logged_in = False
        st.experimental_rerun()
    elif st.session_state.role == "Property Owner":
        if nav == "Dashboard":
            owner_page()
        elif nav == "Matching Report":
            matching_page()
    elif st.session_state.role == "Candidate Looking for Rent":
        if nav == "Dashboard":
            candidate_page()
        elif nav == "Matching Report":
            matching_page()
