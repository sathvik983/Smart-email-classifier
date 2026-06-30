import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import google.generativeai as genai
import json

# Synthetic training data for the baseline classifier
TRAINING_DATA = [
    # Urgent
    ("URGENT: Review Q2 Financial Report by 5 PM", "Urgent"),
    ("System down! Outage on production server", "Urgent"),
    ("CRITICAL: Server crash, customer database inaccessible", "Urgent"),
    ("Emergency meeting at 2 PM - all hands required", "Urgent"),
    ("Immediate action needed: Security breach detected", "Urgent"),
    ("Deadline reminder: Submit expenses before midnight tonight", "Urgent"),
    
    # Work
    ("Project Milestone Update & Sync Schedule", "Work"),
    ("Weekly team status report - Monday sync", "Work"),
    ("Please review the design document for the new dashboard", "Work"),
    ("Feedback on client presentation slides", "Work"),
    ("Code review requested for pull request #452", "Work"),
    ("Discussion on budget allocations for Q3", "Work"),
    ("Notes from the onboarding session this morning", "Work"),
    
    # Personal
    ("Sunday dinner plans?", "Personal"),
    ("Family reunion photos from last weekend", "Personal"),
    ("Dinner this Friday night at 7pm?", "Personal"),
    ("Birthday party invitation for Sophia next Saturday", "Personal"),
    ("Hey! How is your new job going? Let's catch up", "Personal"),
    ("Recipe for the chocolate cookies you liked", "Personal"),
    ("Road trip plan details for July 4th", "Personal"),
    
    # Promotions
    ("Deploy Faster: 50% Off Developer Plans This Week", "Promotions"),
    ("Flash Sale: 24 Hours Only! Get 30% discount on all items", "Promotions"),
    ("Free webinar: Introduction to Machine Learning in Python", "Promotions"),
    ("Upgrade your subscription to Premium and save $50", "Promotions"),
    ("Weekly Newsletter: Tech trends and career advice", "Promotions"),
    ("Special offer just for you: Get free shipping on next purchase", "Promotions"),
    
    # Spam
    ("CONGRATULATIONS!!! You have won $1,000,000 in cash!", "Spam"),
    ("Double your income in 5 days! Click to invest now!", "Spam"),
    ("Cheap Rolex watches online - lowest prices guaranteed", "Spam"),
    ("Claim your long-lost inheritance from the royal family", "Spam"),
    ("Earn money working from home - no experience required!", "Spam"),
    ("Urgent: Your bank account is locked, click here to unlock it", "Spam")
]

class EmailClassifierModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        self.model = MultinomialNB()
        self.is_trained = False
        self.train_baseline()

    def train_baseline(self):
        """Trains the Naive Bayes baseline model on synthetic data."""
        try:
            texts = [item[0] for item in TRAINING_DATA]
            labels = [item[1] for item in TRAINING_DATA]
            
            X = self.vectorizer.fit_transform(texts)
            self.model.fit(X, labels)
            self.is_trained = True
        except Exception as e:
            print(f"Error training baseline model: {e}")

    def predict_baseline(self, subject, body):
        """Classifies an email using the baseline TF-IDF model."""
        if not self.is_trained:
            return "Work", 0.5
            
        combined_text = f"{subject} {body}"
        X_test = self.vectorizer.transform([combined_text])
        prediction = self.model.predict(X_test)[0]
        
        # Calculate approximate confidence (probability)
        probs = self.model.predict_proba(X_test)[0]
        class_idx = list(self.model.classes_).index(prediction)
        confidence = probs[class_idx]
        
        return str(prediction), float(confidence)

    def predict_gemini(self, subject, body, api_key):
        """Classifies an email using the Gemini API.
        
        Falls back to baseline if the API call fails or key is missing.
        """
        if not api_key:
            return self.predict_baseline(subject, body)
            
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            You are an expert email assistant. Analyze the email subject and body below and classify it into EXACTLY one of these categories:
            - Work
            - Personal
            - Promotions
            - Spam
            - Urgent
            
            Format your response as a valid JSON object with the following keys:
            "category": string (one of the five categories above)
            "confidence": float (between 0.0 and 1.0)
            "reasoning": string (brief 1-sentence reason for classification)

            Email Subject: {subject}
            Email Body: {body}
            """
            
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text.strip())
            category = data.get("category", "Work")
            confidence = float(data.get("confidence", 0.8))
            
            # Basic validation of returned category
            valid_categories = ["Work", "Personal", "Promotions", "Spam", "Urgent"]
            if category not in valid_categories:
                category = "Work"
                
            return category, confidence, data.get("reasoning", "Gemini zero-shot classification")
            
        except Exception as e:
            # Fall back to baseline classification on API error
            category, confidence = self.predict_baseline(subject, body)
            return category, confidence, f"Gemini error (falling back to baseline): {str(e)}"

    def predict_batch_gemini(self, emails, api_key):
        """Classifies, prioritizes, and summarizes a list of emails in one single API request.
        
        Falls back to offline models and heuristics if api_key is missing or API call fails.
        """
        if not api_key:
            results = {}
            for email in emails:
                cat, conf = self.predict_baseline(email["subject"], email["body"])
                results[email["id"]] = {
                    "category": cat,
                    "confidence": conf,
                    "reasoning": "Baseline offline classifier"
                }
            return results
            
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Sub-sample email details to stay within token constraints
            emails_input = []
            for email in emails:
                emails_input.append({
                    "id": email["id"],
                    "subject": email["subject"],
                    "body": email["body"][:600] # Snippet is enough for classification & summary
                })
                
            prompt = f"""
            You are an expert email assistant. Analyze the following list of emails.
            
            For each email:
            1. Classify it into exactly one category: Work, Personal, Promotions, Spam, Urgent.
            2. Determine priority level ("High", "Medium", "Low") and assign a numeric score between 0.0 and 1.0.
            3. Generate a 2-3 item bulleted list summarizing key points.
            
            Format your response as a valid JSON object with the exact key "results" containing an array of objects.
            Each object in the array must contain:
            "id": integer (matching the email ID)
            "category": string (exactly "Work", "Personal", "Promotions", "Spam", or "Urgent")
            "confidence": float (between 0.0 and 1.0)
            "priority": string (exactly "High", "Medium", or "Low")
            "priority_score": float (between 0.0 and 1.0)
            "summary": array of strings (the bullet points)
            "reasoning": string (brief reason)
            
            Emails:
            {json.dumps(emails_input, indent=2)}
            """
            
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            data = json.loads(response.text.strip())
            results = {}
            for res in data.get("results", []):
                results[res["id"]] = {
                    "category": res.get("category", "Work"),
                    "confidence": float(res.get("confidence", 0.8)),
                    "priority": res.get("priority", "Medium"),
                    "priority_score": float(res.get("priority_score", 0.5)),
                    "summary": res.get("summary", ["Email processed successfully."]),
                    "reasoning": res.get("reasoning", "Gemini batch classification")
                }
                
            # Backfill any missing IDs
            for email in emails:
                if email["id"] not in results:
                    cat, conf = self.predict_baseline(email["subject"], email["body"])
                    results[email["id"]] = {
                        "category": cat,
                        "confidence": conf,
                        "reasoning": "Missing from Gemini batch response"
                    }
                    
            return results
            
        except Exception as e:
            # Fall back to baseline
            results = {}
            for email in emails:
                cat, conf = self.predict_baseline(email["subject"], email["body"])
                results[email["id"]] = {
                    "category": cat,
                    "confidence": conf,
                    "reasoning": f"Batch API Error (fallback): {str(e)}"
                }
            return results

