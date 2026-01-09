import curses
from .cli.main import main

if __name__ == "__main__":
    curses.wrapper(main)