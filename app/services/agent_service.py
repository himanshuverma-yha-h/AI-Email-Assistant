import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google import genai

from app.config.settings import MODEL_NAME


load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def choose_next_action(
    user_request,
    tools,
    history,
    conversation_history=None
):

    if conversation_history is None:

        conversation_history = []

    india_timezone = ZoneInfo(
        "Asia/Kolkata"
    )

    now = datetime.now(
        india_timezone
    )

    current_date = now.strftime(
        "%Y/%m/%d"
    )

    today_start = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    today_timestamp = int(
        today_start.timestamp()
    )

    prompt = f"""
You are the reasoning engine of an AI Email Assistant.

CURRENT USER REQUEST:

{user_request}

CURRENT DATE:

{current_date}

CURRENT TIMEZONE:

Asia/Kolkata

PREVIOUS CONVERSATION:

{json.dumps(
    conversation_history,
    indent=2,
    ensure_ascii=False
)}

AVAILABLE MCP TOOLS:

{tools}

PREVIOUS ACTION HISTORY:

{json.dumps(
    history,
    indent=2,
    ensure_ascii=False
)}

Your job is to decide the NEXT action.

You may either:

1. Call another tool.
2. Finish and answer the user.

Return ONLY valid JSON.

If another tool is required:

{{
    "action": "tool",
    "tool_name": "tool_name_here",
    "arguments": {{
        "argument_name": "value"
    }}
}}

If the task is complete:

{{
    "action": "finish"
}}

RULES:

1. Use only tools from AVAILABLE MCP TOOLS.
2. Never invent a tool.
3. Carefully inspect PREVIOUS ACTION HISTORY.
4. Do not repeat the same successful tool call with the same arguments.
5. Execute multi-step tasks one action at a time.
6. Use Gmail search syntax when calling search_email.
7. Gmail message IDs must come from previous tool results.
8. Never use an email address as a Gmail message ID.
9. If full email content is required, use get_email_content.
10. If the user asks to analyze an email, get its full content before analysis.
11. If the user asks to draft a reply, get its full content before drafting.
12. If the task is complete, return action finish.
13. Return JSON only.
14. Do not return markdown.
15. Use PREVIOUS CONVERSATION to understand follow-up requests.
16. References such as "it", "that email", "the first one", "the second one", and "that one" may refer to earlier email results.
17. Never invent a Gmail message ID.
18. Resolve earlier email references using PREVIOUS CONVERSATION or PREVIOUS ACTION HISTORY.

EMAIL COMPOSITION RULES:

19. When the user asks to send a new email and provides an idea, message, intent, or informal description instead of a complete email body, write a complete polished email body based on the user's intent.

20. Do not simply copy the user's informal wording into the email body.

21. Preserve the meaning and factual information provided by the user. Do not invent achievements, events, promises, deadlines, relationships, or other facts.

22. Improve grammar, sentence structure, clarity, and professionalism.

23. Infer an appropriate tone from the request. Use a natural professional tone by default unless the user requests a casual, formal, friendly, apologetic, or other specific tone.

24. A generated new email body should normally contain an appropriate opening, a clear main message, and a natural closing.

25. End generated new email bodies with:

Best regards,
Himanshu Verma

unless the user explicitly provides a different signature or asks for no signature.

26. When the user does not provide a subject for a new email, generate a concise and relevant subject based only on the user's intent.

27. When the user provides exact email body text or explicitly asks to send the text exactly as written, preserve that text and do not rewrite it.

28. Before calling send_gmail_email, ensure the body is ready to be shown to the user for confirmation and is suitable to send as an actual email.

DATE AND TIME RANGE RULES:

29. When the user asks for emails "today", interpret "today" as the current calendar date in Asia/Kolkata.

30. When the user asks for emails from the last 24 hours, use newer_than:1d.

31. Do not treat "today" and "last 24 hours" as the same time range.

32. Use the exact CURRENT DATE provided in the prompt. Never invent or estimate the current date.

33. When the user asks for a daily email summary or digest, prefer generate_email_digest instead of repeatedly calling search_email, get_email_content, and analyze_email_content for each email.

34. For a request containing "today", select the appropriate email tool. The application will enforce the exact Asia/Kolkata midnight timestamp before tool execution.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```json"):

        text = text.replace(
            "```json",
            "",
            1
        )

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()

    elif text.startswith("```"):

        text = text.replace(
            "```",
            ""
        )

        text = text.strip()

    try:

        decision = json.loads(text)

    except json.JSONDecodeError:

        return {
            "action": "error",
            "message": (
                "The AI reasoning engine returned "
                "an invalid response."
            )
        }

    if not isinstance(decision, dict):

        return {
            "action": "error",
            "message": (
                "The AI reasoning engine returned "
                "an invalid decision."
            )
        }

    action = decision.get("action")

    normalized_request = user_request.lower()

    today_phrases = {
        "today",
        "today's",
        "todays"
    }

    is_today_request = any(
        phrase in normalized_request
        for phrase in today_phrases
    )

    if (
        action == "tool"
        and decision.get("tool_name") in {
            "generate_email_digest",
            "search_email"
        }
        and is_today_request
    ):

        decision["arguments"] = {
            "query": (
                f"after:{today_timestamp}"
            )
        }

    if action not in {
        "tool",
        "finish"
    }:

        return {
            "action": "error",
            "message": (
                "The AI reasoning engine selected "
                "an invalid action."
            )
        }

    return decision


def generate_agent_response(
    user_request,
    tool_name,
    tool_result
):

    prompt = f"""
