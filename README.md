# doic

smtp_send_env.py
=================
Single-file SMTP email sender with environment variable and .env support.

Usage:
  - Interactive (prompts): python smtp_send_env.py
  - Non-interactive with .env or environment variables:
      * Create a .env file (see .env.example) or export environment variables.
      * Set EMAIL_NONINTERACTIVE=1 and ensure required keys are present:
        SMTP_USERNAME, SMTP_PASSWORD, SMTP_SENDER, SMTP_TO, SUBJECT, BODY_TEXT
      * Run: python smtp_send_env.py

Testing:
  - Unit tests use mocking; run: python -m unittest smtp_send_env.py





pip install pipreqs
pipreqs . --force --ignore ext/,venv/
pip install -r requirements.txt