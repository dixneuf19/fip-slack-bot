from typing import List, Optional, Dict

from pydantic import BaseModel


class Track(BaseModel):
    title: str
    album: str
    artist: str
    year: Optional[int]
    label: Optional[str]
    musical_kind: Optional[str]
    external_urls: Dict[str, str] = {}
    cover_url: Optional[str]


class ExternalURL(BaseModel):
    url: str
    provider: str
    name: str


class Radio(BaseModel):
    name: str
    url: str


FIP_RADIO = Radio(name="FIP", url="https://www.fip.fr")
MEUH_RADIO = Radio(name="RadioMeuh", url="https://www.radiomeuh.com/")
