from fastapi import APIRouter, Response, status
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from markdownify import markdownify
from app.country_codes import alpha3_lookup
from app.hasura import SessionVars
import requests
import json


base_url = "https://services3.arcgis.com/t6lYS2Pmd8iVx1fy/ArcGIS/rest/services/"
travel_url = f"{base_url}COVID_Travel_Restrictions_V2/FeatureServer/0/query"


class Action(BaseModel):
    name: str


class Input(BaseModel):
    country_code: str


class Args(BaseModel):
    session_variables: SessionVars
    input: Input
    action: Action


class TravelInfo(BaseModel):
    info: str
    restrictions: str
    sources: str
    published: datetime


query_country_travel_info = APIRouter()


@query_country_travel_info.post("/", response_model=TravelInfo)
async def handle_info_request(args: Args, response: Response) -> Optional[TravelInfo]:
    country_code = args.input.country_code.lower()

    if country_code.upper() not in alpha3_lookup:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return None

    alpha3 = alpha3_lookup[country_code.upper()]

    r = requests.post(travel_url, data={
        "f": "json",
        "where": "1=1",
        "outFields": "*"
    })

    r.raise_for_status()
    json_response = json.loads(r.text)

    info = None
    restrictions = None
    sources = None
    published = None

    for item in json_response["features"]:
        attributes = item["attributes"]
        if attributes["iso3"] != alpha3:
            continue

        info = attributes["info"]
        info = info.replace("\n", "<br>")
        info = info.replace("• ", "<br><li>")
        info = markdownify(info)

        restrictions = attributes["optional2"]
        restrictions = restrictions.replace("\n", "<br>")
        restrictions = markdownify(restrictions)

        # sources = [s.strip() for s in str(attributes["sources"]).split('\n')]
        sources = attributes["sources"]
        sources = sources.replace("\n", "<br>")
        sources = markdownify(sources)

        published = datetime.strptime(attributes["published"], '%d.%m.%Y')

        break  # Done looping - only one item for country code here.

    result = TravelInfo(
        info=info,
        restrictions=restrictions,
        sources=sources,
        published=published
    )

    return result
