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
    if not os.path.exists(folder):
        st.warning(f"{folder} folder not found")
        return []

    return sorted([
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
    ])


def read_file_once(file_path):
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None


def display_file(folder, file_name):
    file_path = os.path.join(folder, file_name)

    if not os.path.exists(file_path):
        st.error("File not found")
        return

    st.subheader(f"📄 {file_name}")

    file_bytes = read_file_once(file_path)
    if file_bytes is None:
        return

    st.download_button(
        label="⬇ Download File",
        data=file_bytes,
        file_name=file_name,
        mime="application/octet-stream"
    )

    if file_name.lower().endswith(".pdf"):
        base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
        st.markdown(f"""
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="900px"
            style="border:none;">
        </iframe>
        """, unsafe_allow_html=True)

    elif file_name.lower().endswith(".docx"):
        try:
            docx_file = BytesIO(file_bytes)
            result = mammoth.convert_to_html(docx_file)
            html = result.value

            st.components.v1.html(
                f"""
                <div style="background:white;padding:20px;border-radius:10px;height:850px;overflow:auto;color:black;border:1px solid #ddd;">
                    {html}
                </div>
                """,
                height=900,
                scrolling=True
            )
        except Exception as e:
            st.error(f"Error displaying Word document: {e}")

    elif file_name.lower().endswith((".xlsx", ".xls", ".csv")):
        try:
            if file_name.lower().endswith(".csv"):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Error reading spreadsheet: {e}")

    elif file_name.lower().endswith(".txt"):
        try:
            text_content = file_bytes.decode("utf-8")
            st.text_area("Preview", text_content, height=500)
        except Exception as e:
            st.error(f"Error reading text file: {e}")

    else:
        st.warning("Unsupported file type")


def searchable_selectbox(label, options):
    search = st.text_input(f"🔍 Search {label}")

    if search:
        filtered = [o for o in options if search.lower() in o.lower()]
    else:
        filtered = options

    return st.selectbox(label, ["None"] + filtered)


# =========================
# MAIN UI & SIDEBAR NAVIGATION
# =========================
st.title("📂 Admin Document Portal")

with st.sidebar:
    st.header("Navigation")
    # Choose which section you want to operate in
    app_mode = st.radio("Go to:", ["Meetings", "Reports", "Stock", "Consumables"])
    
    st.markdown("---")

# =========================
# INDEPENDENT FUNCTIONAL MODES
# =========================

if app_mode == "Meetings":
    with st.sidebar:
        meeting_files = get_files(FOLDERS["Meetings"])
        selected_meeting = st.selectbox("Meetings", ["None"] + meeting_files)
    
    if selected_meeting != "None":
        display_file(FOLDERS["Meetings"], selected_meeting)
    else:
        st.info("Select a meeting document from the sidebar to view.")

elif app_mode == "Reports":
    with st.sidebar:
        report_files = get_files(FOLDERS["Reports"])
        selected_report = st.selectbox("Reports", ["None"] + report_files)
    
    if selected_report != "None":
        display_file(FOLDERS["Reports"], selected_report)
    else:
        st.info("Select a report document from the sidebar to view.")

elif app_mode == "Stock":
    with st.sidebar:
        stock_files = get_files(FOLDERS["Stock"])
        selected_stock = searchable_selectbox("Stock Records", stock_files)
    
    # If a file is selected, display it at the top
    if selected_stock != "None":
        display_file(FOLDERS["Stock"], selected_stock)
        st.markdown("---")
        
    # The Stock Movement Register features ONLY render here
    st.subheader("📦 Stock/Furniture Movement Register")

    register_file = os.path.join(FOLDERS["Stock"], "stock_movement_register.csv")

    if not os.path.exists(register_file):
        pd.DataFrame(columns=[
            "Date", "Item Name", "Quantity", "From Office", "To Office", "Moved By", "Reason"
        ]).to_csv(register_file, index=False)

    with st.expander("➕ Add Stock Movement"):
        with st.form("movement_form"):
            date = st.date_input("Date")
            item = st.text_input("Item Name")
            qty = st.number_input("Quantity", min_value=1, step=1)
            from_office = st.text_input("From Office")
            to_office = st.text_input("To Office")
            moved_by = st.text_input("Moved By")
            reason = st.text_area("Reason")

            submit = st.form_submit_button("Save Movement")

            if submit:
                if item and from_office and to_office:
                    new_data = pd.DataFrame([{
                        "Date": date,
                        "Item Name": item,
                        "Quantity": qty,
                        "From Office": from_office,
                        "To Office": to_office,
                        "Moved By": moved_by,
                        "Reason": reason
                    }])

                    df = pd.read_csv(register_file)
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv(register_file, index=False)

                    st.success("Movement saved successfully!")
                else:
                    st.error("Please fill required fields")

    st.subheader("📋 Movement History")

    try:
        df = pd.read_csv(register_file)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download Register",
            csv,
            "stock_movement_register.csv",
            "text/csv"
        )
    except Exception as e:
        st.error(f"Error loading register: {e}")

elif app_mode == "Consumables":
    with st.sidebar:
        consumable_files = get_files(FOLDERS["Consumables"])
        selected_consumable = searchable_selectbox("Consumables", consumable_files)
    
    if selected_consumable != "None":
        display_file(FOLDERS["Consumables"], selected_consumable)
    else:
        st.info("Select a consumable record document from the sidebar to view.")
