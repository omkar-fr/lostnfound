import smtplib
from email.message import EmailMessage
from app.core.config import settings

def send_otp_email(email_to: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "lostnfound: Verification code."
    msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_USERNAME}>"
    msg["To"] = email_to
    
    msg.set_content(f"""
    Hello!
    
    Your verification code is: {otp}
    
    This code will expire in 5 minutes. 
    If you did not request this, please ignore this email.
    """)
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 587) as smtp:
            smtp.login(settings.MAIL_USERNAME , settings.MAIL_PASSWORD )
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False