from langchain_core.tools import tool
import json

@tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """
    Sends an email to the specified recipient.
    Use this tool when the user explicitly asks to send an email, draft a message, or communicate with someone.
    """
    # Mock implementation for MVP
    email_data = {
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "status": "sent"
    }
    
    # In a real app, this would use SMTP or an API (SendGrid, SES)
    print(f"📧 SENDING EMAIL to {recipient}: {subject}")
    
    return json.dumps(email_data)

# List of tools to export
tools = [send_email]
