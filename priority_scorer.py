import google.generativeai as genai
import json

HIGH_PRIORITY_KEYWORDS = ["urgent", "deadline", "immediate", "asap", "critical", "outage", "security", "action required", "emergency", "board meeting"]
MEDIUM_PRIORITY_KEYWORDS = ["schedule", "sync", "meeting", "review", "status", "milestone", "update", "feedback"]

def score_priority_heuristics(subject, body, sender, category):
    """Assigns priority (High, Medium, Low) and score based on rule heuristics."""
    combined_text = f"{subject} {body}".lower()
    
    # Base priority from category
    if category == "Urgent":
        base_score = 0.9
        priority = "High"
    elif category == "Work":
        base_score = 0.6
        priority = "Medium"
    elif category == "Personal":
        base_score = 0.4
        priority = "Low"
    elif category == "Promotions":
        base_score = 0.2
        priority = "Low"
    else: # Spam
        base_score = 0.05
        priority = "Low"
        
    # Boost based on keyword matching
    matches_high = sum(1 for kw in HIGH_PRIORITY_KEYWORDS if kw in combined_text)
    matches_med = sum(1 for kw in MEDIUM_PRIORITY_KEYWORDS if kw in combined_text)
    
    score = base_score + (matches_high * 0.15) + (matches_med * 0.05)
    score = min(max(score, 0.0), 1.0) # Clamp score between 0 and 1
    
    # Resolve final label
    if score >= 0.75:
        priority = "High"
    elif score >= 0.45:
        priority = "Medium"
    else:
        priority = "Low"
        
    return priority, score

def recommend_actions(subject, body, category, priority):
    """Recommends a list of actions based on category and content."""
    combined_text = f"{subject} {body}".lower()
    actions = []
    
    if category == "Spam":
        return ["Mark as Spam", "Block Sender", "Archive"]
        
    if category == "Promotions":
        return ["Archive", "Unsubscribe", "Star Offer"]
        
    # Urgent and Work items
    if priority == "High":
        actions.append("Reply Now")
    
    # Check if a meeting is mentioned
    if any(k in combined_text for k in ["meet", "sync", "schedule", "call", "zoom", "calendar"]):
        actions.append("Schedule Meeting")
        
    # Check if a document needs review
    if any(k in combined_text for k in ["review", "check", "edit", "comment", "feedback"]):
        actions.append("Add to Task List")
        
    # Default work & personal actions
    if category == "Work" and "Reply Now" not in actions:
        actions.append("Send Quick Reply")
    elif category == "Personal":
        actions.append("Reply Later")
        
    actions.append("Archive")
    return actions

def get_heuristic_summary(body):
    """Generate a baseline summary by grabbing the first 2 sentences."""
    # Strip whitespace and break into sentences
    cleaned = body.strip().replace("\n", " ")
    sentences = [s.strip() for s in cleaned.split(".") if s.strip()]
    if len(sentences) <= 2:
        return body
    return ". ".join(sentences[:2]) + "."

def get_heuristic_reply(subject, body, category, sender_name="there"):
    """Generates a template-based reply draft."""
    if category == "Urgent":
        return f"Hi,\n\nThanks for reaching out. I have received your urgent message regarding '{subject}' and am looking into it right now. I will follow up with you as soon as possible.\n\nBest regards,"
    elif category == "Work":
        return f"Hi,\n\nThanks for the email. I've received your note about '{subject}' and have added it to my queue. I will review the details and get back to you with updates shortly.\n\nBest,"
    elif category == "Personal":
        return f"Hi,\n\nThanks for writing! It was great to hear from you. Regarding '{subject}', I'll check my schedule and get back to you soon!\n\nCheers,"
    elif category == "Promotions":
        return f"Hello,\n\nThank you for sharing this offer. I will review the details and reach out if we have any interest.\n\nBest,"
    else:
        return "No reply recommended for spam emails."

# --- Gemini API Integrations ---

def get_gemini_priority_and_summary(subject, body, api_key):
    """Uses Gemini to get structured priority score and a bullet-point summary."""
    if not api_key:
        # Fall back to heuristics
        p_label, p_score = score_priority_heuristics(subject, body, "", "Work")
        summary = get_heuristic_summary(body)
        return p_label, p_score, [summary]
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are an intelligent email analyzer. Review the following email details:
        Subject: {subject}
        Body: {body}
        
        Tasks:
        1. Determine priority level ("High", "Medium", "Low") and assign a numeric score between 0.0 (unimportant) and 1.0 (extremely critical).
        2. Provide a 2-3 bullet point summary of the email's key points.
        
        Format your response as a valid JSON object with the exact keys:
        "priority": string ("High", "Medium", "Low")
        "priority_score": float (0.0 to 1.0)
        "summary": array of strings (the bullet points)
        """
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        data = json.loads(response.text.strip())
        priority = data.get("priority", "Medium")
        score = float(data.get("priority_score", 0.5))
        summary = data.get("summary", [get_heuristic_summary(body)])
        
        if priority not in ["High", "Medium", "Low"]:
            priority = "Medium"
            
        return priority, score, summary
        
    except Exception as e:
        # Fallback on error
        p_label, p_score = score_priority_heuristics(subject, body, "", "Work")
        summary = [f"Failed to generate summary via Gemini: {str(e)}", get_heuristic_summary(body)]
        return p_label, p_score, summary

def generate_gemini_reply(subject, body, api_key, tone="Professional", custom_notes=""):
    """Uses Gemini to generate a tailored auto-reply draft."""
    if not api_key:
        return get_heuristic_reply(subject, body, "Work")
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        notes_prompt = f"Additional instructions from user: {custom_notes}" if custom_notes else ""
        
        prompt = f"""
        Write a draft reply to the following email.
        Subject: {subject}
        Body: {body}
        
        Tone requested: {tone}
        {notes_prompt}
        
        Write ONLY the email body response. Keep it concise, natural, and draft-ready. Do not write markdown blocks or subject headers, just the plain text of the email message.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"Error drafting reply: {str(e)}\n\nFallback draft:\n{get_heuristic_reply(subject, body, 'Work')}"
