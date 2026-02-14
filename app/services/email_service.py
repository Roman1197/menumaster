import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

class EmailService:
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    @classmethod
    async def send_verification_email(cls, target_email: str, code: str):
        message = MIMEMultipart()
        
        # הגדרה מפורשת של הקידוד בכותרות
        message["Subject"] = Header("MenuMaster - Verification Code", "utf-8").encode()
        message["From"] = cls.SMTP_USER
        message["To"] = target_email

        body = f"Welcome! Your verification code is: {code}"
        
        # צירוף גוף המייל עם הגדרת utf-8 ברורה
        part = MIMEText(body, "plain", "utf-8")
        message.attach(part)

        try:
            with smtplib.SMTP(cls.SMTP_SERVER, cls.SMTP_PORT) as server:
                server.starttls()
                server.login(cls.SMTP_USER, cls.SMTP_PASSWORD)
                server.send_message(message)
            print(f"INFO: Email sent successfully to {target_email}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to send email: {e}")
            return False