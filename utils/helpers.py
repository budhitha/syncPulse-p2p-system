

def message_with_length(message: str) -> str:
    """Prepend the length of a message to the message."""
    message = " " + message
    return str((10000 + len(message) + 5))[1:] + message