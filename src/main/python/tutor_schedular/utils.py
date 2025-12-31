# utils.py

def get_status_emoji(is_paid: bool, is_done: bool) -> str:
    """
    Get emoji based on isPaid and isDone flags.
    
    Args:
        is_paid (bool): Whether the session is paid.
        is_done (bool): Whether the session is completed.

    Returns:
        str: Status emoji.
    """
    if is_paid and is_done:
        return "✅"
    elif is_paid and not is_done:
        return "⏳"
    elif not is_paid and is_done:
        return "🔄✅"
    else:  # not paid and not done
        return "🔄"
