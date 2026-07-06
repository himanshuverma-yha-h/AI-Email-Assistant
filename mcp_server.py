from fastmcp import FastMCP

from app.services.gmail_service import (
    search_emails,
    mark_email_as_read,
    archive_email,
    send_email,
    get_email_by_id,
    reply_to_email
)
from app.services.ai_service import analyze_email, generate_reply


mcp = FastMCP(
    name="AI Email Assistant"
)


@mcp.tool
def search_email(query: str) -> list[dict]:
    """
    Search Gmail using a Gmail search query.

    Examples:
    is:unread
    from:google
    subject:internship
    newer_than:7d
    """

    emails = search_emails(query)

    results = []

    for email in emails:

        results.append(
            {
                "gmail_id": email.gmail_id,
                "sender": email.sender,
                "subject": email.subject,
                "date": email.date,
                "snippet": email.snippet
            }
        )

    return results

@mcp.tool
def get_email_content(gmail_id: str) -> dict:
    """
    Get the full content of a Gmail message.

    Requires a Gmail message ID.
    """

    email = get_email_by_id(gmail_id)

    return {
        "gmail_id": email.gmail_id,
        "sender": email.sender,
        "subject": email.subject,
        "date": email.date,
        "snippet": email.snippet,
        "body": email.body
    }

@mcp.tool
def analyze_email_content(
    sender: str,
    subject: str,
    body: str
) -> dict:
    """
    Analyze an email using AI.

    Returns:
    summary
    category
    priority
    action
    """

    analysis = analyze_email(
        sender=sender,
        subject=subject,
        body=body
    )

    return {
        "summary": analysis.summary,
        "category": analysis.category,
        "priority": analysis.priority,
        "action": analysis.action
    }

@mcp.tool
def draft_email_reply(
    sender: str,
    subject: str,
    body: str
) -> str:
    """
    Generate an AI draft reply for an email.

    This tool only creates a draft.
    It does not send the email.
    """

    reply = generate_reply(
        sender=sender,
        subject=subject,
        body=body
    )

    return reply

@mcp.tool
def mark_as_read(gmail_id: str) -> dict:
    """
    Mark a Gmail message as read.

    Requires the Gmail message ID.
    """

    mark_email_as_read(gmail_id)

    return {
        "success": True,
        "gmail_id": gmail_id,
        "message": "Email marked as read."
    }


@mcp.tool
def archive_gmail_email(gmail_id: str) -> dict:
    """
    Archive a Gmail message.

    Requires the Gmail message ID.
    """

    archive_email(gmail_id)

    return {
        "success": True,
        "gmail_id": gmail_id,
        "message": "Email archived successfully."
    }

@mcp.tool
def send_gmail_email(
    to: str,
    subject: str,
    body: str
) -> dict:
    """
    Send a new Gmail email.

    This tool performs a Gmail write action.
    Confirmation must be handled by the client before execution.
    """

    gmail_id = send_email(
        to=to,
        subject=subject,
        body=body
    )

    return {
        "success": True,
        "sent": True,
        "gmail_id": gmail_id,
        "message": "Email sent successfully."
    }

@mcp.tool
def reply_to_gmail_email(
    gmail_id: str,
    reply_body: str
) -> dict:
    """
    Reply to an existing Gmail email in the same conversation thread.

    This tool performs a Gmail write action.
    Confirmation must be handled by the client before execution.
    """

    email = get_email_by_id(gmail_id)

    sent_id = reply_to_email(
        email=email,
        reply_body=reply_body
    )

    return {
        "success": True,
        "sent": True,
        "gmail_id": sent_id,
        "thread_id": email.thread_id,
        "message": (
            "Reply sent successfully "
            "in the existing Gmail thread."
        )
    }

if __name__ == "__main__":
    mcp.run()