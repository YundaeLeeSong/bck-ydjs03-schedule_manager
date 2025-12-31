#!/usr/bin/env python3
"""
test_gmail_proxy.py — Unit tests for gmailproxy

Run with: 
     python runner.py test
"""

import unittest
import smtplib
import os
from unittest.mock import patch, MagicMock
from gmailproxy import RealGmailService

class TestRealGmailService(unittest.TestCase):
    
    @patch.dict(os.environ, {
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "465",
        "SMTP_USERNAME": "user",
        "SMTP_PASSWORD": "pass",
        "SMTP_SENDER": "user@example.com",
        "SMTP_SECURITY": "SSL",
        "EMAIL_TIMEOUT": "10"
    })
    @patch("smtplib.SMTP_SSL")
    def test_send_with_ssl_success(self, mock_ssl):
        inst = MagicMock()
        mock_ssl.return_value.__enter__.return_value = inst
        inst.login.return_value = None
        inst.send_message.return_value = {}

        service = RealGmailService()
        ok, err = service.send_email(
            recipients=["to@example.com"],
            subject="hello",
            body_html="<p>hi</p>"
        )
        self.assertTrue(ok)
        self.assertIsNone(err)
        inst.login.assert_called_once_with("user", "pass")
        inst.send_message.assert_called_once()

    @patch.dict(os.environ, {
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "587",
        "SMTP_USERNAME": "user",
        "SMTP_PASSWORD": "pass",
        "SMTP_SENDER": "from@x",
        "SMTP_SECURITY": "STARTTLS"
    })
    @patch("smtplib.SMTP")
    def test_send_with_starttls_success(self, mock_smtp):
        inst = MagicMock()
        mock_smtp.return_value.__enter__.return_value = inst
        inst.starttls.return_value = None
        inst.login.return_value = None

        service = RealGmailService()
        ok, err = service.send_email(
            recipients=["a@b"],
            subject="s",
            body_html="<p>t</p>"
        )
        self.assertTrue(ok)
        self.assertIsNone(err)
        inst.starttls.assert_called_once()
        inst.login.assert_called_once_with("user", "pass")
        inst.send_message.assert_called_once()

    @patch.dict(os.environ, {
        "SMTP_USERNAME": "u",
        "SMTP_PASSWORD": "p",
        "SMTP_SECURITY": "NONE"
    })
    @patch("smtplib.SMTP")
    def test_attachment_missing(self, mock_smtp):
        service = RealGmailService()
        ok, err = service.send_email(
            recipients=["r"],
            subject="sub",
            body_html="<p>b</p>",
            attachments=["/path/does/not/exist.txt"]
        )
        self.assertFalse(ok)
        self.assertIn("Attachment not found", err)

    @patch.dict(os.environ, {
        "SMTP_USERNAME": "u",
        "SMTP_PASSWORD": "wrong",
        "SMTP_SECURITY": "SSL"
    })
    @patch("smtplib.SMTP_SSL")
    def test_auth_fail(self, mock_ssl):
        inst = MagicMock()
        mock_ssl.return_value.__enter__.return_value = inst
        inst.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")

        service = RealGmailService()
        ok, err = service.send_email(
            recipients=["r"],
            subject="sub",
            body_html="<p>b</p>"
        )
        self.assertFalse(ok)
        self.assertIn("Authentication failed", err)

if __name__ == "__main__":
    unittest.main()