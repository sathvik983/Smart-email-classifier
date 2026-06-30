# Custom styles for the Smart Email Classifier & Priority Manager

CSS = """
/* Import premium typography */
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #080B10;
    color: #E2E8F0;
}

/* Custom background for the whole app */
.stApp {
    background: radial-gradient(circle at 50% 0%, #151A26 0%, #080B10 100%);
}

/* Hide standard Streamlit header/footer */
header {visibility: hidden;}
footer {visibility: hidden;}

/* Custom Glassmorphism Card for Emails */
.email-card {
    background: rgba(22, 28, 45, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 16px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.email-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: transparent;
    transition: background 0.3s ease;
}

.email-card-high::before {
    background: linear-gradient(180deg, #FF416C, #FF4B2B);
}

.email-card-medium::before {
    background: linear-gradient(180deg, #F7971E, #FFD200);
}

.email-card-low::before {
    background: linear-gradient(180deg, #11998E, #38EF7D);
}

.email-card:hover {
    transform: translateY(-3px);
    border-color: rgba(255, 255, 255, 0.15);
    background: rgba(22, 28, 45, 0.6);
    box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
}

.email-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.email-sender {
    font-weight: 600;
    color: #F8FAFC;
    font-size: 1.05rem;
}

.email-time {
    font-size: 0.8rem;
    color: #94A3B8;
}

.email-subject {
    font-size: 1.15rem;
    font-weight: 500;
    color: #E2E8F0;
    margin-bottom: 8px;
}

.email-snippet {
    font-size: 0.9rem;
    color: #94A3B8;
    line-height: 1.5;
    margin-bottom: 12px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

/* Custom Badges */
.badge {
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    display: inline-block;
}

.badge-high {
    background: linear-gradient(135deg, rgba(255, 65, 108, 0.2) 0%, rgba(255, 75, 43, 0.2) 100%);
    color: #FF6B6B;
    border: 1px solid rgba(255, 65, 108, 0.4);
}

.badge-medium {
    background: linear-gradient(135deg, rgba(247, 151, 30, 0.2) 0%, rgba(255, 210, 0, 0.2) 100%);
    color: #FFD200;
    border: 1px solid rgba(247, 151, 30, 0.4);
}

.badge-low {
    background: linear-gradient(135deg, rgba(17, 153, 142, 0.2) 0%, rgba(56, 239, 125, 0.2) 100%);
    color: #4EFE8E;
    border: 1px solid rgba(17, 153, 142, 0.4);
}

/* Category Badges */
.cat-badge {
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 500;
    margin-right: 6px;
    display: inline-block;
}

.cat-work {
    background-color: rgba(71, 118, 230, 0.15);
    color: #60A5FA;
    border: 1px solid rgba(71, 118, 230, 0.3);
}

.cat-personal {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.cat-promotions {
    background-color: rgba(167, 139, 250, 0.15);
    color: #A78BFA;
    border: 1px solid rgba(167, 139, 250, 0.3);
}

.cat-spam {
    background-color: rgba(156, 163, 175, 0.15);
    color: #9CA3AF;
    border: 1px solid rgba(156, 163, 175, 0.3);
}

.cat-urgent {
    background-color: rgba(239, 68, 68, 0.15);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Analytics Metric Tile */
.metric-card {
    background: rgba(30, 41, 59, 0.3);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    transition: border-color 0.3s ease;
}

.metric-card:hover {
    border-color: rgba(255, 255, 255, 0.1);
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #FFFFFF 0%, #A5B4FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 4px;
}

.metric-label {
    font-size: 0.8rem;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Detail View glassmorphism block */
.detail-view {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 28px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    margin-top: 10px;
}

.detail-title {
    font-size: 1.6rem;
    font-weight: 700;
    color: #F8FAFC;
    line-height: 1.3;
    margin-bottom: 16px;
    background: linear-gradient(90deg, #FFFFFF 0%, #CBD5E1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.detail-body {
    background: rgba(15, 23, 42, 0.4);
    border-radius: 10px;
    padding: 18px;
    border: 1px solid rgba(255, 255, 255, 0.03);
    color: #E2E8F0;
    font-size: 0.95rem;
    line-height: 1.6;
    white-space: pre-wrap;
    margin: 20px 0;
}

.ai-box {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}

.ai-box-title {
    font-weight: 600;
    color: #C084FC;
    font-size: 0.95rem;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.ai-summary-list {
    margin: 0;
    padding-left: 20px;
    color: #CBD5E1;
    font-size: 0.9rem;
}

.ai-summary-list li {
    margin-bottom: 6px;
}

/* Quick Action Suggestion Buttons */
.action-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #CBD5E1;
    margin-right: 8px;
    margin-bottom: 8px;
    transition: all 0.2s ease;
}

.action-pill:hover {
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(255, 255, 255, 0.2);
    color: #FFFFFF;
}

/* Sidebar Custom Styling */
section[data-testid="stSidebar"] {
    background-color: #0B0E14 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

div[data-testid="stSidebarCollapseButton"] {
    background-color: #0B0E14;
}

/* Main title styling */
.main-title {
    font-weight: 800;
    font-size: 2.5rem;
    background: linear-gradient(135deg, #FFFFFF 0%, #818CF8 50%, #C084FC 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
    letter-spacing: -0.02em;
}

.subtitle {
    font-size: 1.1rem;
    color: #94A3B8;
    margin-bottom: 30px;
    font-weight: 350;
}
"""
