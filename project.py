import imaplib
import email
from email.header import decode_header
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time  # Import time module for delay
from datetime import datetime

# Email account credentials
username = "lucky28103@gmail.com"
password = "qxgg ybxz bexf zdbx"  # Your app password

def get_today_date():
    # Get today's date in the format required by IMAP (e.g., 12-Feb-2025)
    return datetime.now().strftime("%d-%b-%Y")

def check_new_emails():
    try:
        print("Connecting to IMAP server...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        print("Attempting to log in to Gmail...")
        mail.login(username, password)
        
        # If login is successful, this line will execute
        print(f"Logged in successfully as {username}")
        
        mail.select("inbox")
        
        # Get today's date in the required format
        today_date = get_today_date()
        print(f"Searching for unread emails from today: {today_date}...")
        
        # Combine "UNSEEN" flag with "SINCE" condition for today's date
        status, messages = mail.search(None, f'(UNSEEN SINCE {today_date})')
        
        if status != 'OK':
            print("Error during search.")
            mail.logout()
            return []
        
        email_ids = messages[0].split()
        print(f"Found {len(email_ids)} unread email(s) from today.")  # Print number of unread emails found

        if not email_ids:
            print("No unread emails from today found.")
            mail.logout()
            return []
        
        new_emails = []
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != 'OK':
                print(f"Error fetching email {email_id}.")
                continue
            print(f"Processing email ID: {email_id}")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    
                    # Correct way to extract the body (considering both text and HTML parts)
                    body = None
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                body = part.get_payload(decode=True).decode()  # Decode the body
                                break
                    else:
                        # If it's not multipart, extract the body directly
                        body = msg.get_payload(decode=True).decode()

                    # Only forward if the subject contains "SOA PLACEMENT CELL"
                    if "SOA PLACEMENT CELL" in subject:
                        print(f"Email from {from_} with subject '{subject}' matches. Forwarding...")
                        forward_email(from_, subject, body)
                    
                    new_emails.append({"subject": subject, "from": from_, "body": body})
                    print(f"Unread Email from: {from_} with subject: {subject}")
        
        mail.logout()
        return new_emails
    except Exception as e:
        print(f"Error checking new emails: {e}")
        return []

def forward_email(from_, subject, body):
    # Create the email to forward
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = 'nileshkumarsahoo.19061@gmail.com'
    msg['Subject'] = f"Fwd: {subject}"

    # Add the body to the email
    body_msg = MIMEText(body, 'plain')
    msg.attach(body_msg)

    # Send the email via SMTP
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(username, password)  # Use the app password here
            server.send_message(msg)
        print(f"Forwarded email from {from_} with subject '{subject}' successfully.")
    except Exception as e:
        print(f"Error forwarding email: {e}")

def send_notification(new_emails):
    if not new_emails:
        print("No new emails to notify.")
        return
    
    subject = "New Emails from Specific Senders"
    body = "\n".join(f"From: {email['from']}\nSubject: {email['subject']}\n" for email in new_emails)
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = 'nileshkumarsahoo.19061@gmail.com'
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(username, password)  # Use the app password here
            server.send_message(msg)
        print("Notification sent successfully.")
    except Exception as e:
        print(f"Error sending notification: {e}")

def main():
    print("Starting email check process...")
    while True:
        new_emails = check_new_emails()
        if new_emails:
            print(f"Found {len(new_emails)} new unread email(s) from today.")
            send_notification(new_emails)
        else:
            print("No new unread emails from today. Waiting for next check...")
        time.sleep(10)  # Check every 10 seconds

if __name__ == "__main__":
    main()