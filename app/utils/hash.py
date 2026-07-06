import hashlib


def generate_email_id(sender, subject, date):

    text = sender + subject + date

    return hashlib.sha256(
        text.encode()
    ).hexdigest()