# Commission-Free Options Trading on Alpaca

When you log into your Alpaca dashboard, you may see a banner like this:

> **Trade Commission-free Options**  
> *Commission‑free options trading is available on live accounts now!*

It’s a promotional widget inviting you to learn about and apply for Alpaca’s new zero‑commission options trading.

---

## 1. What Is It?

- **Commission‑Free Options**: Trade U.S. equity and ETF options (including multi‑leg strategies) without per‑contract commissions (you still pay regulatory and exchange fees).  
- **API‑First**: Place option‑chain lookups, quotes, and orders via the Alpaca REST or Python API just like you do for stocks.

---

## 2. Why You See the Banner

- **Read API Docs**: Opens the reference for options endpoints.  
- **Watch Tutorial**: A short video guide to placing option orders.  
- **Start Application**: A form to request approval for trading options in your account.

---

## 3. How to Enable Options Trading

1. Click **Start Application** on the banner.  
2. Complete the questionnaire (trading experience, risk profile).  
3. Submit and get approval (typically 1–2 business days).  
4. Once approved, your API `Account` object will have `options_blocked: false`.

---

## 4. Fees & Requirements

- **No Alpaca Commissions**: Pay only mandatory regulatory (SEC, FINRA, OCC) and exchange fees.  
- **Margin Account Needed**: At least \$2,000 equity required to trade options and short underlying assets.  
- **Borrowing & Fees**: Some contracts may be hard to borrow, leading to higher borrow fees.

---

## 5. Next Steps

- **Want Options?** Follow the banner flow and apply.  
- **Just Stocks?** Ignore or collapse the widget—no impact on stock trading.  
- **After Approval**: Use `api.get_option_chain()`, and `api.submit_order(..., asset_class='options')` in your scripts.

---

*Feel free to share any other questions, or let me know if you’d like a full sample Python snippet for options trading!*
