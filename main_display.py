import curses
import pandas as pd

from gui_assets import GuiAssets
from graph_plotter import CursedGraphs


class MainDisplay:

    def __init__(self):

        self.frame_width = 130
        self.frame_height = 40
        self.frame = curses.newwin(self.frame_height, self.frame_width, 10, 35)

        # Create color pairs.
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_WHITE, -1)

        self.YELLOW = curses.color_pair(1)
        self.CYAN = curses.color_pair(2)
        self.WHITE = curses.color_pair(3)

        self.frame.border(0)
        self.frame.attrset(self.YELLOW)
        self.frame.refresh()

        # Seeing the main frame as 3 parts for use in filter management;
        # center part fits 20 symbols. Left and right part shares 55 symbols width
        self.center_frame = self.frame_width // 2  # Should be width 20 max
        self.left_divider = (self.frame_width // 2) - (20 // 2)
        self.right_divider = self.frame_width - self.left_divider

        self.selector_position = 1
        # For keeping a category targetted while browsing its keywords
        self.keep_category_position = 1
        # Track whether the user is in categories or keywords selection
        # Can be "category" or "keyword", mainly deciding where the selector marker goes.
        self.filter_type = "category"
        # "add" or "del" or "graph" depending on sleection menu option. Dictates GUI appearances and behavior
        self.filter_action = "add"

        self.comparison_filters = []

        self.gui_assets = GuiAssets()

    def clear_frame(self):
        for i in range(1, 39):
            self.frame.addstr(i, 1, " " * 128)
        self.frame.refresh()

    def clear_mid_area(self):
        """Clears just the input area of the display window"""

        for i in range(1, 39):
            self.frame.addstr(i, self.left_divider, " " * 20)
        self.frame.refresh()

    def progress_bar(self, stage: int) -> None:
        """Displays a slice of the progress bar depending on argument input. sliced by 1-20, max input is 21."""
        progress_bar = "╞══════════════════╡ "

        self.frame.attrset(self.CYAN)

        self.frame.addstr(4, 55, progress_bar[:stage])
        self.frame.refresh()

    def scraping_message(self, *, line1: str = "", line2: str = "", line3: str = ""):
        """Text shown while scraping articles."""
        self.frame.addstr(2, 54, line1.center(22))
        self.frame.addstr(3, 54, line2.center(22))
        self.frame.addstr(4, 54, line3.center(22), self.YELLOW)
        self.frame.addstr(5, 54, "[q] to stop".center(22), self.YELLOW)
        self.frame.refresh()

    def scraping_url(self, url):
        """Displays the currently checked/scraped url."""
        self.frame.addstr(7, 1, url[:128].center(128), self.YELLOW)
        self.frame.refresh()

    def start_filter_selection(self, categories: dict, filter_type: str = "category", action: str = "add"):
        """Prepare settings, states and other variables upon entering filter selection."""
        
        # Set currently browsed type to be cateogry, not keyword.
        self.filter_type = filter_type
        self.filter_action = action
        # Dict with categores as keys and lists of keywords as values.
        self.categories = categories
        
        if categories:
            # Get length of categories list.
            self.len_categories = len(categories)
            if filter_type == "keyword":
                self.current_category = list(self.categories.keys())[self.selector_position - 1]
            # Get length of longest string among the categories.
            category_word_length = len(max(categories.keys(), key=len))
        else:
            self.len_categories = 0
            category_word_length = 0
        if action == "add" and category_word_length < 13:
            category_word_length = 13

        # Set dimensions for the box drawing based on which menu action is selected.
        if action == "add":
            self.category_height = self.len_categories + 3
        elif action in ["del", "graph"]:
            self.category_height = self.len_categories + 2
        self.category_width = category_word_length + 7
        self.category_pos_y = 2
        self.category_pos_x = self.left_divider

        self.clear_frame()
        self.draw_categories()
        self.draw_keywords()
        self.draw_selector()

    def draw_categories(self):
        """Update the categories box"""

        # set drawing to yellow
        self.frame.attrset(self.YELLOW)
        # Draw categories box and text above and below it. Height mode makes space for
        self.gui_assets.draw_box(self.frame, self.category_height, self.category_width, self.category_pos_y, self.left_divider - self.category_width)
        self.frame.addstr(1, self.left_divider - self.category_width, "Pick a category:".center(self.category_width))
        if self.filter_type == "category":
            self.frame.addstr(self.category_height + 2, self.left_divider - self.category_width, "[q] to cancel".center(self.category_width))

        # Set drawing to white
        self.frame.attrset(0)

        # Draw categories white
        for index, category in enumerate(self.categories, start=1):
            self.frame.addstr(index + 2, self.left_divider - self.category_width + 4, category)

        # Draw the selected cateogry yellow
        if self.filter_type == "category" and self.selector_position <= len(self.categories):
            self.frame.addstr(self.selector_position + 2, self.left_divider - self.category_width + 4, list(self.categories.keys())[self.selector_position - 1], self.YELLOW)

        if self.filter_action == "add":
            # Add an extra row for <Add category> at the bottom of the category list.
            if self.selector_position == self.len_categories + 1:
                self.frame.addstr(self.len_categories + 3, self.left_divider - self.category_width + 4, "<Add category>", self.YELLOW)
            else:
                self.frame.addstr(self.len_categories + 3, self.left_divider - self.category_width + 4, "<Add category>", curses.A_DIM)

        self.frame.attrset(self.YELLOW)

        if self.filter_action == "graph":
            # Draw filter comparison box in the middle segment
            filter1, filter2 = "...", "..."
            if len(self.comparison_filters) > 0:
                filter1 = self.comparison_filters[0]
            if len(self.comparison_filters) == 2:
                filter2 = self.comparison_filters[1]

            self.gui_assets.draw_box(self.frame, 6, 20, 3, self.left_divider)
            self.frame.addstr(4, self.left_divider + 1, "Filter one:".center(18))
            self.frame.addstr(5, self.left_divider + 1, filter1.upper().center(18))
            self.frame.addstr(6, self.left_divider + 1, "Filter two:".center(18))
            self.frame.addstr(7, self.left_divider + 1, filter2.upper().center(18))

        # Set the title text for the filter selection
        match self.filter_action:
            case "add":
                var = "ADD"
            case "del":
                var = "DELETE"
            case "graph":
                var = "COMPARE"

        self.frame.addstr(1, self.left_divider, f"{var} FILTERS".center(20))
        self.frame.refresh()

    def draw_keywords(self):
        """Update the keywords box."""

        self.frame.attrset(self.YELLOW)
        if self.filter_type == "category":
            # No keywords to draw (when selecting <Add new category>)
            if self.selector_position > len(self.categories.keys()):
                return
            else:
                self.current_category = list(self.categories.keys())[self.selector_position - 1]
        elif self.filter_type == "keyword":
            self.current_category = list(self.categories)[self.marked_category - 1]

        self.len_keywords = len(self.categories[self.current_category])
        if self.len_keywords == 0:
            # Always make one box space (height) for "Empty" if there are no keywords
            self.len_keywords = 1

        if not self.categories[self.current_category]:
            keyword_word_length = 7
        # Get length of longest keyword (min 7)
        else:
            keyword_word_length = len(max(self.categories[self.current_category], key=len))
            if keyword_word_length < 7:
                keyword_word_length = 7
        # Make space in the box for selector marker and some edge space.
        keyword_box_width = keyword_word_length + 7

        # Box title
        self.frame.addstr(1, self.right_divider + 4, "Keywords")
        # Draw the box.
        self.gui_assets.draw_box(self.frame, self.len_keywords + 2, keyword_box_width, 2, self.right_divider)

        # Set drawing to white.
        self.frame.attrset(0)

        if not self.categories[self.current_category]:
            self.frame.addstr(3, self.right_divider + 4, "Empty", curses.A_DIM)
        else:
            for i, keyword in enumerate(self.categories[self.current_category]):
                self.frame.addstr(i + 3, self.right_divider + 4, keyword)
        if self.filter_type == "keyword":
            self.frame.addstr(self.selector_position + 2, self.right_divider + 4, self.categories[self.current_category][self.selector_position - 1], self.YELLOW)
            self.frame.addstr(self.len_keywords + 4, self.right_divider + 1, "[q] to cancel", self.YELLOW)
        self.frame.refresh()

    def draw_input_box(self):

        self.hide_selector()

        # Remove the '[q] to cancel' under categories
        self.frame.addstr(self.category_height + 2, self.left_divider - self.category_width, " ".center(self.category_width))

        input_type = "category" if self.selector_position > len(
            self.categories) else "keyword"
        input_instructions = [
            "ENTER text to ", f"store new {input_type}", "",
            "ENTER blank to", "cancel and return"]

        self.frame.attrset(self.YELLOW)
        self.frame.addstr(6, self.left_divider, f"New {input_type}".center(20))

        # Draw the input box
        self.gui_assets.draw_box(self.frame, 3, 20, 7, self.left_divider)

        # Add the rows of isntructions
        for i in range(len(input_instructions)):
            self.frame.addstr(10 + i, self.left_divider, input_instructions[i].center(20))

        self.update_input_box()
        self.frame.refresh()

    def update_input_box(self, user_input: str = ""):

        self.frame.attrset(self.YELLOW)
        self.frame.addstr(8, self.left_divider + 1, user_input,  self.CYAN)
        self.frame.addch(8, self.left_divider + 1 + len(user_input), "█", curses.A_BLINK)
        self.frame.addch(8, self.left_divider + 2 + len(user_input), " ")
        self.frame.refresh()

    def draw_deletion_confirm(self, category: str, keyword: str = None):

        # Remove the '[q] to cancel' below categories or keywords
        self.frame.addstr(self.category_height + 2, self.left_divider - self.category_width, " ".center(self.category_width))
        self.frame.addstr(self.len_keywords + 4, self.right_divider, " " * 20)
        self.hide_selector()

        self.frame.attrset(self.YELLOW)
        self.frame.addstr(7, self.left_divider, "[ENTER] to confirm".center(20))
        self.frame.addstr(8, self.left_divider, "[q] to cancel".center(20))

        # Establish name of filter that is selected.
        filter_to_be_deleted = keyword if keyword else category

        self.gui_assets.draw_box(self.frame, 4, 20, 3, self.left_divider)

        # Make clear whether it is a category or a keyword that is being deleted.
        self.frame.addstr(4, self.left_divider + 1, f"Delete {self.filter_type}:".center(18))
        self.frame.addstr(5, self.left_divider + 1, filter_to_be_deleted.upper().center(18))

        self.frame.refresh()

    def draw_selector(self) -> None:
        """Draw the filter selection marker"""

        if self.filter_type == "category":
            pos_x = self.left_divider - self.category_width
        elif self.filter_type == "keyword":
            pos_x = self.right_divider

        # When there is no filter_type (while using input box), the marker will not be drawn.
        if self.filter_type not in ["category", "keyword"]:
            return

        self.frame.attrset(self.YELLOW)
        self.frame.addstr(self.selector_position + 2, pos_x + 1, "->", self.YELLOW)
        self.frame.refresh()

    def hide_selector(self):
        """Hide the filter selection marker, for when entering input states in main window"""

        pos_x = self.left_divider - \
            self.category_width if self.filter_type == "category" else self.right_divider

        # Erase the selection marker (on index location for BOTH boxes.)
        self.frame.addstr(self.selector_position + 2,
                          pos_x + 1, "  ", self.YELLOW)
        self.frame.refresh()

    def move_filter_selector(self, step: int) -> None:
        """Moves the selection indicator in the main display frame when accessing text filters."""

        if self.filter_type == "category":
            if self.filter_action == "add":
                if self.selector_position == 1 and step == -1 or self.selector_position == self.len_categories + 1 and step == 1:
                    return
            elif self.filter_action in ["del", "graph"]:
                if self.selector_position == 1 and step == -1 or self.selector_position == self.len_categories and step == 1:
                    return

        elif self.filter_type == "keyword":
            if self.selector_position == 1 and step == -1 or self.selector_position == len(self.categories[self.current_category]) and step == 1:
                return

        self.hide_selector()

        # Move the marker either up or down.
        self.selector_position += step

        self.clear_frame()
        self.draw_categories()
        self.draw_keywords()
        self.draw_selector()
        self.frame.refresh()

    def draw_top_list(self, type: str, data: pd.DataFrame) -> None:
        """Draws a bar graph with labels and values from a Dataframe."""

        pos_y, pos_x = 4, 2

        if type == "keywords":
            tuples = [(label, value) for label, value in data[["keyword", "count"]].values]
            header = "Top keywords total hit count, all time"
        elif type == "categories":
            tuples = [(label, value) for label, value in data[["category", "count"]].values]
            header = "Top categories by article count, all time"

        # Limit so that program doesn't crash when trying to print outside the display-window
        tuples = tuples[:17]

        graph = CursedGraphs().plot(tuples, self.frame_width - 2)

        self.clear_frame()

        self.frame.addstr(2, 1, header.center(128), self.YELLOW)

        for i, row in enumerate(graph):
            if i % 2 == 0:
                self.frame.attrset(self.YELLOW)
            else:
                self.frame.attrset(self.CYAN)

            self.frame.addstr(i * 2 + pos_y, pos_x, row[0])
            self.frame.addstr(i * 2 + pos_y, pos_x + len(row[0]), f"{row[1]}{(i + 1):2d} ", self.YELLOW)
            self.frame.attron(curses.A_DIM)
            self.frame.addstr(i * 2 + pos_y, pos_x + len(row[0] + f"{row[1]}{(i + 1):2d} "), row[2])
            self.frame.attroff(curses.A_DIM)
            self.frame.addstr(i * 2 + pos_y, pos_x + len(row[0] + f"{row[1]}{(i + 1):2d} " + row[2]), row[3])

            if i != 0:
                self.frame.addstr(i * 2 + pos_y - 1, pos_x +
                                  len(row[0]), " │ ", self.YELLOW)
            if i == 20 - pos_y:
                break
        self.frame.refresh()

    def draw_grouped_graph(self, header: str, data: pd.DataFrame):
        """Displays graph of values grouped by a label"""

        pos_y, pos_x = 4, 2

        self.clear_frame()

        groups = CursedGraphs().plot_group_flex(data)
        self.frame.addstr(2, 1, header.center(128), self.YELLOW)
        i = 0
        for group in groups:
            for date, rows in group.items():
                group_size = len(rows)

                label, sep, bar, count = rows[0]
                label_l, sep_l, bar_l = len(label), len(sep), len(bar)

                # Draw the separator and then the group label (date)
                # self.frame.addstr(i + pos_y, pos_x, "─" * label_l, self.WHITE)
                self.frame.addstr(i + pos_y, pos_x + label_l, " ┍", self.CYAN)
                self.frame.addstr(i + pos_y, pos_x + label_l + sep_l, date, self.CYAN)

                for j in range(1, 4):
                    label, sep, bar, count = rows[j - 1]

                    # Set alternating colors for the graph rows.
                    if j % 2 == 1:
                        self.frame.attrset(self.YELLOW)
                    else:
                        self.frame.attrset(self.CYAN)

                    # Draw the row items one at a time due to variations in display options
                    self.frame.addstr(i + j + pos_y, pos_x, label)
                    self.frame.addstr(i + j + pos_y, pos_x + label_l, sep, self.CYAN)
                    self.frame.attron(curses.A_DIM)
                    self.frame.addstr(i + j + pos_y, pos_x + label_l + sep_l, bar)
                    self.frame.attroff(curses.A_DIM)
                    self.frame.addstr(i + j + pos_y, pos_x + label_l + sep_l + bar_l, count)
            i += group_size + 2

        self.frame.refresh()
