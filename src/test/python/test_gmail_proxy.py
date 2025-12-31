#!/usr/bin/env python3
"""
test_smtp.py — Unit tests for smtp_send_env.py

Run with: 
     python -m unittest test_smtp.py
"""

import unittest
import smtplib
from unittest.mock import patch, MagicMock
from gmailproxy.core import send_email


class TestSendEmail(unittest.TestCase):
    @patch("smtplib.SMTP_SSL")
    def test_send_with_ssl_success(self, mock_ssl):
        inst = MagicMock()
        mock_ssl.return_value.__enter__.return_value = inst
        inst.login.return_value = None
        inst.send_message.return_value = {}

        ok, err = send_email(
            smtp_host="smtp.example.com",
            port=465,
            security="SSL",
            username="user",
            password="pass",
            sender="user@example.com",
            recipients=["to@example.com"],
            subject="hello",
            body_html="<p>hi</p>",
            attachments=None
        )
        self.assertTrue(ok)
        self.assertIsNone(err)
        inst.login.assert_called_once_with("user", "pass")
        inst.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_send_with_starttls_success(self, mock_smtp):
        inst = MagicMock()
        mock_smtp.return_value.__enter__.return_value = inst
        inst.starttls.return_value = None
        inst.login.return_value = None

        ok, err = send_email(
            smtp_host="smtp.example.com",
            port=587,
            security="STARTTLS",
            username="user",
            password="pass",
            sender="from@x",
            recipients=["a@b"],
            subject="s",
            body_html="<p>t</p>"
        )
        self.assertTrue(ok)
        self.assertIsNone(err)
        inst.starttls.assert_called_once()
        inst.login.assert_called_once_with("user", "pass")
        inst.send_message.assert_called_once()

    @patch("smtplib.SMTP")
    def test_attachment_missing(self, mock_smtp):
        ok, err = send_email(
            smtp_host="smtp.example.com",
            port=25,
            security="NONE",
            username="u",
            password="p",
            sender="s",
            recipients=["r"],
            subject="sub",
            body_html="<p>b</p>",
            attachments=["/path/does/not/exist.txt"]
        )
        self.assertFalse(ok)
        self.assertIn("Attachment not found", err)

    @patch("smtplib.SMTP_SSL")
    def test_auth_fail(self, mock_ssl):
        inst = MagicMock()
        mock_ssl.return_value.__enter__.return_value = inst
        inst.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Auth failed")

        ok, err = send_email(
            smtp_host="smtp.example.com",
            port=465,
            security="SSL",
            username="u",
            password="wrong",
            sender="s",
            recipients=["r"],
            subject="sub",
            body_html="<p>b</p>"
        )
        self.assertFalse(ok)
        self.assertIn("Authentication failed", err)


if __name__ == "__main__":
    unittest.main()
