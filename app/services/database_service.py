from app.database.database import get_connection
from app.models.analysis import Analysis


class DatabaseService:

    def __init__(self):

        self.connection = get_connection()
        self.cursor = self.connection.cursor()

        self.create_table()

    def create_table(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_analysis(

            gmail_id TEXT PRIMARY KEY,

            sender TEXT,

            subject TEXT,

            date TEXT,

            summary TEXT,

            category TEXT,

            priority TEXT,

            action TEXT
        )
        """)

        self.connection.commit()

    def analysis_exists(self, gmail_id):

        self.cursor.execute(
            "SELECT gmail_id FROM email_analysis WHERE gmail_id=?",
            (gmail_id,)
        )

        return self.cursor.fetchone() is not None

    def save_analysis(self, email, analysis):

        self.cursor.execute(
            """
            INSERT INTO email_analysis
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                email.gmail_id,
                email.sender,
                email.subject,
                email.date,
                analysis.summary,
                analysis.category,
                analysis.priority,
                analysis.action
            )
        )

        self.connection.commit()

    def get_analysis(self, gmail_id):

        self.cursor.execute(
            """
            SELECT summary,
                   category,
                   priority,
                   action
            FROM email_analysis
            WHERE gmail_id=?
            """,
            (gmail_id,)
        )

        row = self.cursor.fetchone()

        if row is None:
            return None

        return Analysis(
            summary=row[0],
            category=row[1],
            priority=row[2],
            action=row[3]
        )

    def close(self):

        self.connection.close()