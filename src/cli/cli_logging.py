LOG_FILE = "./log/cli_log.txt"


def clear_log() -> None:
    """Clear the CLI log file."""
    with open(LOG_FILE, "w") as log_file:
        log_file.write("")


def log_message(message: str) -> None:
    """Log a message to the CLI log file."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{message}\n")
