import streamlit as st
import pandas as pd

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="Monthly Appraisal System",
    layout="wide"
)

# ======================================================
# STYLE
# ======================================================
st.markdown("""
<style>
.stApp {
    background-color: white;
}

h1, h2, h3 {
    color: #1f2937;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Monthly Appraisal System")

st.write("Upload employee KPI CSV file for automatic appraisal scoring.")

# ======================================================
# KPI TARGETS & WEIGHTS
# ======================================================
kpi_targets = {
    "Lead Generation": 100,
    "Client Acquisition": 10,
    "Revenue Growth": 5000000,
    "Client Conversion": 30,
    "Pipeline Management": 10000000,
    "Proposal Success": 40,
    "Client Retention": 90,
    "Customer Relationship": 5,
    "Business Expansion": 2,
    "Reporting & Compliance": 100,
    "Team Collaboration": 100,
    "Professional Conduct": 100
}

kpi_weights = {
    "Lead Generation": 10,
    "Client Acquisition": 10,
    "Revenue Growth": 15,
    "Client Conversion": 10,
    "Pipeline Management": 10,
    "Proposal Success": 10,
    "Client Retention": 10,
    "Customer Relationship": 5,
    "Business Expansion": 5,
    "Reporting & Compliance": 5,
    "Team Collaboration": 5,
    "Professional Conduct": 5
}

# ======================================================
# FILE UPLOAD
# ======================================================
uploaded_file = st.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    # ==================================================
    # SCORE CALCULATION
    # ==================================================
    total_scores = []

    for index, row in df.iterrows():

        total_score = 0

        for kpi in kpi_targets.keys():

            actual = row[kpi]
            target = kpi_targets[kpi]
            weight = kpi_weights[kpi]

            achievement = (actual / target) * 100

            # Maximum score cap = 100%
            achievement = min(achievement, 100)

            weighted_score = (
                achievement * weight
            ) / 100

            total_score += weighted_score

        total_scores.append(round(total_score, 2))

    df["Final Score (%)"] = total_scores

    # ==================================================
    # PERFORMANCE RATING
    # ==================================================
    def performance_rating(score):
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Very Good"
        elif score >= 60:
            return "Good"
        elif score >= 50:
            return "Average"
        else:
            return "Poor"

    df["Performance Rating"] = df[
        "Final Score (%)"
    ].apply(performance_rating)

    # ==================================================
    # DISPLAY RESULTS
    # ==================================================
    st.subheader("Monthly Appraisal Results")

    st.dataframe(
        df,
        use_container_width=True
    )

    # ==================================================
    # DOWNLOAD RESULT
    # ==================================================
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download Appraisal Report",
        data=csv,
        file_name="monthly_appraisal_results.csv",
        mime="text/csv"
    )
