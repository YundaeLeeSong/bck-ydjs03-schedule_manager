# gmailproxy/core.py
import os
import smtplib
import ssl
import mimetypes
from abc import ABC, abstractmethod
from email.message import EmailMessage
from typing import List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

class IEmailService(ABC):
    @abstractmethod
    def send_email(self, recipients: List[str], subject: str, body_html: str, attachments: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        pass

class RealGmailService(IEmailService):
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.port = int(os.getenv("SMTP_PORT", "465"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.sender = os.getenv("SMTP_SENDER") or self.username
        self.security = os.getenv("SMTP_SECURITY", "SSL").upper()
        self.timeout = int(os.getenv("EMAIL_TIMEOUT", "10"))

    def send_email(self, recipients: List[str], subject: str, body_html: str, attachments: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        if not self.username or not self.password:
             return False, "Missing SMTP_USERNAME or SMTP_PASSWORD in environment."

        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject
        msg.set_content(body_html, subtype="html")

        if attachments:
            for fp in attachments:
                if not os.path.isfile(fp):
                    return False, f"Attachment not found: {fp}"
                ctype, encoding = mimetypes.guess_type(fp)
                if ctype is None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)
                try:
                    with open(fp, "rb") as f:
                        data = f.read()
                    msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(fp))
                except Exception as e:
                    return False, f"Failed to attach {fp}: {e}"

        try:
            if self.security == "SSL":
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_host, self.port, context=context, timeout=self.timeout) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
            elif self.security == "STARTTLS":
                with smtplib.SMTP(self.smtp_host, self.port, timeout=self.timeout) as server:
                    server.ehlo()
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                    server.login(self.username, self.password)
                    server.send_message(msg)
            else:
                 with smtplib.SMTP(self.smtp_host, self.port, timeout=self.timeout) as server:
                    server.login(self.username, self.password)
                    server.send_message(msg)
            return True, None
        except smtplib.SMTPAuthenticationError:
            return False, "Authentication failed. Check username/app password."
        except Exception as e:
            return False, f"Email Error: {str(e)}"

class GmailProxy(IEmailService):
    def __init__(self):
        self._real_service = RealGmailService()

    def send_email(self, recipients: List[str], subject: str, body_html: str, attachments: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
        print(f"[GmailProxy] Sending email to {recipients} with subject '{subject}'...")
        
        # Pre-check
        if not recipients:
             return False, "No recipients provided"
        
        success, error = self._real_service.send_email(recipients, subject, body_html, attachments)
        
        if success:
            print("[GmailProxy] Email sent successfully.")
        else:
            print(f"[GmailProxy] Failed: {error}")
            
        return success, error