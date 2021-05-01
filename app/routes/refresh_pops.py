from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from io import BytesIO
from io import TextIOWrapper
from zipfile import ZipFile
from app.db import get_conn
import psycopg2
import traceback
import requests
import csv
import json

url = "http://api.worldbank.org/v2/en/indicator/SP.POP.TOTL?downloadformat=csv"


class Payload(BaseModel):
    action: str


class Args(BaseModel):
    payload: Payload


refresh_pops = APIRouter()


@refresh_pops.post("/", response_model=None)
async def handle_refresh_request(args: Args, response: Response) -> None:
    assert args.payload.action == "refresh"

    # Connect to database.
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        r = requests.get(url)
        r.raise_for_status()

        zipfile = ZipFile(BytesIO(r.content))
        for name in zipfile.namelist():
            if name.startswith("API_SP.POP.TOTL"):
                assert name.endswith(".csv")
                with TextIOWrapper(zipfile.open(name), encoding="utf-8") as f:

                    # Skip the first 4 header lines.
                    f.readline()
                    f.readline()
                    f.readline()
                    f.readline()

                    entries = []
                    years = 0

                    csv_reader = csv.DictReader(f)
                    for row in csv_reader:

                        if years == 0:
                            column_names = list(row.keys())
                            years = len(column_names) - 4

                        values = list(row.values())

                        entry = {
                            "name": values[0],
                            "alpha3": values[1],
                            "counts": []
                        }

                        # NOTE: Last column is blank and ignored here.
                        for i in range(years - 2):
                            value = values[i + 4]
                            value = 0 if value == '' else int(round(float(values[i + 4])))
                            entry["counts"].append(value)

                        entries.append(entry)

                    for entry in entries:
                        population = entry["counts"][-1]
                        counts = json.dumps(entry["counts"])
                        if entry["name"] == "World":
                            cur.execute("""
                                UPDATE region SET
                                    population = %s,
                                    population_time_series = %s
                                WHERE alpha3 = %s""", (population, counts, entry["alpha3"]))
                        else:
                            cur.execute("""
                                UPDATE country SET
                                    population = %s,
                                    population_time_series = %s
                                WHERE iso_alpha3 = %s""", (population, counts, entry["alpha3"]))

                # Exit loop after finding the required CSV file.
                break

        conn.commit()
        cur.close()
        return None

    except psycopg2.DatabaseError:
        print(f"EXCEPTION\n{traceback.format_exc()}")

    except:
        print(f"EXCEPTION\n{traceback.format_exc()}")

    finally:
        if conn is not None:
            conn.close()

    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return None
