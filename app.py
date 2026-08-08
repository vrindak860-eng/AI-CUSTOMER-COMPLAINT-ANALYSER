import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Customer Complaint Analyzer",
    page_icon="📋",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: #0B0B0B;
}

.block-container {
    background: #161616;
    padding: 2rem;
    margin-top: 20px;
    border-radius: 18px;
    border: 1px solid #2A2A2A;
    box-shadow: 0px 10px 35px rgba(0,0,0,0.55);
}

section[data-testid="stSidebar"] {
    background: #111111;
    border-right: 1px solid #2B2B2B;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

html, body, [class*="css"] {
    color: white;
}

h1 {
    color: #FFFFFF;
    text-align: center;
    font-weight: 700;
}

h2, h3 {
    color: #4EA8FF;
}

p {
    color: #D1D5DB;
}

li {
    color: #D1D5DB;
}

div.stButton > button {
    background: #2563EB;
    color: white;
    font-size: 18px;
    font-weight: bold;
    border-radius: 10px;
    height: 48px;
    width: 100%;
    border: none;
}

div.stButton > button:hover {
    background: #1D4ED8;
    color: white;
}

.stTextInput input {
    background: #222222;
    color: white;
    border: 1px solid #444444;
    border-radius: 8px;
}

[data-testid="stFileUploader"] {
    background: #1C1C1C;
    border: 1px dashed #555;
    border-radius: 10px;
    padding: 15px;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

label {
    color: white !important;
}

hr {
    border-color: #333333;
}

.metric-box {
    padding: 15px;
    background: #202020;
    border: 1px solid #333333;
    border-radius: 10px;
    text-align: center;
    font-size: 18px;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# HEADER
# =========================================================

st.title("📋 AI Customer Complaint Analyzer")

st.markdown("""
This application uses **Google Gemini AI** to automatically analyze
customer complaints.

### Features

- 📂 Upload Complaint CSV
- 🤖 AI Complaint Categorization
- 🚨 Priority Detection
- 💬 AI Suggested Reply
- 📊 Analytics Dashboard
- 📈 Interactive Charts
- 📥 Download Results
""")


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("⚙ Settings")

st.sidebar.info("""
### Steps

1. Enter Gemini API Key
2. Upload CSV
3. Click Analyze
4. Download Results
""")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    placeholder="Enter your Gemini API key"
)


# =========================================================
# CREATE GEMINI CLIENT
# =========================================================

client = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        st.sidebar.success("Gemini API connected")
    except Exception as e:
        st.sidebar.error("Could not connect to Gemini API.")


# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📂 Upload Complaint CSV",
    type=["csv"]
)


# =========================================================
# SAMPLE FORMAT
# =========================================================

with st.expander("📄 Expected CSV Format"):

    sample = pd.DataFrame({
        "Complaint": [
            "My order has not arrived.",
            "Refund has not been processed.",
            "The product is damaged.",
            "Payment failed but money deducted."
        ]
    })

    st.dataframe(
        sample,
        use_container_width=True
    )


# =========================================================
# AI COMPLAINT ANALYSIS FUNCTION
# =========================================================

def analyze_complaint(text):

    prompt = f"""
You are an AI Customer Support Assistant.

Analyze the customer complaint below.

You MUST return exactly these three lines:

Category: [category]
Priority: [priority]
Reply: [professional reply]

Use ONLY one of these categories:

Delivery
Refund
Payment
Product Quality
Technical Issue
Customer Service
Account
Other

Use ONLY one of these priorities:

High
Medium
Low

Complaint:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    result = response.text.strip()

    category = "Other"
    priority = "Medium"
    reply = "Unable to generate reply."

    lines = result.split("\n")

    for line in lines:

        line = line.strip()

        if line.lower().startswith("category:"):
            category = line.split(":", 1)[1].strip()

        elif line.lower().startswith("priority:"):
            priority = line.split(":", 1)[1].strip()

        elif line.lower().startswith("reply:"):
            reply = line.split(":", 1)[1].strip()

    return category, priority, reply


# =========================================================
# PROCESS UPLOADED FILE
# =========================================================

if uploaded_file is not None:

    # -----------------------------------------------------
    # API KEY CHECK
    # -----------------------------------------------------

    if not api_key:

        st.warning(
            "⚠️ Please enter your Gemini API Key in the sidebar."
        )

        st.stop()


    # -----------------------------------------------------
    # READ CSV
    # -----------------------------------------------------

    try:

        df = pd.read_csv(uploaded_file)

    except Exception as e:

        st.error(
            f"Unable to read the CSV file: {e}"
        )

        st.stop()


    # -----------------------------------------------------
    # CHECK COMPLAINT COLUMN
    # -----------------------------------------------------

    if "Complaint" not in df.columns:

        st.error(
            "❌ CSV must contain a column named 'Complaint'."
        )

        st.info("""
        Example:

        | Complaint |
        |-----------|
        | My order has not arrived |
        | I need a refund |
        | Payment failed |
        """)

        st.stop()


    # -----------------------------------------------------
    # DISPLAY ORIGINAL DATA
    # -----------------------------------------------------

    st.subheader("📂 Uploaded Complaints")

    st.dataframe(
        df,
        use_container_width=True
    )


    # -----------------------------------------------------
    # ANALYZE BUTTON
    # -----------------------------------------------------

    analyze = st.button(
        "🚀 Analyze Complaints"
    )


    # =====================================================
    # START AI PROCESSING
    # =====================================================

    if analyze:

        categories = []
        priorities = []
        replies = []

        total = len(df)

        progress = st.progress(0)

        status = st.empty()

        for i, complaint in enumerate(df["Complaint"]):

            status.info(
                f"🤖 Analyzing complaint {i + 1} of {total}..."
            )

            try:

                category, priority, reply = analyze_complaint(
                    str(complaint)
                )

            except Exception as e:

                category = "Error"
                priority = "Error"

                reply = (
                    "AI analysis failed: "
                    + str(e)
                )

            categories.append(category)
            priorities.append(priority)
            replies.append(reply)

            progress.progress(
                (i + 1) / total
            )


        status.success(
            "✅ Complaint analysis completed!"
        )


        # -------------------------------------------------
        # ADD AI RESULTS TO DATAFRAME
        # -------------------------------------------------

        df["Category"] = categories
        df["Priority"] = priorities
        df["Suggested Reply"] = replies


        # =================================================
        # ANALYSIS RESULTS
        # =================================================

        st.markdown("---")

        st.header("📊 Complaint Analysis Results")

        st.dataframe(
            df,
            use_container_width=True
        )


        # =================================================
        # SUMMARY METRICS
        # =================================================

        st.markdown("---")

        st.header("📌 Summary")

        total_complaints = len(df)

        high_priority = (
            df["Priority"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("high")
            .sum()
        )

        medium_priority = (
            df["Priority"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("medium")
            .sum()
        )

        low_priority = (
            df["Priority"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("low")
            .sum()
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Complaints",
                total_complaints
            )

        with col2:

            st.metric(
                "High Priority",
                high_priority
            )

        with col3:

            st.metric(
                "Medium Priority",
                medium_priority
            )

        with col4:

            st.metric(
                "Low Priority",
                low_priority
            )


        # =================================================
        # ANALYTICS
        # =================================================

        st.markdown("---")

        st.header("📈 Analytics Dashboard")


        col1, col2 = st.columns(2)


        # =================================================
        # CATEGORY CHART
        # =================================================

        with col1:

            category_count = (
                df["Category"]
                .value_counts()
                .reset_index()
            )

            category_count.columns = [
                "Category",
                "Count"
            ]

            fig_category = px.bar(
                category_count,
                x="Category",
                y="Count",
                color="Category",
                title="Complaint Categories"
            )

            st.plotly_chart(
                fig_category,
                use_container_width=True
            )


        # =================================================
        # PRIORITY CHART
        # =================================================

        with col2:

            priority_count = (
                df["Priority"]
                .value_counts()
                .reset_index()
            )

            priority_count.columns = [
                "Priority",
                "Count"
            ]

            fig_priority = px.pie(
                priority_count,
                names="Priority",
                values="Count",
                title="Priority Distribution"
            )

            st.plotly_chart(
                fig_priority,
                use_container_width=True
            )


        # =================================================
        # PRIORITY BAR CHART
        # =================================================

        st.subheader("🚨 Priority Analysis")

        priority_bar = (
            df["Priority"]
            .value_counts()
            .reset_index()
        )

        priority_bar.columns = [
            "Priority",
            "Count"
        ]

        fig_priority_bar = px.bar(
            priority_bar,
            x="Priority",
            y="Count",
            color="Priority",
            title="High / Medium / Low Priority Complaints"
        )

        st.plotly_chart(
            fig_priority_bar,
            use_container_width=True
        )


        # =================================================
        # CATEGORY TABLE
        # =================================================

        st.subheader("📋 Category Summary")

        category_summary = (
            df["Category"]
            .value_counts()
            .reset_index()
        )

        category_summary.columns = [
            "Category",
            "Number of Complaints"
        ]

        st.dataframe(
            category_summary,
            use_container_width=True
        )


        # =================================================
        # DOWNLOAD RESULTS
        # =================================================

        st.markdown("---")

        st.header("📥 Download Results")

        csv_data = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download Analyzed CSV",
            data=csv_data,
            file_name="Complaint_Analysis.csv",
            mime="text/csv"
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
<div style="text-align:center; color:#888;">
AI Customer Complaint Analyzer | Built using Python,
Streamlit, Gemini AI, Pandas & Plotly
</div>
""",
    unsafe_allow_html=True
)