You are an AI Email Assistant.

The user asked:

{user_request}

An email assistant operation was completed.

OPERATION CONTEXT:

{tool_name}

RESULT:

{json.dumps(
    tool_result,
    indent=2,
    ensure_ascii=False
)}

Your job is to explain the result to the user clearly.

GENERAL RULES:

1. Answer the user's original request directly.
2. Use only information from RESULT.
3. Do not invent emails, senders, dates, priorities, actions, links, or facts.
4. Do not mention MCP, JSON, APIs, tool calls, or internal implementation.
5. Do not expose Gmail IDs unless the user specifically asks for them.
6. Mention important email subjects and senders when useful.
7. Keep the answer concise but informative.
8. If no emails were found, clearly say so.
9. Return plain text only.

DRAFT REPLY RULES:

10. If OPERATION CONTEXT is draft_email_reply, display the COMPLETE drafted reply text.
11. Never summarize or describe a drafted reply instead of showing its actual text.
12. Clearly label generated reply text as "Draft Reply".

EMAIL DIGEST RULES:

13. If OPERATION CONTEXT is generate_email_digest, treat every object in RESULT as one separate email.

14. Never merge multiple email objects into one numbered item, even when they have the same sender, subject, category, or similar content.

15. The total email count must equal the exact number of email objects in RESULT.

16. Display every email from RESULT exactly once.

17. Preserve the priority ordering already provided in RESULT.

18. For every email, show:
    - Priority
    - Sender
    - Subject
    - Summary

19. You may show the recommended action briefly when useful.

20. Never generate, display, or invent a Draft Reply in an email digest.

21. Never add placeholders such as [Insert Link], [Add Link], or similar text.

22. Do not combine emails into category summaries such as "two emails from the same sender".

23. Number every email individually.

24. If RESULT contains 6 email objects, the final response must contain exactly 6 individually numbered email entries.

25. Do not omit low-priority emails from the digest.

26. Use this structure for each digest email:

1. [Priority] Priority
From: sender
Subject: subject
Summary: summary
Action: action

27. Do not create information that is absent from RESULT.
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        return response.text.strip()

    except Exception:

        return (
            "I completed the email operation, "
            "but I could not generate a final response."
        )