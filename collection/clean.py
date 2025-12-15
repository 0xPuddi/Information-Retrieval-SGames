

import json
from pathlib import Path

from pydantic import ValidationError
from collection.models.document import Document
from utils.logger import LOGGER


def save_collection(
        name: str,
        docs: list[Document],
):
    path = Path(f"./collection/{name}-clean.json")

    # append
    data = []
    for d in docs:
        data.append(d.model_dump(mode="json"))
    # write
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def read_collection(
        name: str,
) -> list[Document]:
    path = Path(f"./collection/{name}.json")

    # read
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    if not isinstance(data, list):
        print(
            f"[read_collection_by_name] Error: {name} is not an array")
        return documents

    # parse each item as a Source object
    for item in data:
        try:
            doc = Document(**item)
            documents.append(doc)
        except ValidationError as e:
            print(
                f"[read_collection_by_name] Validation error in {name}: {e}")
            continue

    return documents


def before_q(s: str) -> str:
    # for steam we truncate:
    # https://store.steampowered.com/app/3014320/OCTOPATH_TRAVELER_0?snr=1_5_9__300
    # https://store.steampowered.com/app/3014320/OCTOPATH_TRAVELER_0/?snr=1_4_4__tab-TrendingFree
    # to
    # https://store.steampowered.com/app/3014320/OCTOPATH_TRAVELER_0
    # others dont need it
    return s.split('?', 1)[0][:-1] if s.split('?', 1)[0][-1] == '/' else s.split('?', 1)[0]


NAME = "gamejolt"
if __name__ == "__main__":
    # read coll
    docs = read_collection(NAME)

    # filter coll
    once = False
    filtered_docs: list[Document] = []
    for d in docs:
        present = False
        for fd in filtered_docs:
            # if not once and d.metadata.title == "No Man's Sky" and fd.metadata.title == "No Man's Sky":
            #     LOGGER.info(
            #         f"found same game: {d.metadata.title}, {before_q(d.source.url.__str__())} - {fd.metadata.title}, {before_q(fd.source.url.__str__())}")
            #     once = True
            if d.metadata.title == fd.metadata.title and before_q(d.source.url.__str__()) == before_q(fd.source.url.__str__()):
                LOGGER.info(
                    f"found same game: {d.metadata.title}, {d.source.url} - {fd.metadata.title}, {fd.source.url}")
                present = True
                break

        if not present:
            filtered_docs.append(d)

    # save coll
    save_collection(NAME, filtered_docs)
