import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(recipient_email, subject, message):

    # Email credentials (replace with your own)
    sender_email = "danielkioko1844@gmail.com"
    password = "wxqx bnfg oqfu nmcq"

    # Email content
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email


    #attach html part to message
    msg.attach(MIMEText(message, 'html'))

    # Connect to Gmail's SMTP server using TLS encryption
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        # Login to the server
        server.login(sender_email, password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        
        # Quit the SMTP session
        server.quit()

    print("Email sent successfully!")