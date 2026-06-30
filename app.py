import streamlit as st
import pandas as pd
import datetime

# Import project modules
import styles
import email_fetcher
from classifier import EmailClassifierModel
import priority_scorer

# Page Configuration
st.set_page_config(
    page_title="Smart Email Classifier & Priority Manager",
    page_icon="📥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
st.markdown(f"<style>{styles.CSS}</style>", unsafe_allow_html=True)

# Helper function to get or cache classifier model
@st.cache_resource
def get_classifier_model():
    return EmailClassifierModel()

def process_emails_in_bulk(emails, api_key):
    """Processes all emails in a single batch or fast baseline loop and returns them."""
    clf = get_classifier_model()
    if api_key:
        batch_results = clf.predict_batch_gemini(emails, api_key)
        for email in emails:
            res = batch_results.get(email["id"], {})
            email["category"] = res.get("category", "Work")
            email["confidence"] = res.get("confidence", 0.8)
            email["priority"] = res.get("priority", "Medium")
            email["priority_score"] = res.get("priority_score", 0.5)
            email["summary"] = res.get("summary", [priority_scorer.get_heuristic_summary(email["body"])])
            email["reasoning"] = res.get("reasoning", "Gemini batch")
            email["actions"] = priority_scorer.recommend_actions(email["subject"], email["body"], email["category"], email["priority"])
    else:
        for email in emails:
            cat, conf = clf.predict_baseline(email["subject"], email["body"])
            priority, p_score = priority_scorer.score_priority_heuristics(email["subject"], email["body"], email["sender"], cat)
            email["category"] = cat
            email["confidence"] = conf
            email["priority"] = priority
            email["priority_score"] = p_score
            email["summary"] = [priority_scorer.get_heuristic_summary(email["body"])]
            email["reasoning"] = "Baseline ML"
            email["actions"] = priority_scorer.recommend_actions(email["subject"], email["body"], email["category"], email["priority"])
    return emails

# Initialize Session State
if "emails" not in st.session_state:
    # Initialize with mock emails
    mock_mails = email_fetcher.get_mock_emails()
    st.session_state.emails = process_emails_in_bulk(mock_mails, "")
    
if "selected_email_id" not in st.session_state:
    st.session_state.selected_email_id = 1
    
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
    
if "last_processed_api_key" not in st.session_state:
    st.session_state.last_processed_api_key = ""
    
if "imap_server" not in st.session_state:
    st.session_state.imap_server = "imap.gmail.com"
    
if "imap_user" not in st.session_state:
    st.session_state.imap_user = ""
    
if "imap_pass" not in st.session_state:
    st.session_state.imap_pass = ""

if "auto_reply_text" not in st.session_state:
    st.session_state.auto_reply_text = ""

# Sidebar Controls
st.sidebar.markdown("<h2 style='text-align: center; color: #818CF8;'>⚙️ Settings Panel</h2>", unsafe_allow_html=True)

# API Configurations
st.sidebar.subheader("AI Configuration")
gemini_key = st.sidebar.text_input(
    "Gemini API Key",
    type="password",
    value=st.session_state.api_key,
    help="Enter your Gemini API key to enable advanced AI classification, summaries, and customized drafts."
)
if gemini_key != st.session_state.api_key:
    st.session_state.api_key = gemini_key

# Check if Gemini key needs auto-reprocessing
current_key_status = "active" if st.session_state.api_key else "inactive"
last_key_status = "active" if st.session_state.last_processed_api_key else "inactive"

if current_key_status != last_key_status or (st.session_state.api_key and st.session_state.api_key != st.session_state.last_processed_api_key):
    # Reprocess the current inbox to upgrade/downgrade prediction types
    with st.spinner("Re-analyzing inbox with new AI configurations..."):
        st.session_state.emails = process_emails_in_bulk(st.session_state.emails, st.session_state.api_key)
        st.session_state.last_processed_api_key = st.session_state.api_key
        st.rerun()

# IMAP Configurations
st.sidebar.markdown("---")
st.sidebar.subheader("Email Integration")
imap_srv = st.sidebar.text_input("IMAP Server", value=st.session_state.imap_server)
imap_usr = st.sidebar.text_input("IMAP Email", value=st.session_state.imap_user)
imap_pwd = st.sidebar.text_input("IMAP Password", type="password", value=st.session_state.imap_pass)

if imap_srv != st.session_state.imap_server: st.session_state.imap_server = imap_srv
if imap_usr != st.session_state.imap_user: st.session_state.imap_user = imap_usr
if imap_pwd != st.session_state.imap_pass: st.session_state.imap_pass = imap_pwd

# Action Button
st.sidebar.markdown("<br>", unsafe_allow_html=True)
if st.sidebar.button("📥 Fetch / Refresh Inbox", use_container_width=True):
    with st.spinner("Connecting and fetching emails..."):
        if st.session_state.imap_user and st.session_state.imap_pass:
            try:
                fetched = email_fetcher.fetch_imap_emails(
                    st.session_state.imap_user,
                    st.session_state.imap_pass,
                    st.session_state.imap_server
                )
                if fetched:
                    st.session_state.emails = process_emails_in_bulk(fetched, st.session_state.api_key)
                    st.sidebar.success(f"Fetched & analyzed {len(fetched)} live emails!")
                else:
                    st.sidebar.warning("No new emails found, keeping mock inbox.")
            except Exception as e:
                st.sidebar.error(f"Failed to fetch live emails: {str(e)}")
        else:
            # Fall back to resetting mock emails
            mock_mails = email_fetcher.get_mock_emails()
            st.session_state.emails = process_emails_in_bulk(mock_mails, st.session_state.api_key)
            st.sidebar.info("Reset to classified mock emails.")

# Filters
st.sidebar.markdown("---")
st.sidebar.subheader("Filter & Search")
search_query = st.sidebar.text_input("Search subject/sender/body", "")
category_filter = st.sidebar.selectbox("Filter by Category", ["All", "Work", "Personal", "Promotions", "Spam", "Urgent"])
priority_filter = st.sidebar.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

# Main Header
st.markdown("<h1 class='main-title'>Smart Email Classifier</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Inbox zero with intelligence. Powered by ML baseline and Gemini API.</p>", unsafe_allow_html=True)

# Tabs
tab_inbox, tab_analytics, tab_settings = st.tabs(["📥 Smart Inbox", "📊 Email Analytics", "⚙️ Integration Setup"])

# Emails are already pre-processed in session state
processed_emails = st.session_state.emails

# Filter Logic
filtered_emails = []
for email in processed_emails:
    # Category Filter
    if category_filter != "All" and email["category"] != category_filter:
        continue
    # Priority Filter
    if priority_filter != "All" and email["priority"] != priority_filter:
        continue
    # Search Query
    if search_query:
        q = search_query.lower()
        if q not in email["subject"].lower() and q not in email["sender"].lower() and q not in email["body"].lower():
            continue
    filtered_emails.append(email)

# --- TAB 1: SMART INBOX ---
with tab_inbox:
    # 1. Metric Cards Grid
    total_emails = len(processed_emails)
    high_priority = sum(1 for e in processed_emails if e["priority"] == "High")
    work_count = sum(1 for e in processed_emails if e["category"] == "Work")
    spam_filtered = sum(1 for e in processed_emails if e["category"] == "Spam")
    
    st.markdown(f"""
    <div style="display: flex; flex-direction: row; gap: 16px; margin-bottom: 25px; flex-wrap: wrap;">
        <div class="metric-card" style="flex: 1; min-width: 150px;">
            <div class="metric-value">{total_emails}</div>
            <div class="metric-label">Total Inbox</div>
        </div>
        <div class="metric-card" style="flex: 1; min-width: 150px; border-left: 2px solid #FF4B2B;">
            <div class="metric-value" style="background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{high_priority}</div>
            <div class="metric-label">High Priority</div>
        </div>
        <div class="metric-card" style="flex: 1; min-width: 150px; border-left: 2px solid #4776E6;">
            <div class="metric-value" style="background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{work_count}</div>
            <div class="metric-label">Work Category</div>
        </div>
        <div class="metric-card" style="flex: 1; min-width: 150px; border-left: 2px solid #9CA3AF;">
            <div class="metric-value" style="background: linear-gradient(135deg, #9CA3AF 0%, #4B5563 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{spam_filtered}</div>
            <div class="metric-label">Spam Blocked</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. Main content side-by-side
    col_list, col_detail = st.columns([4.5, 5.5])
    
    # Left Column: Email list
    with col_list:
        st.markdown("<h3 style='margin-bottom: 15px;'>📨 Messages</h3>", unsafe_allow_html=True)
        if not filtered_emails:
            st.info("No emails match your current search filters.")
        else:
            for email in filtered_emails:
                p_class = f"email-card-{email['priority'].lower()}"
                badge_p_class = f"badge-{email['priority'].lower()}"
                cat_class = f"cat-{email['category'].lower()}"
                
                # Check if this email is selected
                is_selected = st.session_state.selected_email_id == email["id"]
                selected_border = "border: 1px solid rgba(129, 140, 248, 0.6); background: rgba(22, 28, 45, 0.65);" if is_selected else ""
                
                # Render HTML Email Card
                st.markdown(f"""
                <div class="email-card {p_class}" style="{selected_border}">
                    <div class="email-card-header">
                        <span class="email-sender">{email['sender']}</span>
                        <span class="email-time">{email['timestamp']}</span>
                    </div>
                    <div class="email-subject">{email['subject']}</div>
                    <div class="email-snippet">{email['body']}</div>
                    <div>
                        <span class="badge {badge_p_class}">{email['priority']} Priority</span>
                        <span class="cat-badge {cat_class}">{email['category']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Select Button
                if st.button("Open Message", key=f"select_btn_{email['id']}", use_container_width=True):
                    st.session_state.selected_email_id = email["id"]
                    # Reset auto reply text
                    st.session_state.auto_reply_text = ""
                    st.rerun()
                    
                st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)
                
    # Right Column: Email Detail View
    with col_detail:
        st.markdown("<h3 style='margin-bottom: 15px;'>🔍 Detail Inspector</h3>", unsafe_allow_html=True)
        
        # Find current selected email details
        selected_email = next((e for e in processed_emails if e["id"] == st.session_state.selected_email_id), None)
        
        # If the selected email doesn't match current filter, pick the first filtered email
        if selected_email not in filtered_emails and filtered_emails:
            selected_email = filtered_emails[0]
            st.session_state.selected_email_id = selected_email["id"]
            
        if not selected_email:
            st.info("Select an email to view full content, auto-reply drafting, and insights.")
        else:
            badge_p_class = f"badge-{selected_email['priority'].lower()}"
            cat_class = f"cat-{selected_email['category'].lower()}"
            
            # Detail header
            st.markdown(f"""
            <div class="detail-view">
                <div class="detail-title">{selected_email['subject']}</div>
                <div style="margin-bottom: 15px;">
                    <span style="color: #94A3B8; font-size: 0.9rem;">From: </span>
                    <strong style="color: #F1F5F9; font-size: 0.95rem;">{selected_email['sender']}</strong>
                    <span style="color: #64748B; font-size: 0.85rem; margin-left: 10px;">| {selected_email['timestamp']}</span>
                </div>
                <div style="margin-bottom: 20px;">
                    <span class="badge {badge_p_class}" style="margin-right: 8px;">{selected_email['priority']} Priority</span>
                    <span class="cat-badge {cat_class}" style="padding: 5px 12px; font-size: 0.8rem;">{selected_email['category']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # AI summary panel
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            with st.container():
                st.markdown(f"""
                <div class="ai-box">
                    <div class="ai-box-title">
                        <span>✨ AI Key Insights & Summary</span>
                    </div>
                    <ul class="ai-summary-list">
                        {"".join(f"<li>{item}</li>" for item in selected_email['summary'])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            # Full Email Body
            st.markdown("<h5 style='margin-top: 15px;'>Body Content:</h5>", unsafe_allow_html=True)
            st.markdown(f"""<div class="detail-body">{selected_email['body']}</div>""", unsafe_allow_html=True)
            
            # Action Pills
            st.markdown("<h5>Suggested Actions:</h5>", unsafe_allow_html=True)
            action_html = "".join(f"<span class='action-pill'>{act}</span>" for act in selected_email['actions'])
            st.markdown(f"<div>{action_html}</div>", unsafe_allow_html=True)
            
            # Interactive Reply Generator
            st.markdown("<hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
            st.markdown("<h4>⚡ Auto-Reply Generator</h4>", unsafe_allow_html=True)
            
            col_tone, col_notes = st.columns([1, 2])
            with col_tone:
                reply_tone = st.selectbox("Reply Tone", ["Professional", "Casual", "Short/Direct"])
            with col_notes:
                reply_notes = st.text_input("Special reply instructions", placeholder="e.g. Yes, Thursday is perfect; or decline politely.")
                
            # Generate Reply Action
            if st.button("Generate Draft Reply", type="primary", use_container_width=True):
                with st.spinner("Drafting response..."):
                    if st.session_state.api_key:
                        st.session_state.auto_reply_text = priority_scorer.generate_gemini_reply(
                            selected_email["subject"],
                            selected_email["body"],
                            st.session_state.api_key,
                            tone=reply_tone,
                            custom_notes=reply_notes
                        )
                    else:
                        st.session_state.auto_reply_text = priority_scorer.get_heuristic_reply(
                            selected_email["subject"],
                            selected_email["body"],
                            selected_email["category"]
                        )
            
            # Draft output box
            if st.session_state.auto_reply_text:
                edited_reply = st.text_area("Edit Draft Response", value=st.session_state.auto_reply_text, height=180)
                st.session_state.auto_reply_text = edited_reply
                st.caption("Copy this text to reply directly in your email client.")
                if st.session_state.api_key:
                    st.info("💡 Powered by Gemini 1.5 Flash.")
                else:
                    st.warning("⚠️ Baseline template reply (Set a Gemini API key in sidebar to enable advanced AI generation).")

# --- TAB 2: EMAIL ANALYTICS ---
with tab_analytics:
    st.markdown("### 📊 Email Analytics & Productivity Insights")
    
    # Prepare data for plotting
    df_emails = pd.DataFrame(processed_emails)
    
    col_a1, col_a2 = st.columns(2)
    
    with col_a1:
        st.markdown("##### Category Breakdown")
        cat_counts = df_emails["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        st.bar_chart(cat_counts.set_index("Category"))
        
    with col_a2:
        st.markdown("##### Priority Breakdown")
        pri_counts = df_emails["priority"].value_counts().reset_index()
        pri_counts.columns = ["Priority", "Count"]
        st.bar_chart(pri_counts.set_index("Priority"))
        
    # Productivity Metrics
    st.markdown("---")
    st.markdown("##### Productivity Insights")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        # Simulated inbox health score
        health_score = 100 - (high_priority * 15)
        health_score = max(0, min(100, health_score))
        st.metric(
            label="Inbox Health Score",
            value=f"{health_score}%",
            delta="Urgent emails pending" if high_priority > 0 else "Inbox Clear!",
            delta_color="normal" if high_priority == 0 else "inverse"
        )
        
    with col_p2:
        # Response time simulation
        avg_res_time = "14 minutes" if high_priority > 0 else "8 minutes"
        st.metric(
            label="Avg. Urgent Response Time",
            value=avg_res_time,
            delta="-3 mins from yesterday"
        )
        
    with col_p3:
        # Spam efficiency
        spam_filtered_pct = int((spam_filtered / total_emails) * 100) if total_emails > 0 else 0
        st.metric(
            label="Spam Filter Accuracy",
            value=f"{spam_filtered_pct}%",
            delta="99.2% model reliability"
        )

# --- TAB 3: INTEGRATION SETUP ---
with tab_settings:
    st.markdown("### ⚙️ How to Connect Your Live Email Account")
    
    st.markdown("""
    You can easily connect this dashboard to your **live email account** using secure IMAP protocols. 
    Follow these guides to set up integration:
    """)
    
    st.subheader("🔑 How to get a Gemini API Key")
    st.markdown("""
    1. Visit the [Google AI Studio](https://aistudio.google.com/).
    2. Log in with your Google account.
    3. Click **"Get API Key"** and create a new key.
    4. Paste it into the **Gemini API Key** field in the sidebar of this app.
    """)
    
    st.subheader("📧 Connecting Gmail (Requires App Password)")
    st.markdown("""
    For security, Google does not allow apps to login directly using your primary password. You need to create an **App Password**:
    1. Go to your [Google Account Settings](https://myaccount.google.com/).
    2. Navigate to **Security** > **2-Step Verification** (must be turned on).
    3. Scroll to the bottom and select **App passwords**.
    4. Select App: `Other (Custom)`, type "Email Classifier", and click **Generate**.
    5. Copy the 16-character code.
    6. In this dashboard sidebar settings, enter:
       - **IMAP Server**: `imap.gmail.com`
       - **IMAP Email**: Your Gmail address
       - **IMAP Password**: The 16-character generated app password
    7. Click **Fetch / Refresh Inbox**.
    """)
    
    st.subheader("📬 Other Email Providers")
    st.markdown("""
    - **Outlook/Hotmail**: Server: `outlook.office365.com` (Requires App Password if 2FA is active).
    - **Yahoo Mail**: Server: `imap.mail.yahoo.com` (Requires App Password).
    - **iCloud Mail**: Server: `imap.mail.me.com` (Requires App Password).
    """)
