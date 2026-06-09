# backend/gemini_client.py
"""Simple wrapper for the Gemini API.
Uses GEMINI_API_KEY from .env. Generates an FAQ draft with a detailed step‑by‑step style.
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
HEADERS = {"Content-Type": "application/json"}

def generate_mock_faq(issue_text: str, resolution_text: str) -> dict:
    """Generate a realistic step‑by‑step troubleshooting FAQ locally."""
    from collections import Counter
    # Extract clean terms for a topic title
    words = [w.lower() for w in issue_text.split() if len(w) > 3 and w.lower() not in ['issue', 'ticket', 'problem', 'error', 'with', 'this', 'that', 'please', 'help']]
    top_words = [item[0] for item in Counter(words).most_common(2)]
    topic = " & ".join(top_words).title() if top_words else "System"
    
    question = f"How do I resolve recurring {topic} issues?"
    
    # Structure resolution text into bullet points
    # Clean up the resolution text first
    sentences = [s.strip() for s in resolution_text.replace('\n', ' ').split('.') if len(s.strip()) > 3]
    if not sentences:
        sentences = [resolution_text]
        
    answer = f"To troubleshoot and resolve your {topic.lower()} issue, please follow these step-by-step instructions:\n\n"
    for i, step in enumerate(sentences[:4]):
        step_clean = step[0].upper() + step[1:] if step else ""
        answer += f"{i+1}. **{step_clean}**\n"
    answer += "\n*Note: Ensure all settings are saved. Contact IT support if the problem persists.*"
    
    return {"question": question, "answer": answer}

def generate_faq(issue_text: str, resolution_text: str) -> dict:
    """Send a prompt to Gemini and return a dict with `question` and `answer`.
    Falls back to a high‑quality local rule‑based generation if the API call fails or is unconfigured.
    """
    if not API_KEY or API_KEY.strip() == "" or "your_gemini_api" in API_KEY.lower():
        return generate_mock_faq(issue_text, resolution_text)
        
    prompt = (
        f"""Create a detailed step‑by‑step troubleshooting FAQ.
        Question: {issue_text}
        Answer (include bullet points, checks, and clear guidance): {resolution_text}
        Return a JSON object with fields `question` and `answer`."""
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3},
    }
    params = {"key": API_KEY}
    
    try:
        response = requests.post(BASE_URL, params=params, headers=HEADERS, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        generated = data["candidates"][0]["content"]["parts"][0]["text"]
        try:
            return json.loads(generated)
        except Exception:
            return {"question": "Troubleshooting Guideline", "answer": generated}
    except Exception as e:
        # Graceful fallback on API error, network failure, or rate limits
        return generate_mock_faq(issue_text, resolution_text)

