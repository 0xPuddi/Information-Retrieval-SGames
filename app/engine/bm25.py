
from collection.models.document import Document
from app.engine.indexer import DocumentInfoDTO, Indexer

import math

from utils.logger import LOGGER


class BM25():
    # parameters
    k1 = 1.2
    b = 0.75

    indexer: Indexer

    def __init__(self, indexer: Indexer):
        LOGGER.info("Initializing BM25...")
        self.indexer = indexer
        LOGGER.ok("BM25 Initialized")

    def idf(self, word: str) -> float:
        """
        Calculates IDF for word
        """
        n_documents = self.indexer.get_number_documents_containing_word(word)
        return math.log((self.indexer.collection_documents_number - n_documents + 0.5) / (n_documents + 0.5) + 1)

    def word_score(self, word: str, document_word_frequency: int, document_words_length: int) -> float:
        """
        Calculates score for the single word
        """
        idf = self.idf(word)
        top = document_word_frequency * (self.k1 + 1)
        bottom = document_word_frequency + self.k1 * \
            (1 - self.b + self.b * (document_words_length /
                                    self.indexer.average_document_length))
        return idf * (top / bottom)

    def get_collection_documents(self, indexes: list[tuple[tuple[str, int], int]]) -> list[Document]:
        """
        Reads collection
        Can be improved by ready chunks, and indexing using matched indexes

        list holds: tuple[tuple[collection_name, index], score]

        We need to preserve the order coming from list
        """
        LOGGER.info("Loading documents from disk...")
        # build list of collections name
        collection_names_indexes: list[str] = []
        for idx in indexes:
            collection_name = idx[0][0]

            if collection_name in collection_names_indexes:
                continue
            collection_names_indexes.append(collection_name)

        # now load one collection at a time and build list
        documents: list[Document] = [None for _ in indexes]
        # insert
        for coll_name in collection_names_indexes:
            collection: list[Document] = self.indexer.read_collection_by_name(
                coll_name)
            for i, indx in enumerate(indexes):
                if indx[0][1] < len(collection):
                    documents[i] = collection[indx[0][1]]
        LOGGER.ok("Documents loaded from disk")
        return documents

    def query_sources_documents(self, query_words: list[str], number_returned_documents: int) -> list[Document]:
        """
        Calculates matches and return best matched documents

        Given that we have query words as inputs and that the iteration
        has to move for a document over all query words but we have an inverted
        index that goes from words to indexes we operate this way:

        - We iterate over all query words
        - For each word we calculate that document score for such word
        - We keep an hash table (dict) with index to document score
        - Each document score we add it to the dictionary, new entry we set old entry we add
        - At the end all documents that have query words have been fetched and scored
        - We keep top x results
        """
        # compute documents score
        # dictionary is (collection_name, index) -> score
        LOGGER.info("Computing words scores...")

        LOGGER.info(f"words\n\n{query_words}")
        docs_scores: dict[tuple[str, int], int] = {}
        for word in query_words:
            documents: list[DocumentInfoDTO] = self.indexer.get_documents_for_word(
                word)

            for doc in documents:
                score = self.word_score(
                    word, doc.word_frequency_within_document, doc.words_length)
                key = (doc.collection_name, doc.index)
                if key in docs_scores:
                    docs_scores[key] += score
                else:
                    docs_scores[key] = score
        LOGGER.ok("Words scores computed")

        #
        if len(docs_scores) == 0:
            LOGGER.warn("No documents scores")
            return []

        # keep only best number_returned_documents matches out
        # of all docs_scores
        LOGGER.ok(f"Getting best {number_returned_documents} matches...")
        matches: list[tuple[tuple[str, int], int]] = []
        for doc, score in docs_scores.items():
            if len(matches) == 0:
                matches.append((doc, score))

            for i in range(len(matches)):
                if matches[i][1] > score:
                    # append and break if it is the last and not yet at capacity
                    if len(matches) < number_returned_documents:
                        matches.append((doc, score))
                        break
                    continue

                # otherwise slide array
                tmp = matches[i]
                matches[i] = (doc, score)

                for j in range(i + 1, len(matches)):
                    next_tmp = matches[j]
                    matches[j] = tmp
                    tmp = next_tmp

                # if not max capacity append
                if len(matches) < number_returned_documents:
                    matches.append(tmp)
                break

        LOGGER.info(f"matched scores\n\n{matches}")

        # return best from disk given collection name and index
        LOGGER.ok(
            f"Query Matches Computed, documents matched: {len(matches)} / {number_returned_documents}")
        return self.get_collection_documents(matches)
