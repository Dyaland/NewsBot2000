from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
import re


class TextCleaner:
    """Contains methods for processing texts."""

    stop_words = STOP_WORDS
    
    # Remove som symbols from punctuation for manual cleaning.
    punct = re.sub("'|-|@", "", punctuation)
    punct += "—“”"   # Add some rare cases.

    def clean_text(self, text: str) -> str:
        """Cleans a text from all punctuations and general words."""

        def is_compound(word: str) -> bool:
            """Checks that a word contains hyphen(s) somewhere (not beginning or end), and has no numerics."""

            if not re.search(r"^[a-z]+.*-.*[a-z]+$", word):
                return False
            for part in word.split("-"):
                if len(part) > 0 and not part.isalpha():
                    return False
            return True

        # Remove punctuation
        for char in self.punct:
            text = text.replace(char, "")

        # Remove apostrophes and their ending tails, leaving the base words.
        text = re.sub("'\w\s|'\s|’\w\s|’\s", " ", text)

        # Split text into a list of words
        words_list = text.lower().split()

        # Remove common words and words containing numerics from the list of words, keeping compound words (like-this-one).
        cleaned_words = [word for word in words_list if is_compound(word) or word.isalpha() and word not in self.stop_words and len(word) != 1]

        # Turn list of useful words back into string
        return " ".join(cleaned_words)