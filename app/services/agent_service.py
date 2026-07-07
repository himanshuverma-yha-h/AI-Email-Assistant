import os
import json

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

    prompt = f"""
You are the reasoning engine of an AI Email Assistant.

CURRENT USER REQUEST:

{user_request}

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

RULES:

1. Answer the user's original request directly.
2. Use only information from the result.
3. Do not invent emails, senders, dates, priorities, or actions.
4. Do not mention MCP, JSON, APIs, tool calls, or internal implementation.
5. Do not expose Gmail IDs unless the user specifically asks for them.
6. Summarize large email lists instead of dumping raw data.
7. Mention important email subjects and senders when useful.
8. Keep the answer concise but informative.
9. If no emails were found, clearly say so.
10. If a draft email reply was generated, display the COMPLETE drafted reply text.
11. Never summarize or describe a drafted reply instead of showing its actual text.
12. Clearly label generated reply text as "Draft Reply".
13. Return plain text only.
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