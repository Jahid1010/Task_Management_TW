import streamlit as st
import json
from datetime import datetime

# File paths
TASK_FILE_PATH = "tasks.json"
USER_FILE_PATH = "users.json"

# Helper functions
def load_json(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Authentication
def login_user(email, password):
    users = load_json(USER_FILE_PATH)
    if email in users and users[email]['password'] == password:
        return users[email]['role']
    return None

# Session Initialization
if 'email' not in st.session_state:
    st.session_state.email = None
    st.session_state.role = None

# Sidebar Navigation
menu = ["Login"]
if st.session_state.email:
    if st.session_state.role == "admin":
        menu = ["User Tasks", "Assign Task", "All Tasks", "Logout"]
    else:
        menu = ["User Tasks", "Logout"]
choice = st.sidebar.selectbox("Menu", menu)

# 1. LOGIN PAGE
if choice == "Login":
    st.title("🔐 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        role = login_user(email, password)
        if role:
            st.session_state.email = email
            st.session_state.role = role
            st.success(f"Logged in as {role}")
            st.rerun()
        else:
            st.error("Invalid credentials")

# LOGOUT
elif choice == "Logout":
    st.session_state.email = None
    st.session_state.role = None
    st.success("Logged out successfully")
    st.rerun()

# 2. USER TASK PAGE
elif choice == "User Tasks":
    st.title("📋 My Tasks")
    tasks = load_json(TASK_FILE_PATH)
    my_tasks = [task for task in tasks if task['email'] == st.session_state.email]

    for i, task in enumerate(my_tasks):
        with st.expander(f"{task['project']} - Due: {task['due_date']}"):
            st.write(task['description'])
            task_summary = st.text_area("Summary", value=task.get('summary', ''), key=f"summary_{i}")
            if st.button("Mark as Done", key=f"done_{i}"):
                tasks[i]['status'] = "done"
                tasks[i]['summary'] = task_summary
                save_json(TASK_FILE_PATH, tasks)
                st.success("Task updated")
                st.rerun()

# 3A. ASSIGN TASK PAGE (Admin)
elif choice == "Assign Task" and st.session_state.role == "admin":
    st.title("🛠️ Assign Task")
    users = load_json(USER_FILE_PATH)
    emails = list(users.keys())
    email = st.selectbox("Assign to", emails)
    project = st.text_input("Project Name")
    description = st.text_area("Task Description")
    due_date = st.date_input("Due Date")

    if st.button("Assign"):
        new_task = {
            "email": email,
            "project": project,
            "description": description,
            "due_date": due_date.strftime("%Y-%m-%d"),
            "status": "pending",
            "summary": ""
        }
        tasks = load_json(TASK_FILE_PATH)
        tasks.append(new_task)
        save_json(TASK_FILE_PATH, tasks)
        st.success("Task assigned successfully")

# 3B. ALL TASKS OVERVIEW (Admin)
elif choice == "All Tasks" and st.session_state.role == "admin":
    st.title("📊 All Tasks Overview")
    tasks = load_json(TASK_FILE_PATH)
    if tasks:
        st.dataframe(tasks)
    else:
        st.info("No tasks assigned yet.")
