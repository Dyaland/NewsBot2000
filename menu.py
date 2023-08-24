import curses
from datetime import datetime

from gui_assets import GuiAssets


class BotHead:

    def __init__(self) -> None:

        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        self.YELLOW = curses.color_pair(1)
        self.CYAN = curses.color_pair(2)

        # Animated robot head
        self.frame = curses.newwin(10, 26, 0, 5)
        self.frame.attrset(self.YELLOW)

        self.robot_parts = GuiAssets().robot_parts

        # Draw the bot face with the default look.
        for i, line in enumerate(self.robot_parts["right"] + self.robot_parts["base"]):
            self.frame.addstr(0 + i, 2, line)

    def draw_bot(self, style: str) -> None:
        """Update the bot_face using one of the styles."""
        self.frame.attrset(self.YELLOW)
        for i, line in enumerate(self.robot_parts[style]):
            self.frame.addstr(0 + i, 2, line)
        self.frame.refresh()

    def update_clock(self) -> None:
        """Write current time and date."""
        current_time = datetime.now()
        self.frame.attrset(self.CYAN)
        self.frame.addstr(4, 8, f"{current_time.time()}"[:8].center(10))
        self.frame.addstr(
            5, 8, f"{f'{current_time.ctime()}'[:3]} {current_time.strftime('%d')}".center(10))
        self.frame.addstr(6, 8, f"{current_time.strftime('%b %Y')}".center(10))

        self.frame.refresh()


class Menu:

    def __init__(self) -> None:

        # Frame settings
        self.frame = curses.newwin(18, 26, 10, 5)

        # Create color pairs.
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)

        self.YELLOW = curses.color_pair(1)
        self.CYAN = curses.color_pair(2)
        curses.init_pair(3, -1, curses.COLOR_CYAN)
        self.progress_bar_style = curses.color_pair(3)

        self.frame.attrset(self.YELLOW)

        self.frame.nodelay(True)

        self.gui_assets = GuiAssets()

        self.frame.border(0)
        for x in (8, 12, 16):
            self.frame.addch(0, x, "┴")
        self.frame.addch(13, 0, "├")
        self.frame.addch(13, 25, "┤")
        self.frame.addstr(13, 1, 24 * "─")
        self.frame.attrset(0)

        self.options = {
            "main": {
                1: ["Start Scraper", ["Scrape for more", "news articles", "[q] to stop it"]],
                2: ["Finetune Filters", ["View filter", "management options"]],
                3: ["Access Analysis", ["Views analysis", "and graphing options"]],
                5: ["[q] Quit", ["Good bye", ""]]
            },
            "filters": {
                1: ["Add Filter", ["Add new filters", "to the SQL database"]],
                2: ["Delete Filter", ["Delete filters", "from the SQL database"]],
                4: ["[q] Back to main", ["Return to the main menu", ""]]
            },
            "analysis": {
                1: ["Top keyword hits", ["Display a toplist of", "keywords of all time"]],
                2: ["Top categories", ["Display a toplist of", "categories of all time"]],
                3: ["Top 3 cat. per day", ["View of most common", "categories per day"]],
                5: ["All urls -> file", ["Save all urls in the", "database to 'urls.txt'"]],
                7: ["[q] Back to main", ["Return to the main menu", ""]]
            }
        }

        self.current_menu = "main"  # "main", "filters" or "analysis".
        self.marker_position = 1

        self.draw_main_menu()
        self.frame.refresh()

    def draw_menu_marker(self) -> None:

        x_mod = 0
        y_mod = 0
        if self.current_menu != "main":
            x_mod = 1
            y_mod = 2

        # Draw the menu marker
        self.frame.addstr(self.marker_position + y_mod,
                          1 + x_mod, "->", self.YELLOW)

    def hide_marker(self):
        """Hide the menu marker, for when entering input states in main window"""
        x_mod = 0
        y_mod = 0
        if self.current_menu != "main":
            x_mod = 1
            y_mod = 2

        # Draw the menu marker
        self.frame.addstr(self.marker_position + y_mod,
                          1 + x_mod, "  ", self.YELLOW)

    def draw_main_menu(self) -> None:

        self.current_menu = "main"
        self.frame.attrset(self.YELLOW)

        # Clear the menu selection area:
        for y_pos in range(1, 13):
            self.frame.addstr(y_pos, 1, " " * 24)

        # Clear the description area
        for i in range(3):
            self.frame.addstr(14 + i, 1, " " * 24)

        # Set drawing to white, for menu options
        self.frame.attrset(0)
        # Draw the menu options.
        for i, option in self.options["main"].items():
            option_text = option[0]

            if i == self.marker_position:
                # Selected option will be yellow
                self.frame.addstr(0 + i, 4, option_text, self.YELLOW)
                # Grab the selected menu description during the loop
                description = option[1]
            else:
                self.frame.addstr(0 + i, 4, option_text)

        # And draw the description
        for i, line in enumerate(description):
            self.frame.addstr(14 + i, 1, line.center(24), self.CYAN)

        # Draw the menu marker
        self.draw_menu_marker()
        self.frame.refresh()

    def draw_sub_menu(self, sub_menu: str) -> None:
        """Draws sub-menus for "filters" and "analysis" menus."""

        self.current_menu = sub_menu
        self.frame.attrset(self.YELLOW)

        if self.current_menu == "filters":
            title = "Filters Menu"
        elif self.current_menu == "analysis":
            title = "Analysis Menu"

        # Draw the title
        self.frame.addstr(1, 2, title.center(22))
        # Draw the inner sub-menu box on top of the main menu.
        self.gui_assets.draw_box(self.frame, 11, 24, 2, 1)

        # Change drawing to white, for menu options.
        self.frame.attrset(0)
        for key, option in self.options[self.current_menu].items():
            option_text = option[0]

            if key == self.marker_position:
                # Selected option will be yellow
                self.frame.addstr(key + 2, 5, option_text, self.YELLOW)
                # Grab the selected menu description during the loop
                description = option[1]
            else:
                self.frame.addstr(key + 2, 5, option_text)

        # And draw the description
        for i, line in enumerate(description):
            self.frame.addstr(14 + i, 1, line.center(24), self.CYAN)

        self.draw_menu_marker()
        self.frame.refresh()

    def move_marker(self, step: int) -> None:

        if self.marker_position == 1 and step == -1 or self.marker_position == max(self.options[self.current_menu].keys()) and step == 1:
            return

        # Move the marker either up or down.
        self.marker_position += step

        if self.marker_position not in self.options[self.current_menu].keys():
            self.move_marker(step)

        # Draw either main menu or sub menu
        if self.current_menu == "main":
            self.draw_main_menu()
        else:
            self.draw_sub_menu(self.current_menu)

        self.frame.refresh()


if __name__ == "__main__":
    me = Menu()
