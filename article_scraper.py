import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re


class ArticleScraper:
    """Class containing web-scrapers for several news sites"""

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    def scrape_text(self, url: str, tag_regex: str, tag_blacklist: list) -> str:
        """Scrapes text from a news article by targetting a div or paragraphs."""

        self.tag_blacklist = []
        if tag_blacklist:
            self.tag_blacklist += tag_blacklist

        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                logging.warning(f"{response.status_code} url")
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            logging.warning(e, exc_info=True)
            return

        # Find tags by tag_name
        div = soup.find(class_=re.compile(tag_regex))
        if not div:
            div = soup.find(id=re.compile(tag_regex))

        if div is None:
            logging.warning(
                f"{datetime.now()} Found no tag div named '{tag_regex}' in {url}")
            raise TypeError("Requested div was not found in the url.")

        # Extract the article text paragraphs, method depending on tag type targeted
        paragraphs = [p for p in div.find_all("p") if p.parent.name != "figcaption"]

        if len(paragraphs) < 7:
            paragraphs = div.find_all(class_=re.compile("paragraph"))

        # if it's still not enough "content" we raise a Value Error
        if len(paragraphs) < 7:
            logging.warning(f"{datetime.now()} Found no tag div named '{tag_regex}' in {url}")
            raise TypeError("Too few paragraphs found.")

        article_paragraphs = []
        for paragraph in paragraphs:
            p_attrs_list = list(paragraph.attrs.values())
            current_tagnames = [word for lst in p_attrs_list for word in lst if type(
                lst) is list] if p_attrs_list else []

            if any(re.search(filter_tag, p_tag) for p_tag in current_tagnames for filter_tag in tag_blacklist):
                continue

            article_paragraphs.append(paragraph)

        article_text = " ".join([p.get_text().strip()
                                for p in article_paragraphs])
        return article_text


if __name__ == "__main__":
    pass
    # # THE FOLLOWING ARE TESTS FOR ALL CURRENTLY ADDED SITES
    
    ns = ArticleScraper()

    # # HUFFPOST TEST
    # print(ns.scrape_text(
    #     url="https://www.huffpost.com/entry/king-charles-queen-camilla-covid-19_n_63ea78f1e4b0063ccb27caf8",
    #     tag_regex="entry__content",
    #     tag_blacklist=[r"author-card", r"slidedown"]))

    # # APNEWS TEST
    # print(ns.scrape_text(
    #     url="https://apnews.com/article/indonesia-business-climate-and-environment-dc31d840d9016b8fa946fe431fdb64fe",
    #     # tag_regex=r"Article|article-",
    #     tag_blacklist=[]))

    # # CNN TEST
    # print(ns.scrape_text(
    #     "https://edition.cnn.com/2023/02/03/africa/south-africa-tottenham-deal-intl",
    #     tag_regex=r"article__content|pg-rail-tall__body|BasicArticle__main|pg-special-article__body",
    # tag_blacklist=["footer"]
    # ))

    # # NEWS.COM.AU TEST
    # print(ns.text_scraper(
    #     "https://www.news.com.au/lifestyle/health/marburg-virus-kills-nine-in-equatorial-guinea-amid-fears-hundreds-of-people-are-infected/news-story/0c4339ed8c6a4a909b3932ff00021a55",
    #     # tag_regex="story-primary",
    #     tag_blacklist=["story-intro", "footer", "storyblock"]
    # ))

    # # LATIMES TEST
    # print(ns.text_scraper(
    #     url="https://www.latimes.com/world-nation/story/2023-02-21/putin-defends-ukraine-invasion-suspends-nuclear-pact-us",
    #     # tag_regex="story-body",
    #     tag_blacklist=["promo", "social-bar-heading"]
    # ))

    # # ALJAZEERA TEST
    # print(ns.scrape_text(
    #     "https://www.aljazeera.com/news/2023/2/15/russia-ukraine-war-list-of-key-events-day-357",
    #     tag_regex="wysiwyg"
    # ))