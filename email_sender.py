import os
import random
import glob
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
import re
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

sender_email = os.environ.get("SENDER_EMAIL")
app_password = os.environ.get("APP_PASSWORD")

def parse_list(env_value: str) -> list[str]:
    if not env_value:
        return []
    return [x.strip() for x in env_value.split(",") if x.strip()]

to_emails = parse_list(os.environ.get("TO_EMAILS"))
cc_emails = parse_list(os.environ.get("CC_EMAILS"))
bcc_emails = parse_list(os.environ.get("BCC_EMAILS"))

content = glob.glob("./newsletter/content/*.md")

path = random.choice(content)

MD_PATH = Path(path)

def _extract_subject(markdown_text: str, fallback: str = "Stay Focused - Never Give Up") -> str:
    """
    Use the first Markdown H1 ('# Title') as the subject if present,
    otherwise fall back to a default.
    """
    for line in markdown_text.splitlines():
        m = re.match(r"^\s*#\s+(.+?)\s*$", line)
        if m:
            return m.group(1).strip()
    return fallback

def _render_html(markdown_text: str) -> str:
    """
    Convert Markdown to HTML. Requires `pip install markdown`.
    """
    import markdown
    # Basic HTML wrapper so it looks nice in email clients
    body = markdown.markdown(markdown_text, extensions=["extra", "sane_lists"])
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Email</title>
  </head>
  <body>
    {body}
  </body>
</html>"""

def send_email(md_file: Path):
    """
    Connects to the Gmail SMTP server and sends a pre-defined email.
    """
    # --- Create the Email Content ---
    if not md_file.exists():
        raise FileNotFoundError(f"Markdown file not found: {md_file}")

    # --- Load and parse the markdown ---
    markdown_text = md_file.read_text(encoding="utf-8")
    subject = _extract_subject(markdown_text, fallback=md_file.stem.replace("_", " ").title())


    # Create an EmailMessage object
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email

    # For headers, use comma-separated strings (RFC compliant)
    if to_emails:
        msg["To"] = ", ".join(to_emails)
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
    # NOTE: Do NOT set a "Bcc" header; BCCs should not appear in headers.

    msg.set_content(markdown_text)

    html = _render_html(markdown_text)
    msg.add_alternative(html, subtype="html")

    # Build the actual recipient list for SMTP (To + Cc + Bcc), de-duplicated
    all_recipients = list({email.strip().lower(): email for email in (to_emails + cc_emails + bcc_emails)}.values())
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
            smtp.login(sender_email, app_password)
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
    if sender_email == "your_email@gmail.com" or app_password == "your_16_character_app_password":
        print("="*50)
        print("SCRIPT NOT CONFIGURED!")
        print("Please open email_sender.py and replace the placeholder values")
        print("for SENDER_EMAIL and APP_PASSWORD.")
        print("="*50)
    else:
        send_email(MD_PATH)
