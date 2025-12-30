# Market Order Timing & Time-in-Force (TIF) Options

When you place a **stock** Market order after U.S. equity market hours (9:30 AM–4:00 PM ET), Alpaca will **queue** the order and only submit it when the market next opens.

## Why Your Order Is Still “Accepted”
- You submitted at **9:00 PM ET** (market closed), so it will not **fill** until the next trading session begins at 9:30 AM ET.
- Until then, its status remains **Accepted** under Recent Orders.

## Time-in-Force (TIF) Options

| TIF Flag | Behavior                                                                                 | Use Case                          |
|----------|------------------------------------------------------------------------------------------|-----------------------------------|
| **DAY**  | Active for the upcoming trading session only; expires at market close if unfilled.       | Typical one-session order.        |
| **GTC**  | Good ’Til Canceled; stays active across multiple sessions until filled or canceled.       | Keep order in book indefinitely.  |
| **IOC**  | Immediate or Cancel; executes any available shares at next open, cancels the rest.       | Part-fill preference.             |
| **FOK**  | Fill or Kill; must fill in full at next open or be canceled entirely.                    | All-or-nothing execution.         |
| **OPG**  | Execute only in the **opening auction** of the next session.                             | Participate in opening auction.   |
| **CLS**  | Execute only in the **closing auction** of the session.                                  | Participate in closing auction.   |

### Recommended Settings for Normal Buys
- **Order Type:** Market  
- **Time in Force:** DAY  
  - Fires at next market open; expires at that close
- Or use **GTC** if you’d like to leave it open until it eventually fills

---

**Extended-hours Trading**  
- Alpaca’s web UI does **not** support extended-hours for equities by default, so market orders only hit the tape at official open (9:30 AM ET).