import streamlit as st
import os
import base64
import pandas as pd
import mammoth
from io import BytesIO

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Admin Panel",
    layout="wide"
)

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
section[data-testid="stSidebar"] {
    background-color: black;
}
section[data-testid="stSidebar"] * {
    color: white !important;
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
    """Get all files inside folder"""
    if not os.path.exists(folder):
        st.warning(f"{folder} folder not found")
        return []

    return sorted([
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ])


def read_file_once(file_path):
    """Read file once"""
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None


def display_file(folder, file_name):
    """Display selected file"""
    file_path = os.path.join(folder, file_name)

    if not os.path.exists(file_path):
        st.error("File not found")
        return

    st.subheader(f"📄 {file_name}")

    file_bytes = read_file_once(file_path)

    if file_bytes is None:
        return

    # =========================
    # DOWNLOAD BUTTON
    # =========================
    st.download_button(
        label="⬇ Download File",
        data=file_bytes,
        file_name=file_name,
        mime="application/octet-stream"
    )

    # =========================
    # PDF PREVIEW
    # =========================
    if file_name.lower().endswith(".pdf"):
        try:
            base64_pdf = base64.b64encode(file_bytes).decode("utf-8")

            st.markdown(f"""
            <iframe
                src="data:application/pdf;base64,{base64_pdf}"
                width="100%"
                height="900px"
                style="border:none;">
            </iframe>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error displaying PDF: {e}")

    # =========================
    # DOCX PREVIEW
    # =========================
    elif file_name.lower().endswith(".docx"):
        try:
            # Convert bytes to file-like object
            docx_file = BytesIO(file_bytes)

            result = mammoth.convert_to_html(docx_file)
            html = result.value

            st.components.v1.html(
                f"""
                <div style="
                    background:white;
                    padding:20px;
                    border-radius:10px;
                    height:850px;
                    overflow:auto;
                    color:black;
                    border:1px solid #ddd;
                ">
                    {html}
                </div>
                """,
                height=900,
                scrolling=True
            )

        except Exception as e:
            st.error(f"Error displaying Word document: {e}")

    # =========================
    # EXCEL / CSV PREVIEW
    # =========================
    elif file_name.lower().endswith((".xlsx", ".xls", ".csv")):
        try:
            if file_name.lower().endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(f"Error reading spreadsheet: {e}")

    # =========================
    # TEXT FILE PREVIEW
    # =========================
    elif file_name.lower().endswith(".txt"):
        try:
            text_content = file_bytes.decode("utf-8")
            st.text_area("Preview", text_content, height=500)

        except Exception as e:
            st.error(f"Error reading text file: {e}")

    # =========================
    # UNSUPPORTED FILE
    # =========================
    else:
        st.warning("Unsupported file type")


# =========================
# SEARCHABLE SELECTBOX
# =========================
def searchable_selectbox(label, options):
    search = st.text_input(f"🔍 Search {label}")

    if search:
        filtered = [
            option for option in options
            if search.lower() in option.lower()
        ]
    else:
        filtered = options

    return st.selectbox(
        label,
        ["None"] + filtered
    )


# =========================
# MAIN UI
# =========================
st.title("📂 Admin Document Portal")

with st.sidebar:
    st.header("Navigation")

    # Meetings
    meeting_files = get_files(FOLDERS["Meetings"])
    selected_meeting = st.selectbox(
        "Meetings",
        ["None"] + meeting_files
    )

    # Reports
    report_files = get_files(FOLDERS["Reports"])
    selected_report = st.selectbox(
        "Reports",
        ["None"] + report_files
    )

    # Stock
    stock_files = get_files(FOLDERS["Stock"])
    selected_stock = searchable_selectbox(
        "Stock Records",
        stock_files
    )

    # Consumables
    consumable_files = get_files(FOLDERS["Consumables"])
    selected_consumable = searchable_selectbox(
        "Consumables",
        consumable_files
    )

# =========================
# DISPLAY LOGIC
# =========================
if selected_meeting != "None":
    display_file(
        FOLDERS["Meetings"],
        selected_meeting
    )

elif selected_report != "None":
    display_file(
        FOLDERS["Reports"],
        selected_report
    )

elif selected_stock != "None":
    display_file(
        FOLDERS["Stock"],
        selected_stock
    )

elif selected_consumable != "None":
    display_file(
        FOLDERS["Consumables"],
        selected_consumable
    )

else:
    st.info("Select a file from the sidebar")
