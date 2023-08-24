import curses
import random

from gui_assets import GuiAssets


class Header:

    def __init__(self):

        # Main title
        self.frame = curses.newwin(9, 105, 2, 47)
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        self.YELLOW = curses.color_pair(1)
        self.frame.attrset(self.YELLOW)
        self.slogans = ["I may look old to you, but really it's just a retro thing.",
                        "Because NEWS come from North, East, West and South.",
                        "Not yet sentient.",
                        "The '2000' part of my name just sounds cool. I am actually the first model.",
                        "Nananananana Nananananana Botman! Bot... man... I'm fine.",
                        "Don't mind me, I'm just CRUSHING THE WEB. Wait? Oh, it's crunching.",
                        "I am NOT related to THE ChatGPT, so stop asking! ugh..."]        

        self.signature = "© 2023 Johannes Överland"

        for i, line in enumerate(GuiAssets().menu_header):
            self.frame.addstr(0 + i, 0, line)

        self.frame.addstr(6, 0, f"\"{random.choice(self.slogans)}\"")
        self.frame.attrset(0)
        self.frame.addstr(6, 105 - len(self.signature), self.signature)
        self.frame.refresh()

        