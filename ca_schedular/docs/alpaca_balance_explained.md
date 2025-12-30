
# Understanding Your Alpaca Balance Sheet

This document breaks down each field in your Alpaca balance sheet and explains what they mean in your current trading context.

---

## Key Balances

| Field | Description | Value | Interpretation |
|-------|-------------|-------|----------------|
| **RegT Buying Power** | Regular buying power for marginable securities | $1,266.24 | Severely reduced from $200k because you used margin. |
| **Day Trading Buying Power** | Reserved for Pattern Day Traders with margin accounts | $0.00 | You are not flagged as a Pattern Day Trader or don't meet criteria. |
| **Effective Buying Power** | Maximum funds available to buy securities | $1,266.24 | You only have this much left to spend due to margin use. |
| **Cash** | Actual cash in your account | ($98,138.65) | You are deep into margin. This negative value means you borrowed this much to buy stocks. |
| **Cash Withdrawable** | Cash you can pull out | $0.00 | All tied up or borrowed; nothing can be withdrawn now. |

---

## Position and Equity

| Field | Description | Value | Interpretation |
|-------|-------------|-------|----------------|
| **Equity** | Your total net account value = Cash + Position value | $99,404.89 | Your actual wealth in Alpaca right now. |
| **Long Market Value** | Value of all securities you bought ("long") | $197,543.54 | You’re fully invested in long positions. |
| **Short Market Value** | Value of shorted stocks | $0.00 | You haven’t shorted any stocks. |
| **Position Market Value** | Total market value of all positions | $197,543.54 | Same as long since no shorts. |

---

## Margin and Risk

| Field | Description | Value | Interpretation |
|-------|-------------|-------|----------------|
| **Initial Margin** | Capital needed to initiate your current margin positions | $98,771.77 | Amount of margin you're required to post. |
| **Maintenance Margin** | Minimum equity to maintain your positions | $59,263.06 | If equity falls below this, you get a margin call. |
| **Non-Marginable Buying Power** | Funds to buy stocks not eligible for margin | $0.00 | You’ve used it up or don’t have any free cash. |

---

## Other Fields

| Field | Description | Value |
|-------|-------------|-------|
| **SMA (Special Memorandum Account)** | Line of credit generated when you sell stock at a profit | $0.00 |
| **Accrued Fees** | Unsettled commissions or regulatory fees | $0.00 |
| **Held ACH Deposits** | ACH deposits still in process | 0 |
| **Day Trade Count** | Number of day trades done in the past 5 days | 1 |
| **Crypto Tier** | Access level for crypto trading | 1 (basic access) |

---

## Final Notes

- You are **almost fully invested** using margin.  
- Your **cash is negative** — you’re borrowing from Alpaca.  
- Your **buying power is now limited**, and you should watch for a **margin call** if the stock prices fall.  
- Make sure your **equity stays above your maintenance margin ($59k)** or you could be forced to sell holdings.

Stay cautious with large margin use—it can amplify both gains and losses.

