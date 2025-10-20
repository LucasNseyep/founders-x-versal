import smtplib
import ssl
from email.message import EmailMessage

# --- CONFIGURATION ---
# IMPORTANT: Fill in these details for the script to work.
#
# 1. SENDER_EMAIL: The email address you want to send emails FROM.
# 2. APP_PASSWORD: The special 16-character "App Password" you generate from your
#    Google Account settings. See the instructions file for how to get this.
# 3. RECEIVER_EMAIL: The email address you want to send emails TO.

SENDER_EMAIL = "lucas.nseyep@gmail.com"
APP_PASSWORD = "lagc zxoi hpzs fkxo" # Needs to be added to this folder as a secret
# Put as many recipients as you like here
TO_EMAILS  = ["lucas.nseyep@gmail.com"]
CC_EMAILS  = []  # optional, e.g. ["teammate@example.com"]
BCC_EMAILS = []  # optional, e.g. ["hidden@example.com"]

def send_email():
    """
    Connects to the Gmail SMTP server and sends a pre-defined email.
    """
    # --- Create the Email Content ---
    subject = "This is your automated two-day reminder!"
    body = """
    Hello,

    This is a friendly, automated reminder email sent by your Python script.
    Have a great day!
    """

    # Create an EmailMessage object
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL

    # For headers, use comma-separated strings (RFC compliant)
    if TO_EMAILS:
        msg["To"] = ", ".join(TO_EMAILS)
    if CC_EMAILS:
        msg["Cc"] = ", ".join(CC_EMAILS)
    # NOTE: Do NOT set a "Bcc" header; BCCs should not appear in headers.

    msg.set_content(body)

    # Build the actual recipient list for SMTP (To + Cc + Bcc), de-duplicated
    all_recipients = list({email.strip().lower(): email for email in (TO_EMAILS + CC_EMAILS + BCC_EMAILS)}.values())
    if not all_recipients:
        raise ValueError("No recipients provided. Add at least one email to TO_EMAILS/CC_EMAILS/BCC_EMAILS.")
    # --- Send the Email ---
    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        print("Connecting to Gmail's server...")
        # Connect to Gmail's SMTP server over a secure connection
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            # Login to your account
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            print("Login successful. Sending email...")

            # Send the email
            smtp.send_message(msg)
            print(f"Email successfully sent to: {', '.join(all_recipients)}")

    except smtplib.SMTPAuthenticationError:
        print("Authentication Error: Failed to log in.")
        print("Please check your SENDER_EMAIL and APP_PASSWORD in the script.")
        print("Ensure you are using a valid 16-character App Password, not your regular password.")
    except Exception as e:
        print(f"An error occurred: {e}")


# This part of the script runs only when you execute the file directly
if __name__ == "__main__":
    # Before running, make sure you have filled in your details above!
    if SENDER_EMAIL == "your_email@gmail.com" or APP_PASSWORD == "your_16_character_app_password":
        print("="*50)
        print("SCRIPT NOT CONFIGURED!")
        print("Please open email_sender.py and replace the placeholder values")
        print("for SENDER_EMAIL and APP_PASSWORD.")
        print("="*50)
    else:
        send_email()
