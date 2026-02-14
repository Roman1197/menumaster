import smtplib
import os
from email.mime.text import MIMEText

class EmailService:
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    @classmethod
    async def send_verification_code(cls, email: str, code: str):
        msg = MIMEText(f"Your MenuMaster verification code is: {code}")
        msg['Subject'] = "Verify your MenuMaster account"
        msg['From'] = cls.SMTP_USER
        msg['To'] = email

        # In a real DevOps environment, we use an async task queue like Celery
        # For now, we'll use a simple SMTP send
        try:
            with smtplib.SMTP(cls.SMTP_SERVER, cls.SMTP_PORT) as server:
                server.starttls()
                server.login(cls.SMTP_USER, cls.SMTP_PASSWORD)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False