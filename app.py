import streamlit as st
import os
import base64
import mammoth

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Admin Document Portal",
    layout="wide"
)

# =========================
# FOLDERS
# =========================
MEETINGS_FOLDER = "Meetings"
REPORTS_FOLDER = "Reports"

# =========================
# HELPERS
# =========================
def get_files(folder):
    if not os.path.exists(folder):
        st.warning(f"{folder} folder not found")
        return []

    return sorted(
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    )


def display_file(folder, file_name):
    file_path = os.path.join(folder, file_name)

    st.subheader(file_name)

    if not os.path.exists(file_path):
        st.error("File not found")
        return

    # Read file once
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # =========================
    # DOWNLOAD BUTTON
    # =========================
    st.download_button(
        "⬇ Download File",
        data=file_bytes,
        file_name=file_name,
        mime="application/octet-stream"
    )

    # =========================
    # PDF PREVIEW (Original Format)
    # =========================
    if file_name.lower().endswith(".pdf"):

        base64_pdf = base64.b64encode(file_bytes).decode("utf-8")

        st.markdown(
            f"""
            <iframe
                src="data:application/pdf;base64,{base64_pdf}"
                width="100%"
                height="900px"
                style="border:none;"
            ></iframe>
            """,
            unsafe_allow_html=True
        )

    # =========================
    # DOCX PREVIEW (Word-like Format)
    # =========================
    elif file_name.lower().endswith(".docx"):

        result = mammoth.convert_to_html(file_bytes)
        html = result.value

        st.markdown("### Document Preview")

        st.components.v1.html(
            f"""
            <div style="
                background:white;
                padding:20px;
                border-radius:10px;
                border:1px solid #ddd;
                height:850px;
                overflow:auto;
                color:black;
                font-family: Arial, sans-serif;
            ">
                {html}
            </div>
            """,
            height=900,
            scrolling=True
        )

    # =========================
    # TXT FILES
    # =========================
    elif file_name.lower().endswith(".txt"):

        st.text_area(
            "Text Preview",
            file_bytes.decode("utf-8"),
            height=500
        )

    else:
        st.warning("Unsupported file type")


# =========================
# UI
# =========================
st.title("📂 Admin Document Portal")

with st.sidebar:
    st.header("Navigation")

    meeting_files = get_files(MEETINGS_FOLDER)
    selected_meeting = st.selectbox("Meetings", ["None"] + meeting_files)

    report_files = get_files(REPORTS_FOLDER)
    selected_report = st.selectbox("Reports", ["None"] + report_files)

# =========================
# DISPLAY LOGIC
# =========================
if selected_meeting != "None":
    display_file(MEETINGS_FOLDER, selected_meeting)

elif selected_report != "None":
    display_file(REPORTS_FOLDER, selected_report)

else:
    st.info("Select a file from the sidebar")
