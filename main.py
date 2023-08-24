import sqlite3
import logging
import curses  # "pip install windows-curses" on windows systems.
import pandas as pd
import os
from time import sleep
from datetime import datetime
from collections import defaultdict

import sql_manager as sql
from info import Info
from menu import BotHead, Menu
from header import Header
from gui_assets import GuiAssets
from url_scraper import UrlScraper
from main_display import MainDisplay
from text_cleaner import TextCleaner
from article_scraper import ArticleScraper
from graph_calculations import Statistics


class NewsBot2000:

    def __init__(self) -> None:

        # This list of dicts is iterated over while scraping news sites.
        # I contains the required specific arguments for both the url_scraper and the article_scraper to function with precision.
        self.news_sites = [
            {"urls": [
             "huffpost.com", "huffpost.com/news/world-news"],
             "regex_url_match": r"/entry/",
             "url_blacklist": None,
             "tag_regex": r"entry__content",
             "tag_blacklist": [r"author-card", r"slidedown"]
             },

            {"urls": [
                "apnews.com/hub/world-news",
                "apnews.com"],
             "regex_url_match": r"/article/",
             "url_blacklist": [r"/article/photography-", r"/article/videos-"],
             "tag_regex": r"Article|article-|Body",
             "tag_blacklist": []
             },

            {"urls": [
                "edition.cnn.com/world",
                "edition.cnn.com/world/africa",
                "edition.cnn.com/world/americas",
                "edition.cnn.com/world/asia",
                "edition.cnn.com/world/australia",
                "edition.cnn.com/world/china",
                "edition.cnn.com/world/europe",
                "edition.cnn.com/world/india",
                "edition.cnn.com/world/middle-east",
                "edition.cnn.com/world/united-kingdom"],
             "regex_url_match": r"/\d+/\d+/\d+/",
             "url_blacklist": [r"/gallery/", r"/videos/"],
             "tag_regex": r"article__content|pg-rail-tall__body|BasicArticle__main|pg-special-article__body",
             "tag_blacklist": [r"footer_"]
             },

            {"urls": ["news.com.au/world", "news.com.au"],
             "regex_url_match": r"/news-story/",
             "url_blacklist": None,
             "tag_regex": r"story-primary",
             "tag_blacklist": []
             },

            {"urls": ["latimes.com/world-nation", "latimes.com",],
             "regex_url_match": r"/story/",
             "url_blacklist": None,
             "tag_regex": r"rich-text-article-body-content",
             "tag_blacklist": [r"promo"]
             },

            {"urls": ["aljazeera.com"],
             "regex_url_match": r"/\d+/\d+/\d+/",
             "url_blacklist": [r"/gallery/", r"/liveblog/", r"list-of-key-events", r"/program/"],
             "tag_regex": r"wysiwyg",
             "tag_blacklist": []
             }
        ]

        # Initialize screen
        self.stdcr = curses.initscr()
        curses.curs_set(False)
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()  # Disable printing to terminal

        # Initiate the article scraper and text processor
        self.article_scraper = ArticleScraper()
        self.text_cleaner = TextCleaner()

        # Database check. Creates new db if check fails.
        self.db = {"database": "data.db"}

        try:
            sql.execute_query(self.db, "SELECT * FROM articles LIMIT 1;")
        except sqlite3.OperationalError:
            self.create_database(self.db)

        # Dict to be populated with categories and keywords when requried.
        self.categories = {}

        # Create color pairs.
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)

        self.YELLOW = curses.color_pair(1)
        self.CYAN = curses.color_pair(2)

        # Create curses windows
        self.header = Header()
        self.bothead = BotHead()
        self.menu = Menu()
        self.info = Info(self.db)
        self.display = MainDisplay()

        # Import graphical assets (custom box drawer)
        self.gui_assets = GuiAssets()

        # Set key input frame.
        self.menu.frame.keypad(1)
        self.key = -1

        # Keeps track of user input
        self.input_text = ""

    def create_database(self, database: str) -> None:

        # Define news categories and keywords
        default_categories = {
            'Business': ['economy', 'finance', 'market', 'investment', 'mergers', 'acquisitions', 'trade', 'industry', 'companies', 'stocks', 'bonds', 'startup', 'inflation'],
            'Sports': ['athlete', 'team', 'competition', 'tournament', 'match', 'medal', 'record', 'championship', 'coach', 'stadium', 'player', 'league'],
            'Technology': ['software', 'hardware', 'ai', 'cybersecurity', 'cloud', 'mobile', 'internet', 'electronics', 'innovation', 'gadget', 'robotics', 'cryptocurrency'],
            'Politics': ['government', 'election', 'president', 'congress', 'senate', 'house', 'policy', 'bill', 'law', 'diplomacy', 'foreign', 'nation'],
            'Entertainment': ['film', 'music', 'television', 'theater', 'comedy', 'dance', 'fashion', 'beauty', 'arts', 'media', 'pop', 'culture'],
            'Health': ['medicine', 'disease', 'vaccine', 'nutrition', 'fitness', 'wellness', 'therapy', 'rehabilitation', 'lifestyle', 'doctor', 'pharmaceuticals', 'surgery'],
            'Science': ['biology', 'chemistry', 'astronomy', 'climate', 'environment', 'evolution', 'geology', 'oceanography', 'physics', 'research', 'invention', 'space'],
            'World News': ['war', 'conflict', 'peace', 'terrorism', 'human rights', 'disaster', 'refugee', 'immigration', 'politics', 'geopolitics', 'diplomat', 'humanitarian', 'ukraine'],
            'Crime': ['murder', 'theft', 'robbery', 'fraud', 'cybercrime', 'police', 'kidnapping', 'smuggling', 'counterfeiting', 'illegal', 'arrest', 'bribery'],
            'Environment': ["climate change", "global warming", "greenhouse gases", "renewable energy", "carbon emissions", "sustainability", "climate crisis", "oil spill", "environmental protection", "biodiversity", "ice caps", "environmental justice"]
        }

        # Create tables.
        for query in (
            "CREATE TABLE articles(url TEXT PRIMARY KEY, scrape_date DATETIME, content TEXT)",
            "CREATE TABLE categories(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, category TEXT)",
            "CREATE TABLE keywords(keyword TEXT PRIMARY KEY, category_id INT, FOREIGN KEY (category_id) REFERENCES categories(id));",
            "CREATE TABLE failed_scrapes(url TEXT PRIMARY KEY, scrape_date DATETIME, error_message TEXT)"
        ):
            sql.execute_query(database, query)

        # Insert categories (keys from the above dict)
        for category, keywords_list in default_categories.items():
            sql.execute_query(
                database, f"""INSERT INTO categories (category) VALUES ("{category}");""")

            # Get the serial id from the category table for use as foreign key for keywords.
            category_id = sql.execute_query(
                database, f"""SELECT id FROM categories WHERE category = "{category}" """)[0][0]
            for keyword in keywords_list:
                sql.execute_query(
                    database, f"""INSERT INTO keywords (keyword, category_id) VALUES ("{keyword}", {category_id});""")

    def fetch_filters_from_db(self):
        """Fetches and matches keywords with categories."""
        # Get categories andd assign as keys in a new dictionary
        cats = sql.execute_query(self.db, "SELECT * FROM categories;")
        categories = {item[1]: item[0] for item in cats}
        # Get keywords and assign into lists of values for each category
        for key in categories:
            categories[key] = [keyword[0] for keyword in sql.execute_query(
                self.db,
                f"SELECT keyword FROM keywords WHERE category_id = {categories[key]};")]
        return categories

    def delete_filter_from_database(self, *, category: str = None, keyword: str = None) -> None:

        if category:
            # Delete the cateogry
            sql.execute_query(
                self.db, f"""DELETE FROM categories WHERE category = "{category}";""")
        elif keyword:
            # Delete the keyword
            sql.execute_query(
                self.db, f"""DELETE FROM keywords WHERE keyword = "{keyword}";""")

    def export_urls(self):
        """Saves all article urls to at txt file."""

        article_urls = (url[0] for url in sql.execute_query(
            self.db, "SELECT url FROM articles;"))
        with open("urls.txt", "w") as f:
            for url in article_urls:
                f.write(url + "\n")

    def run_scraper(self) -> None:
        """Fetch any new articles from the news sites."""

        # Fetch all stored urls from the database.
        stored_urls = defaultdict(None)
        for url in [url[0] for url in sql.execute_query(self.db, "SELECT url FROM articles;")]:
            stored_urls[url] = None
        for url in [url[0] for url in sql.execute_query(self.db, "SELECT url FROM failed_scrapes;")]:
            stored_urls[url] = None

        # Initiate the scraping GUI assets.
        self.display.frame.attrset(self.YELLOW)
        self.gui_assets.draw_box(self.display.frame, 6, 24, 1, 53)
        self.display.frame.addstr(5, 54, "[q] to stop".center(22))

        for news_site in self.news_sites:
            for url in news_site["urls"]:
                # Get a list of generators with article urls from each site url.
                url_generator = UrlScraper().generator(
                    site_url=url,
                    regex_url_match=news_site["regex_url_match"],
                    url_blacklist=news_site["url_blacklist"]
                )

                # Iterate over the generator's urls and check the url against the database. Scrape it if not already stored.
                for article_url in url_generator:
                    # Stars on either side of the progress bar

                    self.display.scraping_message(
                        line1="CHECKING", line2="URLS", line3=f"*{' ' * 20}*")
                    self.display.progress_bar(0)
                    self.bothead.update_clock()
                    sleep(0.01)  # SLEEP

                    # GUI update, show current url
                    self.display.scraping_url(article_url)
                    self.display.frame.refresh()
                    stop = self.menu.frame.getch()
                    if stop == -1:
                        pass
                    if stop == 113:
                        self.display.clear_frame()
                        return

                    # Avoid scraping the same article twice.
                    if article_url in stored_urls:
                        continue

                    self.display.scraping_message(
                        line1="REQUESTING", line2="PAGE", line3=f"*{' ' * 20}*")
                    self.display.progress_bar(7)
                    self.bothead.update_clock()
                    # sleep(randint(1, 1) // 50)  # SLEEP

                    # Scrape the article text. Stores in failed_scrapes for later review if there was a problem.
                    try:
                        text = self.article_scraper.scrape_text(
                            article_url, news_site["tag_regex"], news_site["tag_blacklist"])
                    except Exception as e:
                        sql.execute_query(self.db,
                                          f"""INSERT INTO failed_scrapes (url, scrape_date, error_message)
                                            VALUES ("{article_url}", "{str(datetime.now().date())}", "{e}");""")
                        stored_urls[article_url] = None
                        continue

                    if not text:
                        sql.execute_query(self.db,
                                          f"""INSERT INTO failed_scrapes (url, scrape_date, error_message)
                                            VALUES ("{article_url}", "{str(datetime.now().date())}", "No text found");""")
                        continue

                    self.display.scraping_message(
                        line1="CLEANING", line2="TEXT", line3=f"*{' ' * 20}*")
                    self.display.progress_bar(13)
                    self.bothead.update_clock()
                    sleep(0.03)  # SLEEP

                    # Clean the text and turn into list of list of words
                    list_of_words = self.text_cleaner.clean_text(text)
                    # With some forced delay and gui progress display, store them in the database.

                    self.display.scraping_message(
                        line1="SAVING TO ", line2="DATABASE", line3=f"*{' ' * 20}*")
                    self.display.progress_bar(21)
                    self.bothead.update_clock()
                    sleep(0.03)  # SLEEP

                    sql.execute_query(self.db,
                                      f"""INSERT INTO articles (url, scrape_date, content)
                                            VALUES ("{article_url}", "{str(datetime.now().date())}", "{list_of_words}") """)
                    stored_urls[article_url] = None
                    self.info.display_info()

        self.display.clear_frame()

    def back_to_main_menu(self) -> None:
        """Reset assets for main menu view"""

        self.display.clear_frame()

        self.key = -1
        self.menu.marker_position = 1
        self.menu.draw_main_menu()
        self.bothead.draw_bot("right")

    def back_to_sub_menu(self, sub_menu: str):

        self.display.clear_frame()
        self.key = -1
        self.menu.draw_sub_menu(sub_menu)
        self.bothead.draw_bot("right")

    def enter_filters_menu(self):
        """Load data from database and draw filters sub-menu over the main menu"""

        self.menu.current_menu = "filters"
        self.menu.marker_position = 1
        self.menu.draw_sub_menu("filters")
        # Get categories and filters from the database
        self.categories = self.fetch_filters_from_db()

    def add_filter_to_database(self) -> None:
        """Evalutate user input and save to database."""

        # If there was anything in the input field.
        self.input_text = self.input_text.strip()

        # Check that the input is not a duplicate of existing filter words.
        if self.input_text.capitalize() in self.categories or self.input_text.lower() in [keyword for category in self.categories for keyword in category]:
            return

        if len(self.input_text) > 0:
            if self.display.selector_position > len(self.categories):

                # Store the new category in the database.
                sql.execute_query(
                    self.db, f"""INSERT INTO categories (category) VALUES ("{self.input_text.capitalize()}") """)
            else:
                # Get the id for the category to be used as foreign key for the keyword.
                cat_id = sql.execute_query(
                    self.db, f"""SELECT id FROM categories WHERE category = "{list(self.categories.keys())[self.display.selector_position - 1]}" """)[0][0]
                # Store the new keyword in the database, with foreign key referring to the category.
                sql.execute_query(
                    self.db, f"""INSERT INTO keywords (keyword, category_id) VALUES ("{self.input_text.lower()}", "{cat_id}") """)

    def key_events_base(self):
        self.key = -1
        self.bothead.update_clock()
        pressed_key = self.menu.frame.getch()

        if pressed_key == -1:
            return

        self.key = pressed_key

    def key_events_menu(self, current_options_list: str) -> None:
        self.key = -1
        self.bothead.update_clock()
        pressed_key = self.menu.frame.getch()

        if pressed_key == -1:
            return

        self.key = pressed_key
        match self.key:

            case 258:  # DOWN ARROW
                self.menu.move_marker(1)
                if self.menu.marker_position > len(current_options_list):
                    self.bothead.draw_bot("sad")
                else:
                    self.bothead.draw_bot("right")

            case 259:  # UP ARROW
                self.menu.move_marker(-1)
                self.bothead.draw_bot("left")

            case 10:  # ENTER
                if self.menu.marker_position == max(current_options_list):
                    # Triggers a break in the outer while loop
                    self.key = 113

    def key_events_filters_management(self) -> None:
        self.key = -1
        self.bothead.update_clock()
        pressed_key = self.menu.frame.getch()

        if pressed_key == -1:
            return

        self.key = pressed_key
        match self.key:

            case 258:  # DOWN ARROW
                self.display.move_filter_selector(1)
                self.bothead.draw_bot("right")

            case 259:  # UP ARROW
                self.display.move_filter_selector(-1)
                self.bothead.draw_bot("left")

    def key_events_text_input(self):
        self.key = -1
        self.bothead.update_clock()
        pressed_key = self.menu.frame.getch()

        if pressed_key == -1:
            return

        self.key = pressed_key
        match self.key:

            case 10:  # ENTER
                self.key = 113
                return

            case 27:  # ESCAPE
                self.input_text = ""
                self.key = 113
                return

            case 263:  # Backspace
                if len(self.input_text) > 0:
                    self.input_text = self.input_text[:-1]
                self.display.update_input_box(self.input_text)

            case _:
                # Add characters to input_text, only if input is alphabetical.
                char = chr(self.key)

                if char.isalpha() or char == " " and len(self.input_text) < 17:
                    self.input_text += char
                self.display.update_input_box(self.input_text)
                self.key = -1

    def main(self) -> None:
        """Menu tree, key-events and curses GUI assets management.
        char 113, or lower case 'q' is used to break while loops."""
        # MAIN MENU, listen for key presses.
        while self.key != 113:
            self.key_events_menu(self.menu.options["main"].keys())

            if self.key == 10 and self.menu.marker_position == 1:
                # Run the scraper, cancel it with 'q'.
                self.run_scraper()

            elif self.key == 10 and self.menu.marker_position == 2:
                # FILTERS MENU, sub-menu, listen for key presses.
                self.enter_filters_menu()

                while self.key != 113:
                    self.key_events_menu(self.menu.options["filters"].keys())

                    if self.key == 10 and self.menu.marker_position == 1:
                        # FILTER SELECTION / CREATION in display window, listen for key presses.
                        self.menu.hide_marker()
                        self.menu.frame.refresh()

                        self.display.selector_position = 1
                        self.display.start_filter_selection(self.categories, "category", "add")
                        while self.key != 113:
                            self.key_events_filters_management()

                            # NEW FILTER INPUT CATEGORY/KEYWORD
                            if self.key == 10:
                                self.input_text = ""
                                self.display.draw_input_box()
                                # TEXT INPUT, listen to key presses
                                while self.key != 113:
                                    self.key_events_text_input()

                                # When ENTER is pressed loop breaks, input is evaluated and category or keyword added to the database.
                                self.add_filter_to_database()
                                # Update the dict from the database.
                                self.categories = self.fetch_filters_from_db()
                                # Re-draw the display window after the changes.
                                self.display.start_filter_selection(self.categories, "category", "add")
                                self.info.display_info()
                                self.key = -1

                        self.back_to_sub_menu("filters")

                    elif self.key == 10 and self.menu.marker_position == 2:
                        # FILTER SELECTION / DELETION in display window, listen for key presses.
                        if not self.categories:
                            continue
                        self.menu.hide_marker()
                        self.menu.frame.refresh()

                        self.display.selector_position = 1
                        self.display.start_filter_selection(self.categories, "category", "del")
                        while self.key != 113:
                            self.key_events_filters_management()

                            # FILTER DELETION FOR CATEGORIES AND KEYWORDS
                            if self.key == 10:
                                category = list(self.categories.keys())[
                                    self.display.selector_position - 1]

                                # In case the selected category is empty, prompt it for deletion.
                                if not self.categories[category]:
                                    # Prompt deletion of the category
                                    self.display.draw_deletion_confirm(category=category)
                                    # Listen for key input
                                    while self.key != 113:
                                        self.key_events_base()
                                        if self.key == 10:
                                            self.delete_filter_from_database(category=category)
                                            self.key = 113

                                    # After deletion of cateogry
                                    # Move the selector marker up one step due to the deleted category
                                    self.info.display_info()
                                    if self.display.selector_position != 1:
                                        self.display.selector_position -= 1

                                # In case there is at elast one keyword in the cateogory, switch to keyword selection.
                                else:
                                    # Set a fixed category while browsing its keywords
                                    self.display.marked_category = self.display.selector_position
                                    self.display.selector_position = 1
                                    self.display.start_filter_selection(self.categories, "keyword", "del")
                                    while self.key != 113:
                                        self.key_events_filters_management()
                                        if self.key == 10:
                                            keyword = self.categories[self.display.current_category][
                                                self.display.selector_position - 1]
                                            self.display.draw_deletion_confirm(
                                                category=self.display.current_category, keyword=keyword)
                                            while self.key != 113:
                                                self.key_events_base()
                                                if self.key == 10:
                                                    self.delete_filter_from_database(
                                                        keyword=keyword)
                                                    self.key = 113

                                    # After deletion of a keyword, move the selector back to the category box at the previously selected category.
                                    self.display.selector_position = self.display.marked_category

                                # Update the info-box
                                self.info.display_info()
                                # After deletion of either category or keyword
                                self.display.clear_frame()
                                # Update the dict from the database after deleting filter.
                                self.categories = self.fetch_filters_from_db()
                                # Re-initate the data used for drawing assets.
                                self.display.start_filter_selection(self.categories, "category", "del")
                                if self.categories:
                                    self.key = -1
                                else:
                                    self.key = 113

                        # When leaving filter management, returning to the "filters" sub-menu
                        self.key = -1
                        self.back_to_sub_menu("filters")

                # Set GUI assets to main menu view
                self.back_to_main_menu()

            elif self.key == 10 and self.menu.marker_position == 3:
                # ANALYSIS options, while loop and key events to come.

                self.categories = self.fetch_filters_from_db()
                stats = Statistics(self.db)

                self.menu.marker_position = 1
                self.menu.draw_sub_menu("analysis")

                while self.key != 113:
                    self.key_events_menu(self.menu.options["analysis"].keys())

                    if self.key == 10 and self.menu.marker_position == 1:
                        # CHART DISPLAY - top keywords of all time

                        df_keyw_hits = stats.top_keywords()

                        self.display.draw_top_list(type="keywords", data=df_keyw_hits)

                    elif self.key == 10 and self.menu.marker_position == 2:
                        # CHART DISPLAY - top categories of all time

                        df_top_categories = stats.top_categories()

                        self.display.draw_top_list(type="categories", data=df_top_categories)

                    elif self.key == 10 and self.menu.marker_position == 3:

                        # CHART DISPLAY - top 3 categories day by day

                        df_top_categories = stats.cateogories_by_date()
                        try:
                            self.display.draw_grouped_graph(header="Top 3 categories, by date (scrape date)", data=df_top_categories)
                        except Exception as e:
                            logging.info(e, exc_info=True)

                    elif self.key == 10 and self.menu.marker_position == 5:
                        self.export_urls()

                # Set GUI assets to main menu view
                self.back_to_main_menu()
        self.quit()

    def quit(self) -> None:
        curses.endwin()
        print("\nThank you for using NEWS BOT 2000.\n")
        exit()


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")

    size = os.get_terminal_size()
    if size.columns < 170 or size.lines < 50:
        print(f"""Failed to run program.\nTerminal dimensions: ({size.lines}, {size.columns})\nRequired dimensions: (50, 170)\n""")
        exit()

    logging.basicConfig(filename="error_log.txt", level=logging.INFO)

    try:
        NewsBot2000().main()

    except Exception as e:
        logging.error(e, exc_info=True)
        curses.endwin()
        raise
