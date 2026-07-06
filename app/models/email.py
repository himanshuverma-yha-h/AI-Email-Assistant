class Email:

    def __init__(
        self,
        gmail_id,
        thread_id,
        message_id,
        sender,
        subject,
        date,
        snippet,
        body
    ):

        self.gmail_id = gmail_id
        self.thread_id = thread_id
        self.message_id = message_id
        self.sender = sender
        self.subject = subject
        self.date = date
        self.snippet = snippet
        self.body = body

    def __str__(self):

        return (
            f"From: {self.sender}\n"
            f"Subject: {self.subject}\n"
            f"Date: {self.date}"
        )