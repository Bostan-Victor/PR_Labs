import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email():
    sender_email = "victorbostan01@gmail.com"
    recipient_email = "victor.bostan@isa.utm.md"
    subject = "Test Email from Python"
    body = "This is a test email sent from a Python SMTP client."

    smtp_server = "smtp.gmail.com"
    smtp_port = 587  

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()

            email_password = "mgsh eexx udee zxnd" 
            server.login(sender_email, email_password)

            server.sendmail(sender_email, recipient_email, message.as_string())
            print("Email sent successfully!")

    except Exception as e:
        print(f"Error: {e}")

send_email()
