import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = "tim.daecher@outlook.com"
sender_password = "hsnnpmxuqalnhcwe"
recipient_email = "ottowidl@gmail.com"
smtp_server = "smtp-mail.outlook.com"
smtp_port = 587

msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = recipient_email
msg['Subject'] = "Test Email with Tracking Pixel"

html = """\
<!DOCTYPE html>
<html>
<body>
    <p>Hi there,</p>
    <p>This email contains a tracking pixel.</p>
    <!-- Tracking Pixel -->
    <img src="https://email-tracker-8794.onrender.com/track" width="1" height="1" alt="">
    <p>Regards,<br>Your Team</p>
</body>
</html>
"""

msg.attach(MIMEText(html, 'html'))

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Secure the connection
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error sending email: {e}")
finally:
    server.quit()