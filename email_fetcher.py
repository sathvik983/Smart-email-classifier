import imaplib
import email
from email.header import decode_header
import datetime
import re

def get_mock_emails():
    """Generates a rich set of realistic mock emails for demonstration."""
    return [
        {
            "id": 1,
            "sender": "Sarah Jenkins <sarah.j@company.com>",
            "subject": "URGENT: Review Q2 Financial Report by 5 PM",
            "body": "Hi team,\n\nWe need to finalize the Q2 financial slides before the board meeting at 5 PM today. Please review the attached sheet and add your comments by 3 PM. This is critical for our budget approval.\n\nThanks,\nSarah Jenkins\nDirector of Finance",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M"),
            "category": "Urgent",
            "priority": "High",
            "read": False
        },
        {
            "id": 2,
            "sender": "David Lee <david.lee@company.com>",
            "subject": "Project Milestone Update & Sync Schedule",
            "body": "Hello everyone,\n\nHere is the latest progress report for Project Apex. We have successfully completed Phase 1. Let's schedule a brief sync tomorrow morning at 10 AM to outline tasks for Phase 2. Please fill in your availability in the shared doc.\n\nBest,\nDavid Lee\nProject Manager",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"),
            "category": "Work",
            "priority": "Medium",
            "read": False
        },
        {
            "id": 3,
            "sender": "Mom <mom@familymail.com>",
            "subject": "Sunday dinner plans?",
            "body": "Hey sweetie, hope you're having a good week!\n\nAre you free for dinner this Sunday? I was thinking of making your favorite lasagna. Let me know if you can make it, and if you want to bring anything.\n\nLove,\nMom",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
            "category": "Personal",
            "priority": "Low",
            "read": True
        },
        {
            "id": 4,
            "sender": "Cloud Services <newsletter@cloud-updates.com>",
            "subject": "Deploy Faster: 50% Off Developer Plans This Week",
            "body": "Unlock ultimate performance!\n\nUpgrade your cloud instances today and save 50% for the first three months. Our new GPU-optimized instances are now live in your region.\n\nClick the link below to upgrade your plan now.\n---\nUnsubscribe from these emails by clicking here.",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
            "category": "Promotions",
            "priority": "Low",
            "read": True
        },
        {
            "id": 5,
            "sender": "Lucky Winner <win-prizes@lottery-winner-online.xyz>",
            "subject": "CONGRATULATIONS!!! You have won $1,000,000 in cash!",
            "body": "Dear customer,\n\nYour email address was selected as the grand prize winner of our international sweepstakes! To claim your $1,000,000 cash prize, please click the link below and enter your banking details.\n\nAct fast before your prize expires!\n\nRegards,\nSweepstakes Claims Office",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M"),
            "category": "Spam",
            "priority": "Low",
            "read": True
        },
        {
            "id": 6,
            "sender": "HR Operations <hr@company.com>",
            "subject": "ACTION REQUIRED: Submit your benefit enrollment choices",
            "body": "Hi all,\n\nJust a reminder that the annual benefits open enrollment period closes this Friday. If you do not submit your choices by then, you will be automatically enrolled in the default medical and dental plans.\n\nPlease log into the HR portal and complete your forms as soon as possible.\n\nHR Operations Team",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M"),
            "category": "Work",
            "priority": "High",
            "read": False
        },
        {
            "id": 7,
            "sender": "Alex Mercer <alex.m@gmail.com>",
            "subject": "Basketball game this Thursday?",
            "body": "Hey,\n\nWe are putting together a game of basketball this Thursday at 7 PM at the local community center court. We need two more players to make full teams. Let me know if you're interested in joining us!\n\nCheers,\nAlex",
            "timestamp": (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M"),
            "category": "Personal",
            "priority": "Low",
            "read": True
        }
    ]

def clean_html(raw_html):
    """Simple regex to remove HTML tags for cleaner text bodies."""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def fetch_imap_emails(email_user, email_pass, imap_server, limit=10):
    """Fetches real emails via IMAP protocol.
    
    Returns a list of email dicts matching the structure of mock emails.
    """
    emails_list = []
    try:
        # Connect to server
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select("inbox")
        
        # Search for all emails
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            return []
            
        mail_ids = messages[0].split()
        total_emails = len(mail_ids)
        
        # Fetch the most recent ones
        start_idx = max(0, total_emails - limit)
        recent_ids = mail_ids[start_idx:][::-1] # reverse to get newest first
        
        for idx, mail_id in enumerate(recent_ids):
            # Fetch message parts
            res, msg_data = mail.fetch(mail_id, "(RFC822)")
            if res != "OK":
                continue
                
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Get Subject
                    subject, encoding = decode_header(msg["Subject"] or "")[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")
                        
                    # Get Sender
                    sender, encoding = decode_header(msg["From"] or "")[0]
                    if isinstance(sender, bytes):
                        sender = sender.decode(encoding or "utf-8", errors="ignore")
                        
                    # Get Date
                    date_str = msg["Date"]
                    # Format date string
                    try:
                        parsed_date = email.utils.parsedate_to_datetime(date_str)
                        formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        formatted_date = date_str or "Unknown Date"
                        
                    # Get Body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    break
                                except Exception:
                                    pass
                            elif content_type == "text/html" and not body:
                                try:
                                    html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                    body = clean_html(html_body)
                                except Exception:
                                    pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                        except Exception:
                            body = str(msg.get_payload())
                            
                    # Clean up body whitespace
                    body = body.strip()
                    if len(body) > 5000:
                        body = body[:5000] + "\n...[truncated]"
                        
                    emails_list.append({
                        "id": idx + 100, # Offset ID to distinguish from mock data
                        "sender": sender,
                        "subject": subject,
                        "body": body or "[No text body found]",
                        "timestamp": formatted_date,
                        "category": "Unclassified",
                        "priority": "Medium",
                        "read": False
                    })
        mail.close()
        mail.logout()
    except Exception as e:
        raise Exception(f"IMAP Error: {str(e)}")
        
    return emails_list
