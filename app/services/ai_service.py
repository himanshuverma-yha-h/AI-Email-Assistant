import os
import json
from app.prompts.reply_prompt import EMAIL_REPLY_PROMPT
from dotenv import load_dotenv
from google import genai

from app.prompts.email_prompt import EMAIL_ANALYSIS_PROMPT
from app.models.analysis import Analysis
from app.config.settings import MODEL_NAME

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def analyze_email(sender, subject, body):

    prompt = EMAIL_ANALYSIS_PROMPT.format(
        sender=sender,
        subject=subject,
        body=body
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "").replace("```", "").strip()

    elif text.startswith("```"):
        text = text.replace("```", "").replace("```", "").strip()

    data = json.loads(text)

    analysis = Analysis(
        summary=data["summary"],
        category=data["category"],
        priority=data["priority"],
        action=data["action"]
    )

    return analysis

def generate_reply(
    sender,
    subject,
    body
):

    from app.config.settings import (
        USER_NAME,
        USER_EMAIL_SIGNATURE
    )

    prompt = f"""
You are an AI email reply assistant.

USER NAME:

{USER_NAME}

EMAIL SENDER:

{sender}

EMAIL SUBJECT:

{subject}

EMAIL BODY:

{body}

Generate a professional email reply for the user.

RULES:

1. Write the reply as if it is being sent by {USER_NAME}.
2. Respond directly to the email content.
3. Do not invent facts, promises, meetings, payments, or completed actions.
4. Keep the reply concise and professional.
5. Do not include a Subject line.
6. Do not use placeholders such as [Your Name], [Name], or [Signature].
7. End the email with exactly this signature:

{USER_EMAIL_SIGNATURE}

8. Return only the complete email reply.
9. Do not explain the reply.
10. Do not use markdown.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text.strip()