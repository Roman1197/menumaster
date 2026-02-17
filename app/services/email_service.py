import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from jinja2 import Environment, FileSystemLoader

class EmailService:
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

    # הגדרת Jinja2 לטעינת קבצים מתיקיית templates
    # השתמש בנתיב יחסי למיקום הקובץ הנוכחי
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))

    @classmethod
    async def send_verification_email(cls, target_email: str, code: str):
        # טעינת התבנית לפי שם הקובץ
        template = cls.env.get_template("verify_email.html")
        
        # "הזרקת" המשתנים לתוך ה-HTML
        html_content = template.render(code=code)

        message = MIMEMultipart()
        message["Subject"] = Header("MenuMaster - Your Verification Code", "utf-8").encode()
        message["From"] = cls.SMTP_USER
        message["To"] = target_email
        message.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            with smtplib.SMTP(cls.SMTP_SERVER, cls.SMTP_PORT) as server:
                server.starttls()
                server.login(cls.SMTP_USER, cls.SMTP_PASSWORD)
                server.send_message(message)
            print(f"INFO: Beautiful HTML email sent to {target_email}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to send email: {e}")
            return False
            
    @classmethod
    async def send_welcome_email(cls, target_email: str, username: str):
        try:
            # טעינת התבנית החדשה
            template = cls.env.get_template("welcome_verified.html")
            html_content = template.render(username=username)

            message = MIMEMultipart()
            message["Subject"] = Header("Welcome to MenuMaster!", "utf-8").encode()
            message["From"] = cls.SMTP_USER
            message["To"] = target_email
            message.attach(MIMEText(html_content, "html", "utf-8"))

            with smtplib.SMTP(cls.SMTP_SERVER, cls.SMTP_PORT) as server:
                server.starttls()
                server.login(cls.SMTP_USER, cls.SMTP_PASSWORD)
                server.send_message(message)
            return True
        except Exception as e:
            print(f"ERROR: Failed to send welcome email: {e}")
            return False