import requests
from bs4 import BeautifulSoup
import re
import logging


class UrlScraper:
    """Scrapes all article urls on a front page of a news site, based on specific input to finetune the filtering."""

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

    # This is the generic url blacklist, used to remove any links containg the strings inside.
    blacklist = [r"mailto:?"]
    
    def generator(self, site_url: str, regex_url_match: str = None, url_blacklist: list = None):
        """Fetches all urls, containing the required partial string, from a site.
           Domains are to be in the format like: "domain-name.com", without https:// and wwww"""

        if url_blacklist:
            # Expand the blacklist with site specific blacklist phrases, if any.
            self.blacklist += url_blacklist
        
        # Establish the current sites base domain, for adding to relative urls and making sure of not getting articles from other sites.
        base_domain = re.sub("/.*", "", site_url)

        try:
            response = requests.get("https://" + site_url, headers=self.headers)
            if response.status_code != 200:
                logging.warning(f"{response.status_code} url")
            soup = BeautifulSoup(response.text, "lxml")
        except Exception as e:
            logging.error(e, exc_info=True)
            return

        # Find all urls on the page, regardless of tag type (at least one site has urls in <h3> tags)
        for url in (tag["href"] for tag in soup.find_all(href=True)):
            
            # Don't scrapy any useless urls.
            if not re.search(rf"^/|^https://(www.)?{base_domain}", url):
                continue
                
            # Exclude site specific phrases in the urls, like "/gallery/" etc.
            if any(re.search(regex, url) for regex in self.blacklist):
                continue

            if regex_url_match:
                # Include only urls containing the required url component for that site, i.e. "/article/".
                if re.search(regex_url_match, url):
                    if url.startswith("/"):
                        url = "https://" + base_domain + url
                    yield url
            else:
                if url.startswith("/"):
                    url = "https://" + base_domain + url
                yield url


if __name__ == "__main__":
    
    # # THE FOLLOWING ARE TESTS FOR ALL CURRENTLY ADDED SITES

    scr = UrlScraper()

    # # No regex-tag TEST
    # for url in scr.generator("huffpost.com"):
    #     print(url)

    # # HUFFPOST TEST
    # for url in scr.generator("huffpost.com", r"/entry/", None):
    #     print(url)

    # # HUFFPOST TEST
    # for url in scr.generator("huffpost.com", "/entry/"):
    #     print(url)

    # # APNEWS TEST
    # for url in scr.generator("apnews.com", r"/article/.+", None):
    #     print(url)

    # # CNN TEST
    # for url in scr.generator("edition.cnn.com/world/united-kingdom", r"^/\d+/\d+/\d+/.*", [r".*/gallery/.*"]):
    #     print(url)

    # # NEWS.COM.AU TEST
    # for url in scr.generator("news.com.au", r".*/news-story/.*", None):
    #     print(url)

    # # LATIMES TEST
    # for url in scr.generator("latimes.com", r".*/story/.*", None):
    #     print(url)

    # # ALJAZEERA TEST
    # for url in scr.generator("aljazeera.com", r"/\d+/\d+/\d+/.*", [r".*/gallery/.*", r".*/liveblog/.*"]):
    #     print(url)
