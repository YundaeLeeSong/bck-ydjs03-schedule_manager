# Plaid vs Zelle

**Plaid** and **Zelle** serve very different roles in the world of banking and payments:

## What is Plaid?
- A fintech “connector,” not a bank. Plaid provides secure APIs that let apps (like Alpaca, Venmo, Robinhood, etc.) link to your existing bank account.
- Primary functions:
  - **Account verification**: Confirms your account number and balance so the app can open or fund an account.
  - **Transaction access**: (With your permission) reads transaction history for budgeting apps or risk checks.
  - **ACH transfers**: Enables apps to initiate deposits and withdrawals via the Automated Clearing House network.
- How it works: You log into your real bank’s online portal within Plaid’s secure widget; Plaid then shares encrypted tokens with the third-party app.

## What is Zelle?
- A peer-to-peer (P2P) payment network. Zelle moves money directly between bank accounts—often within minutes.
- Primary functions:
  - **Instant transfers**: Send or receive up to your bank’s limit using just an email or phone number.
  - **No middle-app needed**: Many U.S. banks integrate Zelle right in their mobile apps.
- How it works: You authorize your bank to send funds via Zelle’s network to another person’s bank (also on Zelle).

## Key Differences

| Feature              | Plaid                                          | Zelle                                |
|----------------------|------------------------------------------------|--------------------------------------|
| **Role**             | Securely connects your bank to third-party apps | Moves money person-to-person         |
| **Use case**         | Funding/integrating apps (Alpaca, Venmo, etc.) | Sending/receiving money with friends |
| **Speed of transfer**| Depends on ACH (1–3 business days)             | Often near-instant                   |
| **Account creation** | No new account—just links existing bank accounts| No new account—uses your bank account|
| **Cost to user**     | Free (paid by the third-party app)             | Free (beyond bank limits)            |

**Bottom line**:  
- **Plaid** is the secure “bridge” that lets Alpaca (and other apps) interact with your **existing** bank account—no new account needed.  
- **Zelle** is a fast way to **send or receive** money directly between bank accounts.  
- They’re complementary tools, not alternatives. Placing a deposit on Alpaca via Plaid uses ACH; sending your friend lunch money in two minutes would use Zelle.
