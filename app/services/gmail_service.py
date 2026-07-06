import base64
from email.message import EmailMessage

from app.auth.gmail_auth import authenticate_gmail
from app.models.email import Email



def _decode_body(data):

    if not data:
        return ""

    try:

        return base64.urlsafe_b64decode(
            data.encode("utf-8")
        ).decode(
            "utf-8",
            errors="replace"
        )

    except Exception:

        return ""


def _extract_body(payload):

    body = ""

    parts = payload.get("parts", [])

    for part in parts:

        mime_type = part.get("mimeType", "")

        if mime_type == "text/plain":

            data = part.get(
                "body",
                {}
            ).get(
                "data"
            )

            body = _decode_body(data)

            if body:
                return body


        nested_parts = part.get(
            "parts",
            []
        )

        if nested_parts:

            nested_payload = {
                "parts": nested_parts
            }

            body = _extract_body(
                nested_payload
            )

            if body:
                return body


    data = payload.get(
        "body",
        {}
    ).get(
        "data"
    )

    return _decode_body(data)


def _get_header(headers, header_name, default_value):

    for header in headers:

        if (
            header.get("name", "").lower()
            == header_name.lower()
        ):

            return header.get(
                "value",
                default_value
            )

    return default_value


def _parse_email(msg):

    gmail_id = msg.get(
        "id",
        ""
    )

    thread_id = msg.get(
        "threadId",
        ""
    )

    payload = msg.get(
        "payload",
        {}
    )

    headers = payload.get(
        "headers",
        []
    )

    sender = _get_header(
        headers,
        "From",
        "Unknown"
    )

    subject = _get_header(
        headers,
        "Subject",
        "No Subject"
    )

    date = _get_header(
        headers,
        "Date",
        "Unknown"
    )

    message_id = _get_header(
        headers,
        "Message-ID",
        ""
    )

    snippet = msg.get(
        "snippet",
        "No Snippet"
    )

    body = _extract_body(
        payload
    )

    return Email(
        gmail_id=gmail_id,
        thread_id=thread_id,
        message_id=message_id,
        sender=sender,
        subject=subject,
        date=date,
        snippet=snippet,
        body=body
    )


def _fetch_emails(query=None):

    service = authenticate_gmail()

    request_arguments = {
        "userId": "me",
        "maxResults": 10
    }

    if query is not None:

        request_arguments["q"] = query


    results = service.users().messages().list(
        **request_arguments
    ).execute()


    messages = results.get(
        "messages",
        []
    )

    emails = []


    for message in messages:

        msg = service.users().messages().get(
            userId="me",
            id=message["id"],
            format="full"
        ).execute()

        email = _parse_email(
            msg
        )

        emails.append(
            email
        )


    return emails


def read_latest_emails():

    return _fetch_emails()


def search_emails(query):

    return _fetch_emails(
        query
    )


def get_email_by_id(gmail_id):

    service = authenticate_gmail()

    msg = service.users().messages().get(
        userId="me",
        id=gmail_id,
        format="full"
    ).execute()

    return _parse_email(
        msg
    )


def mark_email_as_read(gmail_id):

    service = authenticate_gmail()

    service.users().messages().modify(
        userId="me",
        id=gmail_id,
        body={
            "removeLabelIds": [
                "UNREAD"
            ]
        }
    ).execute()

    return True


def archive_email(gmail_id):

    service = authenticate_gmail()

    service.users().messages().modify(
        userId="me",
        id=gmail_id,
        body={
            "removeLabelIds": [
                "INBOX"
            ]
        }
    ).execute()

    return True


def send_email(
    to,
    subject,
    body
):

    service = authenticate_gmail()

    message = EmailMessage()

    message.set_content(
        body
    )

    message["To"] = to

    message["Subject"] = subject


    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()


    send_message = {
        "raw": encoded_message
    }


    result = service.users().messages().send(
        userId="me",
        body=send_message
    ).execute()


    return result["id"]


def reply_to_email(
    email,
    reply_body
):

    service = authenticate_gmail()

    message = EmailMessage()

    message.set_content(
        reply_body
    )

    message["To"] = email.sender


    if email.subject.lower().startswith(
        "re:"
    ):

        message["Subject"] = email.subject

    else:

        message["Subject"] = (
            f"Re: {email.subject}"
        )


    if email.message_id:

        message["In-Reply-To"] = (
            email.message_id
        )

        message["References"] = (
            email.message_id
        )


    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()


    send_message = {
        "raw": encoded_message,
        "threadId": email.thread_id
    }


    result = service.users().messages().send(
        userId="me",
        body=send_message
    ).execute()


    return result["id"]