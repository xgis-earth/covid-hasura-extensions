from fastapi import APIRouter, Response
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from os import environ as env
from app.hasura import SessionVars
import requests
import json


api_key = env.get("MEDIASTACK_API_KEY")
api_base_url = "http://api.mediastack.com/v1/"


class Action(BaseModel):
    name: str


class Input(BaseModel):
    country_code: str
    limit: Optional[int]
    offset: Optional[int]


class Args(BaseModel):
    session_variables: SessionVars
    input: Input
    action: Action


class Item(BaseModel):
    title: str
    description: str
    url: str
    image_url: Optional[str]
    category: str
    language: str
    country: str
    published_at: datetime
    source: str


query_country_news = APIRouter()


@query_country_news.post("/", response_model=List[Item])
async def handle_items_request(args: Args, response: Response) -> Optional[List[Item]]:
    country_code = args.input.country_code.lower()

    # Handle limit and offset inputs.
    limit = args.input.limit or 10
    if limit > 100:
        limit = 100
    offset = args.input.offset or 0

    countries = country_code
    sources = ""
    if country_code == "gb":
        countries = f"{countries},-us"
        sources = "-mail,-thesun"

    url = f"{api_base_url}news" \
          f"?access_key={api_key}" \
          f"&limit={limit}" \
          f"&offset={offset}" \
          f"&countries={countries}" \
          f"&sources={sources}" \
          f"&sort=published_desc" \
          f"&keywords=covid+coronavirus"

    r = requests.get(url)
    r.raise_for_status()
    json_response = json.loads(r.text)

    items = []

    for item in json_response["data"]:
        items.append(Item(
            title=item["title"],
            description=item["description"],
            url=item["url"],
            image_url=item["image"],
            category=item["category"],
            language=item["language"],
            country=item["country"],
            published_at=item["published_at"],
            source=item["source"],
        ))

    return items
