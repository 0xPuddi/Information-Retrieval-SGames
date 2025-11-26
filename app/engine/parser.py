
import string

import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords

from utils.logger import LOGGER


class Parser():
    stemmer: PorterStemmer

    def __init__(self):
        LOGGER.info("Initializing parser...")
        self.stemmer = PorterStemmer()
        nltk.download('stopwords')
        LOGGER.ok("Parser Initialized")

    def tokenizer(self, text: str) -> str:
        """
        Tokenizer removes all punctuation, excessive whitespace and returns all words lowercase
        """
        # punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))

        # return words in lowercase
        return [word.lower() for word in text.split() if word]

    def stopwords_removal(self, words: list[str]) -> list[str]:
        """
        Remove stopwords
        """
        # remove english stopwords
        stop_words = set(stopwords.words('english'))
        return [word for word in words if word not in stop_words]

    def stemming(self, words: list[str]) -> list[str]:
        """
        Stem words
        """
        # stem each word
        return [self.stemmer.stem(word) for word in words]

    def parse_text_to_words(self, text: str) -> list[str]:
        """
        Takes a text and converts it to words to be used within bm25
        """
        words = self.tokenizer(text)
        return self.stemming(self.stopwords_removal(words))
