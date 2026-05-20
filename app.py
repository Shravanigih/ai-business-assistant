import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import smtplib

from email.mime.text import MIMEText
from datetime import datetime

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="SmartFlow AI CRM Assistant",
    layout="wide"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.stButton>button {
    background-color: #6C63FF;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
}

h1, h2, h3 {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# DATABASE
# =========================================

conn = sqlite3.connect(
    "business_ai.db",
    check_same_thread=False
)

cursor = conn.cursor()

# Leads Table

cursor.execute("""
CREATE TABLE IF NOT EXISTS leads(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    phone TEXT,
    interest TEXT,
    priority TEXT,
    summary TEXT,
    message TEXT
)
""")

# Chat History Table

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_message TEXT,
    ai_response TEXT,
    timestamp TEXT
)
""")

conn.commit()

# =========================================
# EMAIL FUNCTION
# =========================================

def send_email(user_email, user_name):

    sender_email = "YOUR_GMAIL@gmail.com"
    
    sender_password = "YOUR_APP_PASSWORD"

    subject = "Thank You for Contacting SmartFlow AI"

    body = f"""
Hello {user_name},

Thank you for contacting SmartFlow AI CRM Assistant.

Our team will contact you shortly.

Regards,
SmartFlow Team
"""

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = user_email

    try:

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            sender_email,
            sender_password
        )

        server.sendmail(
            sender_email,
            user_email,
            msg.as_string()
        )

        server.quit()

    except Exception as e:

        st.error(e)

# =========================================
# TITLE
# =========================================

st.title("SmartFlow AI CRM Assistant")

st.markdown("""
AI-Powered Business Automation Assistant
""")

# =========================================
# TABS
# =========================================

tab1, tab2, tab3, tab4 = st.tabs([
    "AI Assistant",
    "Lead Manager",
    "Analytics",
    "Dashboard"
])

# =========================================
# TAB 1 - AI ASSISTANT
# =========================================

with tab1:

    st.header("AI Business Assistant")

    user_input = st.text_input(
        "Ask your business query"
    )

    if st.button("Generate AI Response"):

        if user_input:

            with st.spinner(
                "Generating AI response..."
            ):

                ai_reply = f"""
SmartFlow AI Assistant Response:

Thank you for your query regarding:

{user_input}

Our business automation solutions help improve workflow efficiency, lead management, and customer engagement.

Our team will contact you shortly with more details.
"""

                st.success(ai_reply)

                # Save Chat History

                cursor.execute("""
                INSERT INTO chat_history(
                    user_message,
                    ai_response,
                    timestamp
                )
                VALUES(?,?,?)
                """, (
                    user_input,
                    ai_reply,
                    str(datetime.now())
                ))

                conn.commit()

    st.subheader("Recent Chats")

    chat_df = pd.read_sql_query(
        "SELECT * FROM chat_history ORDER BY id DESC LIMIT 5",
        conn
    )

    st.dataframe(chat_df)

# =========================================
# TAB 2 - LEAD MANAGER
# =========================================

with tab2:

    st.header("Lead Capture System")

    name = st.text_input("Name")

    email = st.text_input("Email")

    phone = st.text_input("Phone")

    interest = st.selectbox(
        "Interested In",
        [
            "AI Solutions",
            "Automation",
            "Consulting",
            "Web Development"
        ]
    )

    message = st.text_area("Message")

    if st.button("Submit Lead"):

        # Priority Logic

        if interest == "Consulting":
            priority = "High"

        elif interest == "Automation":
            priority = "Medium"

        else:
            priority = "Low"

        # AI Summary

        lead_summary = f"""
Lead interested in {interest} services.

Customer message:
{message}

Priority Level:
{priority}
"""

        # Save Lead

        cursor.execute("""
        INSERT INTO leads(
            name,
            email,
            phone,
            interest,
            priority,
            summary,
            message
        )
        VALUES(?,?,?,?,?,?,?)
        """, (
            name,
            email,
            phone,
            interest,
            priority,
            lead_summary,
            message
        ))

        conn.commit()

        # Send Email

        send_email(email, name)

        st.success("Lead Submitted Successfully")

        st.info(f"Lead Priority: {priority}")

        st.subheader("AI Lead Summary")

        st.write(lead_summary)

# =========================================
# TAB 3 - ANALYTICS
# =========================================

with tab3:

    st.header("Analytics Dashboard")

    df = pd.read_sql_query(
        "SELECT * FROM leads",
        conn
    )

    if len(df) > 0:

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Leads",
            len(df)
        )

        high_priority = len(
            df[df["priority"] == "High"]
        )

        col2.metric(
            "High Priority Leads",
            high_priority
        )

        total_chats = len(
            pd.read_sql_query(
                "SELECT * FROM chat_history",
                conn
            )
        )

        col3.metric(
            "Total Conversations",
            total_chats
        )

        st.subheader("Interest Distribution")

        fig1 = px.pie(
            df,
            names="interest",
            title="Lead Interests"
        )

        st.plotly_chart(fig1)

        st.subheader("Priority Distribution")

        fig2 = px.bar(
            df,
            x="priority",
            title="Lead Priorities"
        )

        st.plotly_chart(fig2)

    else:

        st.warning("No lead data available.")

# =========================================
# TAB 4 - DASHBOARD
# =========================================

with tab4:

    st.header("Admin Dashboard")

    df = pd.read_sql_query(
        "SELECT * FROM leads ORDER BY id DESC",
        conn
    )

    st.dataframe(df)

    st.download_button(
        label="Download Leads CSV",
        data=df.to_csv(index=False),
        file_name="leads.csv",
        mime="text/csv"
    )

    st.subheader("High Priority Leads")

    high_df = df[df["priority"] == "High"]

    st.dataframe(high_df)

# =========================================
# FOOTER
# =========================================

st.markdown("---")

st.caption(
    "SmartFlow AI CRM Assistant | AI-Powered Business Automation System"
)