from app.services.gmail_service import search_emails
from app.services.ai_service import analyze_email, generate_reply
from app.services.database_service import DatabaseService

from app.config.settings import MAX_EMAILS


class EmailAgent:

    def __init__(self):

        self.database = DatabaseService()

    def run(self):

        emails = search_emails("is:unread")

        emails = emails[:MAX_EMAILS]

        for index, email in enumerate(emails, start=1):

            print("\n" + "=" * 80)
            print(f"EMAIL {index}")
            print("=" * 80)

            print(f"From    : {email.sender}")
            print(f"Subject : {email.subject}")
            print(f"Date    : {email.date}")

            if self.database.analysis_exists(email.gmail_id):

                print("\nLoaded from Database")

                analysis = self.database.get_analysis(
                    email.gmail_id
                )

            else:

                print("\nAnalyzing with Gemini")

                analysis = analyze_email(
                    sender=email.sender,
                    subject=email.subject,
                    body=email.body
                )

                self.database.save_analysis(
                    email,
                    analysis
                )

            print("\nAI ANALYSIS")
            print("-" * 80)

            print(f"Summary  : {analysis.summary}")
            print(f"Category : {analysis.category}")
            print(f"Priority : {analysis.priority}")
            print(f"Action   : {analysis.action}")

        self.database.close()
    
    def generate_reply_for_email(self, email):

        reply = generate_reply(
            sender=email.sender,
            subject=email.subject,
            body=email.body
        )

        return reply

#EmailAgent responsibilities

#It will:

#* Read emails
#* Check database
#* Call Gemini only if needed
#* Save analysis
#* Return results