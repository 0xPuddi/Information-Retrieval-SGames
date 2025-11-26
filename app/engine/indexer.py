
from collections import Counter
import hashlib
import json
from pathlib import Path
import duckdb
from pydantic import BaseModel, ValidationError
from duckdb import DuckDBPyConnection

from app.engine.parser import Parser
from collection.models.document import Document
from utils.logger import LOGGER


# document for document informations
class DocumentRef(BaseModel):
    collection_name: str
    index: int
    words_length: int


# postings for word-document informations
class Postings(BaseModel):
    word_frequency_within_document: int
    document: DocumentRef


# lexicon for word informations
class Lexicon(BaseModel):
    word: str
    collection_frequency: int

    postings: list[Postings]


class DocumentInfoDTO(BaseModel):
    collection_name: str
    index: int
    word_frequency_within_document: int
    words_length: int


class Indexer():
    # constans
    COLLECTION_FOLDER: str = "collection"
    DATABASE_PATH: str = "app/engine/db/main.duckdb"

    # modules
    connection: DuckDBPyConnection
    parser: Parser

    # collection related info
    collection_hash: str
    collection_documents_number = 0
    average_document_length = 0

    def __init__(self, parser: Parser):
        if not parser:
            raise Exception("Parser and db connection are needed")
        self.parser = parser

        # connect to db
        db_path = Path(self.DATABASE_PATH)
        # make folder if missing
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = duckdb.connect(db_path)

        LOGGER.info("Initializing indexer...")

        # load collection json
        LOGGER.info("Reading collection...")
        collection = self.read_collection_files()

        if len(collection) == 0:
            LOGGER.error("Collection is empty")
            LOGGER.warn("Not initializing indexer")
            self.connection.close()
            return
        LOGGER.ok("Collection read")

        if self.load_collection_related_information():
            if not self.has_collection_changed(collection):
                # build index
                LOGGER.ok("Collection hasn't changed skipping index build")
                return

        # build index
        LOGGER.info("Building Inverted Index...")

        # clear preemprively
        LOGGER.info("Clearing DB...")
        self.clear_db()
        LOGGER.ok("DB Cleared")

        # we build the index by building Lexicon and Postings classes
        lexicon_list = self.build_inverted_index(collection)
        # compute hash
        self.collection_hash = self.hash_collection(collection)
        # save collection related info to db for quick reload
        self.save_collection_related_informations()

        # then we load them on the duckbd in-memory database
        # create tables
        self.create_inverted_index_tables(self.connection)
        # populate tables
        self.insert_lexicon(self.connection, lexicon_list)
        LOGGER.ok("Inverted Index built")
        LOGGER.ok("Indexer Initialized")

    def has_collection_changed(self, collection: list[list[Document]]):
        """
        Returns true if the collection has changed, as we need to trigger the inverted index rebuild
        """
        hash = self.hash_collection(collection)
        return hash != self.collection_hash

    def hash_collection(self, collection: list[list[Document]]) -> str:
        """
        Compute a deterministic hash for a collection of documents.
        """
        json_string = "".join(
            doc.model_dump_json() for file_docs in collection for doc in file_docs
        )
        return hashlib.sha256(json_string.encode("utf-8")).hexdigest()

    def clear_db(self):
        """
        Clears db: close connection, delete file, re-establish connection
        """
        self.connection.close()

        db_path = Path(self.DATABASE_PATH)
        if db_path.exists():
            db_path.unlink()

        self.connection = duckdb.connect(db_path)

    def load_collection_related_information(self) -> bool:
        """
        Loads collection related infos from db
        """

        # try to load info
        try:
            row = self.connection.execute(
                "SELECT data FROM collection_info").fetchone()
        except Exception as _:
            return False

        if row:
            info = json.loads(row[0])
            self.collection_documents_number = info.get(
                "collection_documents_number", None)
            self.average_document_length = info.get(
                "average_document_length", None)
            self.collection_hash = info.get("collection_hash", None)

            if not self.collection_documents_number or not self.average_document_length or not self.collection_hash:
                return False
            return True
        else:
            return False

    def save_collection_related_informations(self):
        """
        Saves collection related data to db
        """
        # prepare data
        info = {
            "collection_documents_number": self.collection_documents_number,
            "average_document_length": self.average_document_length,
            "collection_hash": self.collection_hash
        }

        # create table if not there
        self.connection.execute("""
CREATE TABLE IF NOT EXISTS collection_info (
		data JSON
)
""")

        # save data as json
        self.connection.execute("DELETE FROM collection_info")
        self.connection.execute(
            "INSERT INTO collection_info VALUES (?)", [json.dumps(info)])

    def build_inverted_index(self, collection: list[list[Document]]) -> list[Lexicon]:
        """
        Naive inverted index algorithm. We do:

        - build a dict of word -> Lexicon so that we efficiently add words
        - add Postings and Document to each word
        - convert dict into list of Lexicon

        While we do so we also compute collection related infomations:
        - collection_documents_number
        - average_document_length
        """
        total_documents_words_length = 0
        words_lexicon: dict[str, Lexicon] = {}
        for col in collection:
            collection_size = len(col)
            LOGGER.info(
                f"Processing sub-collection of size: {collection_size}")
            self.collection_documents_number += collection_size
            for idx, doc in enumerate(col):
                words = self.parser.parse_text_to_words(doc.metadata.text)
                total_documents_words_length += len(words)

                # we build a word -> frequency dict and operate on that
                words_freq = Counter(words)

                # add document to words
                for word, freq in words_freq.items():
                    # document related information for word
                    doc_ref = DocumentRef(
                        collection_name=doc.source.name, index=idx, words_length=len(words))
                    posting = Postings(
                        word_frequency_within_document=freq, document=doc_ref)

                    if word in words_lexicon:
                        # update lexicon entry
                        words_lexicon[word].collection_frequency += freq
                        words_lexicon[word].postings.append(posting)
                    else:
                        # create lexicon entry
                        lexicon = Lexicon(
                            word=word, collection_frequency=freq, postings=[posting])
                        words_lexicon[word] = lexicon
                if idx % 250 == 0:
                    LOGGER.ok(
                        f"Processed : {idx} / {collection_size}")
                if idx == collection_size:
                    LOGGER.ok(
                        f"Processed : {idx} / {collection_size}")

            LOGGER.ok(f"Processed collection")

        self.average_document_length = total_documents_words_length / \
            self.collection_documents_number
        return [value for _, value in words_lexicon.items()]

    def create_inverted_index_tables(self, con: DuckDBPyConnection):
        """
        Create tables for inverted index
        """
        LOGGER.info("Creating Lexicon, Postings and DocumentRef tables...")
        # documents table adn id sequence
        con.execute("CREATE SEQUENCE seq_document START 1")
        con.execute("""
CREATE TABLE IF NOT EXISTS documents (
																document_id INTEGER PRIMARY KEY DEFAULT nextval('seq_document'),

																collection_name VARCHAR NOT NULL,
																index INTEGER NOT NULL,
																words_length INTEGER NOT NULL,

																UNIQUE(collection_name, index)
)
""")

        # lexicon table
        # we dont use varchar as primary key because in postings would take a lot
        # of space when referenced each time
        con.execute("CREATE SEQUENCE seq_lexicon START 1")
        con.execute("""
CREATE TABLE IF NOT EXISTS lexicon (
																word_id INTEGER PRIMARY KEY DEFAULT nextval('seq_lexicon'),

																word VARCHAR UNIQUE NOT NULL,
																collection_frequency INTEGER NOT NULL
)
""")

        # Create postings table (many-to-many)
        con.execute("CREATE SEQUENCE seq_postings START 1")
        con.execute("""
CREATE TABLE IF NOT EXISTS postings (
																posting_id INTEGER PRIMARY KEY DEFAULT nextval('seq_postings'),

																lexicon_id INTEGER NOT NULL,
																document_id INTEGER NOT NULL,
																word_frequency_within_document INTEGER NOT NULL,

																FOREIGN KEY (lexicon_id) REFERENCES lexicon(word_id),
																FOREIGN KEY (document_id) REFERENCES documents(document_id),
																UNIQUE(lexicon_id, document_id)
)
""")

        # indexes for better query performance
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_postings_lexicon ON postings(lexicon_id)")
        con.execute(
            "CREATE INDEX IF NOT EXISTS idx_postings_document ON postings(document_id)")
        LOGGER.ok("Tables created")

    def insert_lexicon(self, con: DuckDBPyConnection, lexicon_list: list[Lexicon]):
        """
        Insert lexicon into tables, handling Documents duplicates.
        """
        LOGGER.info("Inserting computed Inverted index in database...")

        # collect unique documents: (collection_name, index) -> words_length
        documents_map = {}
        for lexicon_entry in lexicon_list:
            for posting in lexicon_entry.postings:
                doc = posting.document
                key = (doc.collection_name, doc.index)
                if key not in documents_map:
                    documents_map[key] = doc.words_length

        # insert unique documents
        con.executemany(
            """
INSERT INTO documents (collection_name, index, words_length)
VALUES (?, ?, ?)
""",
            [(key[0], key[1], value)
             for key, value in documents_map.items()]
        )
        LOGGER.ok("DocumentsRef inserted")

        # insert lexicon entries, already unique
        con.executemany(
            """
INSERT INTO lexicon (word, collection_frequency)
VALUES (?, ?)
""",
            [(e.word, e.collection_frequency)
             for e in lexicon_list])
        LOGGER.ok("Lexicon inserted")

        # insert postings that reference lexicon and document rows
        postings_data = []
        for lexicon_entry in lexicon_list:
            for posting in lexicon_entry.postings:
                doc = posting.document
                postings_data.append((
                    lexicon_entry.word,
                    doc.collection_name,
                    doc.index,
                    posting.word_frequency_within_document
                ))

        # given values: word, (collection_name, index) we fetch proper ids to build references
        # within the table
        con.executemany(
            """
INSERT INTO postings (lexicon_id, document_id, word_frequency_within_document)
																VALUES (
																																(SELECT word_id FROM lexicon WHERE word = ?),
																																(SELECT document_id FROM documents WHERE collection_name = ? AND index = ?),
																																?
																)
""",
            postings_data
        )
        LOGGER.ok("Postings inserted")

    def read_collection_files(self) -> list[list[Document]]:
        """
        Load all JSON files from collection directory.
        Returns a list of lists of Source objects, one list per file.
        """
        collection_dir = Path(self.COLLECTION_FOLDER)
        all_collections = []

        if not collection_dir.exists():
            print(
                f"[read_collection_files] Directory not found: {collection_dir}")
            return all_collections

        # we need determinism as has of documents is used
        for json_file in sorted(collection_dir.glob("*.json")):
            # get filename without extension
            name = json_file.stem
            documents = self.read_collection_by_name(name)
            if documents and 0 < len(documents):
                all_collections.append(documents)
            LOGGER.ok(f"Read {json_file}.json")
        return all_collections

    def read_collection_by_name(self, name: str) -> list[Document]:
        """
        Load a specific collection JSON file by name and parse as Document objects.
        """
        collection_file = Path(self.COLLECTION_FOLDER) / f"{name}.json"
        documents = []

        if not collection_file.exists():
            print(
                f"[read_collection_by_name] File not found: {collection_file}")
            return documents

        try:
            with open(collection_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                print(
                    f"[read_collection_by_name] Error: {collection_file.name} is not an array")
                return documents

            # parse each item as a Source object
            for item in data:
                try:
                    doc = Document(**item)
                    documents.append(doc)
                except ValidationError as e:
                    print(
                        f"[read_collection_by_name] Validation error in {collection_file.name}: {e}")
                    continue

        except json.JSONDecodeError as e:
            print(
                f"[read_collection_by_name] Error parsing {collection_file.name}: {e}")
        except Exception as e:
            print(
                f"[read_collection_by_name] Error reading {collection_file.name}: {e}")

        return documents

    def get_number_documents_containing_word(self, word: str) -> int:
        # fetch the lexicon id of word
        # then count postings entries that reference such id
        result = self.connection.execute("""
SELECT COUNT(*) 
FROM postings 
WHERE lexicon_id = (SELECT word_id FROM lexicon WHERE word = ?)
																																																																""", [word]).fetchone()

        freq = result[0] if result else 0
        return freq

    def get_documents_for_word(self, word: str) -> list[DocumentInfoDTO]:
        results = self.connection.execute("""
SELECT d.collection_name, d.index, p.word_frequency_within_document, d.words_length
FROM lexicon l
JOIN postings p ON l.word_id = p.lexicon_id
JOIN documents d ON p.document_id = d.document_id
WHERE l.word = ?
																																																""", [word]).fetchall()

        return [DocumentInfoDTO(
                collection_name=r[0], index=r[1], word_frequency_within_document=r[2], words_length=r[3]) for r in results]
