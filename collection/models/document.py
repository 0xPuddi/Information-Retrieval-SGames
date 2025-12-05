from typing import Optional
from pydantic import BaseModel, HttpUrl


class Source(BaseModel):
    name: str
    url: HttpUrl


class Metadata(BaseModel):
    title: str
    description: str  # this is text/html

    videos: Optional[list[str]]
    images: Optional[list[str]]

    price: Optional[float | str | list[dict[str, float | str]]]

    author: str
    status: Optional[str]

    category: Optional[str]
    genre: Optional[list[str]]
    rating: Optional[float | str]
    tags: Optional[list[str]]
    platforms: Optional[list[str]]
    published: Optional[str]

    # unlabeled key-value data that has been found
    extra_data: dict

    # whole text structure of the document for semantic search
    text: str


class Document(BaseModel):
    # hash of the string: "source.name-source.url-metadata.title"
    id: str
    # source specific info to distinguis: itchio, steam, gamejolt
    source: Source
    # metadata realted to the document, base information scraped
    # that make a common ground (normalize) between different sources
    # to make a homogeneous collection structure we cna work with
    metadata: Metadata

    def model_dump(self, *args, **kwargs):
        # remove multiple modes passed in
        kwargs.pop("mode", None)
        # python mode serializes nested objects
        data = super().model_dump(*args, **kwargs, mode="python")
        data["source"]["url"] = str(data["source"]["url"])
        return data
