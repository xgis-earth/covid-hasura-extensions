from fastapi import APIRouter, Response, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.country_codes import alpha3_lookup
from app.hasura import SessionVars
import requests
import json


base_url = "https://services3.arcgis.com/t6lYS2Pmd8iVx1fy/ArcGIS/rest/services/"
airline_url = f"{base_url}COVID_Airline_Information_V2/FeatureServer/0/query"


class Action(BaseModel):
    name: str


class Input(BaseModel):
    country_code: str


class Args(BaseModel):
    session_variables: SessionVars
    input: Input
    action: Action


class AirlineInfo(BaseModel):
    name: str
    info: str
    source: str
    published: datetime


query_country_airline_info = APIRouter()


@query_country_airline_info.post("/", response_model=List[AirlineInfo])
async def handle_info_request(args: Args, response: Response) -> Optional[List[AirlineInfo]]:
    country_code = args.input.country_code.lower()

    if country_code.upper() not in alpha3_lookup:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return None

    alpha3 = alpha3_lookup[country_code.upper()]

    r = requests.post(airline_url, data={
        "f": "json",
        "where": "1=1",
        "outFields": "*"
    })

    r.raise_for_status()
    json_response = json.loads(r.text)

    airlines = []

    for item in json_response["features"]:
        attributes = item["attributes"]
        if attributes["iso3"] != alpha3:
            continue

        airlines.append(AirlineInfo(
            name=attributes["airline"],
            info=attributes["info"],
            source=attributes["source"],
            published=datetime.strptime(attributes["published"], '%d.%m.%Y')
        ))

    return airlines
