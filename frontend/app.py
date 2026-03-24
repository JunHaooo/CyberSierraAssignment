import streamlit as st
import requests
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# 1. Initialize session state
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = {} # {filename: [sheet_names]}
if "history" not in st.session_state:
    st.session_state["history"] = []
if "last_answer" not in st.session_state:
    st.session_state["last_answer"] = None

st.set_page_config(page_title="AI Data Query", layout="wide")
st.title("AI-powered Multi-File Query App")

# 2. Upload Multiple Files
uploaded_files = st.file_uploader(
    "Upload CSV/XLSX files", 
    type=["csv", "xls", "xlsx"], 
    accept_multiple_files=True
)

# Get a list of names currently in the uploader
current_file_names = [f.name for f in uploaded_files] if uploaded_files else []

# Identify files that were removed via the 'X' button
files_to_remove = [
    fname for fname in st.session_state["uploaded_files"] 
    if fname not in current_file_names
]

# Remove them from session state
for fname in files_to_remove:
    del st.session_state["uploaded_files"][fname]
    # Optional: Reset last_answer if it was related to the deleted file
    if st.session_state["last_answer"] and fname in str(st.session_state["last_answer"]):
        st.session_state["last_answer"] = None
    st.rerun()

# --- LOGIC: Handle Uploads to Backend ---
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file.name not in st.session_state["uploaded_files"]:
            with st.spinner(f"Uploading {uploaded_file.name}..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                try:
                    res = requests.post(f"{BACKEND_URL}/upload", files=files).json()
                    if res.get("success"):
                        # Get sheet names locally just for the UI dropdown logic
                        if uploaded_file.name.lower().endswith(('.xls', '.xlsx')):
                            xl = pd.ExcelFile(uploaded_file)
                            sheets = xl.sheet_names
                        else:
                            sheets = [None]
                        
                        st.session_state["uploaded_files"][uploaded_file.name] = sheets
                except Exception as e:
                    st.error(f"Upload Error: {e}")

# --- UI: Data Preview (Using Backend /top_rows) ---
if st.session_state["uploaded_files"]:
    st.divider()
    st.subheader("🔍 Data Preview")
    
    p_col1, p_col2, p_col3 = st.columns([3, 2, 1])
    
    with p_col1:
        sel_file = st.selectbox("Select file to preview", options=list(st.session_state["uploaded_files"].keys()))
    with p_col2:
        file_sheets = st.session_state["uploaded_files"][sel_file]
        sel_sheet = st.selectbox("Select sheet", options=file_sheets) if file_sheets[0] else None
    with p_col3:
        n_val = st.number_input("N rows", min_value=1, max_value=100, value=5)

    if st.button("Fetch Preview"):
        payload = {
            "filename": sel_file, 
            "sheet_name": sel_sheet if sel_sheet is not None else "", 
            "n": n_val
        }
        try:
            resp = requests.post(f"{BACKEND_URL}/top_rows", json=payload).json()
            if "columns" in resp:
                df_preview = pd.DataFrame(data=resp["rows"], columns=resp["columns"])
                st.table(df_preview) # or st.dataframe
            else:
                st.error("Could not fetch preview.")
        except Exception as e:
            st.error(f"Backend Error: {e}")

# --- UI: Query Section ---
if st.session_state["uploaded_files"]:
    st.divider()
    st.subheader("💬 Ask a Question")
    
    # 1. Selection Row (OUTSIDE the form for instant reactivity)
    q_col1, q_col2 = st.columns(2)
    
    target_f = q_col1.selectbox(
        "Target File", 
        options=list(st.session_state["uploaded_files"].keys()), 
        key="query_file_sel"
    )
    
    sheets = st.session_state["uploaded_files"][target_f]
    if sheets and sheets[0] is not None:
        target_s = q_col2.selectbox("Target Sheet", options=sheets, key=f"sheet_sel_{target_f}")
    else:
        target_s = ""
        q_col2.selectbox("Target Sheet", options=["N/A (CSV File)"], disabled=True, key=f"csv_disabled_{target_f}")

    # 2. Query Form (INSIDE the form to enable the Enter key)
    # clear_on_submit=True makes the UI feel like a chat app
    with st.form("query_form", clear_on_submit=True):
        query_text = st.text_input(f"Question about: {target_f}")
        submit_btn = st.form_submit_button("Get Answer", type="primary")

    # 3. Handle Submission Logic
    if submit_btn and query_text.strip():
        query_payload = {
            "filename": target_f, 
            "query": query_text, 
            "sheet_name": target_s
        }
        
        with st.spinner("AI is analyzing..."):
            try:
                response = requests.post(f"{BACKEND_URL}/query", json=query_payload)
                res = response.json()
                
                # Update session state
                st.session_state["last_answer"] = res.get("answer", "No answer found.")
                st.session_state["history"].insert(0, {"file": target_f, "prompt": query_text})
                
                # Rerun to show the answer and update history immediately
                # st.rerun()
                
            except Exception as e:
                st.error(f"Query Error: {e}")

    # 4. Display Answer
    if st.session_state["last_answer"]:
        st.info(f"**Answer:** {st.session_state['last_answer']}")

# --- UI: History ---
if st.session_state["history"]:
    st.divider()
    st.subheader("History")
    
    for item in st.session_state["history"]:
        # Show which file this was for as a small, non-copyable label
        st.caption(f"Source: {item['file']}")
        
        # Show the prompt in a copyable code block without the filename inside it
        st.code(item['prompt'], language=None)