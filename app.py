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

    return sorted(os.listdir(folder))


def display_file(folder, file_name):
    file_path = os.path.join(folder, file_name)

    st.subheader(file_name)

    # =========================
    # PDF PREVIEW
    # =========================
    if file_name.lower().endswith(".pdf"):

        with open(file_path, "rb") as f:
            pdf_bytes = f.read()

        st.download_button(
            "⬇ Download PDF",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf"
        )

        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

        pdf_display = f"""
        <iframe
            src="data:application/pdf;base64,{pdf_base64}"
            width="100%"
            height="900"
            type="application/pdf">
        </iframe>
        """

        st.markdown(pdf_display, unsafe_allow_html=True)

    # =========================
    # DOCX PREVIEW
    # =========================
    elif file_name.lower().endswith(".docx"):

        with open(file_path, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value

        with open(file_path, "rb") as f:
            docx_bytes = f.read()

        st.download_button(
            "⬇ Download DOCX",
            data=docx_bytes,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

        st.markdown("### Document Preview")

        st.components.v1.html(
            f"""
            <div style="
                border:1px solid #ddd;
                padding:25px;
                border-radius:10px;
                background-color:white;
                color:black;
                height:800px;
                overflow-y:auto;
            ">
            {html}
            </div>
            """,
            height=850,
            scrolling=True
        )

    # =========================
    # TXT FILES
    # =========================
    elif file_name.lower().endswith(".txt"):

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        st.text_area(
            "Text Preview",
            content,
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

    selected_meeting = st.selectbox(
        "Meetings",
        ["None"] + meeting_files
    )

    report_files = get_files(REPORTS_FOLDER)

    selected_report = st.selectbox(
        "Reports",
        ["None"] + report_files
    )

# =========================
# DISPLAY
# =========================
if selected_meeting != "None":
    display_file(MEETINGS_FOLDER, selected_meeting)

elif selected_report != "None":
    display_file(REPORTS_FOLDER, selected_report)

else:
    st.info("Select a file from the sidebar")
