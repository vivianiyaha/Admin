import streamlit as st
import os
import base64
import pandas as pd
import mammoth

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Admin Panel", layout="wide")

# =========================
# CUSTOM STYLING
# =========================
st.markdown("""
<style>
body {
    background-color: #ffffff;
}
.stApp {
    background-color: #ffffff;
    color: black;
}
h1, h2, h3 {
    color: #ff6600;
}
.sidebar .sidebar-content {
    background-color: black;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =========================
# FOLDERS
# =========================
FOLDERS = {
    "Meetings": "Meetings",
    "Reports": "Reports",
    "Stock": "Stock_Records",
    "Consumables": "Consumables_Records"
}

# =========================
# HELPERS
# =========================
def get_files(folder):
    if not os.path.exists(folder):
        st.warning(f"{folder} folder not found")
        return []

    return sorted([
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ])


def read_file_once(file_path):
    with open(file_path, "rb") as f:
        return f.read()


def display_file(folder, file_name):
    file_path = os.path.join(folder, file_name)

    if not os.path.exists(file_path):
        st.error("File not found")
        return

    st.subheader(file_name)

    file_bytes = read_file_once(file_path)

    # DOWNLOAD
    st.download_button(
        "⬇ Download File",
        data=file_bytes,
        file_name=file_name
    )

    # PDF
    if file_name.lower().endswith(".pdf"):
        base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
        st.markdown(f"""
        <iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="900px"></iframe>
        """, unsafe_allow_html=True)

    # DOCX
    elif file_name.lower().endswith(".docx"):
        result = mammoth.convert_to_html(file_bytes)
        html = result.value

        st.components.v1.html(f"""
        <div style='background:white;padding:20px;border-radius:10px;height:850px;overflow:auto;color:black;'>
        {html}
        </div>
        """, height=900)

    # EXCEL / CSV
    elif file_name.lower().endswith((".xlsx", ".xls", ".csv")):
        try:
            if file_name.endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")

    # TXT
    elif file_name.lower().endswith(".txt"):
        st.text_area("Preview", file_bytes.decode("utf-8"), height=500)

    else:
        st.warning("Unsupported file type")


# =========================
# SEARCHABLE SELECT
# =========================
def searchable_selectbox(label, options):
    search = st.text_input(f"Search {label}")
    filtered = [o for o in options if search.lower() in o.lower()] if search else options
    return st.selectbox(label, ["None"] + filtered)


# =========================
# UI
# =========================
st.title("📂 Admin Document Portal")

with st.sidebar:
    st.header("Navigation")

    meeting_files = get_files(FOLDERS["Meetings"])
    selected_meeting = st.selectbox("Meetings", ["None"] + meeting_files)

    report_files = get_files(FOLDERS["Reports"])
    selected_report = st.selectbox("Reports", ["None"] + report_files)

    stock_files = get_files(FOLDERS["Stock"])
    selected_stock = searchable_selectbox("Stock Records", stock_files)

    consumable_files = get_files(FOLDERS["Consumables"])
    selected_consumable = searchable_selectbox("Consumables", consumable_files)

# =========================
# DISPLAY LOGIC
# =========================
if selected_meeting != "None":
    display_file(FOLDERS["Meetings"], selected_meeting)

elif selected_report != "None":
    display_file(FOLDERS["Reports"], selected_report)

elif selected_stock != "None":
    display_file(FOLDERS["Stock"], selected_stock)

elif selected_consumable != "None":
    display_file(FOLDERS["Consumables"], selected_consumable)

else:
    st.info("Select a file from the sidebar")
        
