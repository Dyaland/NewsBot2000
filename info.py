import curses
import re
from collections import defaultdict

import sql_manager as sql
from graph_plotter import CursedGraphs


class Info:

    def __init__(self, database) -> None:

        self.db = database
        self.graphs = CursedGraphs()
        
        curses.init_pair(1, curses.COLOR_YELLOW, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        self.YELLOW = curses.color_pair(1)
        self.CYAN = curses.color_pair(2)

        self.frame = curses.newwin(20, 26, 30, 5)
        
        self.frame.attrset(self.YELLOW)
        self.frame.border(0)
        self.frame.addstr(1, 1, "DATABASE INFORMATION".center(24))
        
        self.display_info()

    def display_info(self) -> None:
        """Dispaly a breakdown of statistics from the database."""
        
        # Tables counts
        article_count = len([row for row in sql.execute_query(
            self.db, "SELECT url from articles")])
        category_count = len([row for row in sql.execute_query(
            self.db, "SELECT category from categories")])
        keyword_count = len([row for row in sql.execute_query(
            self.db, "SELECT keyword from keywords")])

        self.frame.addstr(3, 1, "Tables data".center(24), self.YELLOW)
        self.frame.attrset(self.CYAN)
        self.frame.addstr(4, 2, f"Articles        :{article_count:5d}")
        self.frame.addstr(5, 2, f"Categories      :{category_count:5d}")
        self.frame.addstr(6, 2, f"Keywords        :{keyword_count:5d}")
        
        # Articles by domain 
        # Fetch urls from database
        article_urls = sql.execute_query(self.db, "SELECT url FROM articles")
        domains_data = defaultdict(int)
        # Count occurence of each domain
        for url in article_urls:
            domain = re.sub(r"^https://(www.)?|/.*", "", url[0])
            domains_data[domain] += 1
        
        #Put domain name and count in tuples in a list. Sort tuples by the count
        tuples = sorted([(label, value) for label, value in domains_data.items()], key=lambda a: a[1], reverse=True)
        
        # Display domain article counts.
        self.frame.addstr(8, 1, "Articles by domain".center(24), self.YELLOW)
        self.frame.attrset(self.CYAN)
        for i, tup in enumerate(tuples):
            name = tup[0] if len(tup[0]) <= 15 else tup[0][:10] + "[...]"
            self.frame.addstr(9 + i, 2, name)
            self.frame.addstr(9 + i, 18, ":")
            self.frame.addstr(9 + i, 19, f"{tup[1]:5d}")
            # Only shows top 10 domains
            if i == 9:
                break

        self.frame.refresh()