from collections import defaultdict
import pandas as pd
import re
import logging

import sql_manager as sql


class Statistics:
    """Uses Pandas to sift through and analyze data."""

    def __init__(self, database):

        self.db = database

        # Articles from sql table
        self.articles_sql = sql.execute_query(self.db, "SELECT * FROM articles;")
        # Dataframe from articles table in sql database
        self.df_articles = pd.DataFrame(self.articles_sql, columns=["url", "date", "text"])
        # Create a single list of all article words, not changing their original order within the texts
        self.article_texts_list = (article[2].split() for article in self.articles_sql)
        # All articles' words in a list
        self.articles_words_list = (word for lst in self.article_texts_list for word in lst)

        # Text filters from sql table
        self.keywords_sql = sql.execute_query(self.db, """
                                  SELECT keyword, cat.category FROM keywords
                                  JOIN categories cat ON category_id = cat.id;""")

        # Keywords consisting of a single word.
        self.single_keywords = [(keyword, category) for keyword, category in self.keywords_sql if " " not in keyword]
        # Key phrases consisting of multiple words.
        self.phrase_keywords = [(keyword, category) for keyword, category in self.keywords_sql if " " in keyword]

    def _classify_text(self, text):
        """Decides the main category of a text based on keyword hits."""

        # # # KEYWORD PHRASES HITS (multiple word key phrases)

        category_hits = defaultdict(int)
        for phrase, category in self.phrase_keywords:
            category_hits[category] += len(re.findall(phrase, text))

        # # # SINGLE KEYWORDS HITS

        # Get a word count of unique words in all articles.
        article_words = text.split()
        for keyword, category in self.single_keywords:
            category_hits[category] += article_words.count(keyword)

        # Determine the most common category among keyword hits
        category, count = list(category_hits.keys()), list(category_hits.values())
        main_category = [category[count.index(max(count))]][0]

        # Return the category with the most hits.
        return main_category

    def top_keywords(self) -> pd.DataFrame:
        """Count keyword hits in all articles, using different methods for single word keywords and multiple word phrases, for better speed."""

        # # # KEYWORD PHRASES HITS (multiple word key phrases)

        # Counting phrase hits for rows with "phrase_hit" == True
        phrases_hit_count = defaultdict(int)
        for article in self.df_articles["text"]:
            for phrase, _ in self.phrase_keywords:
                phrases_hit_count[phrase] += len(re.findall(phrase, article))
        df_phrases_hits = pd.DataFrame(
            phrases_hit_count.items(), columns=["phrase", "count"])

        # # # SINGLE KEYWORD HITS (single word keywords)

        # Get a word count of unique words in all articles.
        words_count = defaultdict(int)
        for word in self.articles_words_list:
            words_count[word] += 1
        df_all_articles_words_count = pd.DataFrame(words_count.items(), columns=["word", "count"])

        # # # Finalize data

        # Dataframe from keywords/categories table in sql database
        df_keywords = pd.DataFrame(self.keywords_sql, columns=["keyword", "category"])
        # By merging keywords table with article words counts, we get a DF with single keyword hit counts
        df_singles_result = df_keywords.merge(df_all_articles_words_count, left_on="keyword", right_on="word")
        del df_singles_result["word"]
        # By merging keywords table with phrases hit counts, we get a DF of all phrases hit counts.
        df_phrases_result = df_keywords.merge(df_phrases_hits, left_on="keyword", right_on="phrase")
        del df_phrases_result["phrase"]

        # Merging the hit count DFs for phrases and single keywords
        df_output = pd.concat([df_singles_result, df_phrases_result])

        df_output = df_output.sort_values(by=["count"], ascending=False)
        # Sort dataframe by count
        return df_output

    def top_categories(self):
        """Counts articles per category and groups by date."""

        categorized_articles = defaultdict(int)
        for article in self.df_articles["text"]:

            # Run _classify_text on the article, getting the most prominent category for the article..
            main_category = self._classify_text(article)

            categorized_articles[main_category] += 1

        # # # Finalize data

        # Create a dataframe
        df_output = pd.DataFrame(categorized_articles.items(), columns=["category", "count"])
        # Sort dataframe bycount
        df_output = df_output.sort_values(by="count", ascending=False)

        return df_output

    def cateogories_by_date(self):
        """Isolate top 3 article category count per day (scrape-date)"""

        # Make a working copy of the articles dataframe, leaving out the url column.
        df_articles = self.df_articles[["date", "text"]]

        # Run the text classfier on each article and add the main category to the new "label" column.
        df_articles["label"] = df_articles["text"].apply(self._classify_text)
        df_grouped_by = df_articles.groupby(['date', 'label']).size().reset_index(name='count')

        # Pivot the table and put labels (categories) as columns. 
        pivoted = df_grouped_by.pivot(index='date', columns='label', values='count')

        # get the labels with the three highest values for each date, and keep the values
        top_three = pivoted.apply(lambda x: x.nlargest(3), axis=1)

        # reset the index of the resulting DataFrame
        top_three = top_three.reset_index()

        # melt the DataFrame so that each label has its own row
        melted = top_three.melt(id_vars='date', var_name='label', value_name='count')

        # sort the DataFrame by date and count
        sorted_df = melted.sort_values(['date', 'count'], ascending=[True, False])

        # group the DataFrame by date and keep only the top 3 categories per date.
        top_three_by_date = sorted_df.groupby('date').head(3)

        # Sort the DataFrame by date first, and then by count, so all the data is in the correct order.
        df_output = top_three_by_date.sort_values(by=['date', 'count'], ascending=[False, False])
        return df_output