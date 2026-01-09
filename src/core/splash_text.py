SPLASH_PATH = "./data/splash_text.txt"

def get_random_splash_text() -> str:
    from random import choice 

    splash_texts = get_splash_text_file()

    if not splash_texts:
        return "???"
    
    return choice(splash_texts)

def get_splash_text_file() -> list[str]:
    """Retrieve all splash texts from the splash text file."""
    import random

    try:
        with open(SPLASH_PATH, "r") as f:
            splash_texts = [line.strip() for line in f if line.strip()]
        return splash_texts
    except FileNotFoundError:
        return list()