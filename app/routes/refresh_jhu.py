from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from io import StringIO
from app.db import get_conn
import psycopg2
import traceback
import requests
import csv
import json


base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/" \
           "csse_covid_19_time_series/"

confirmed_global_csv_url = f"{base_url}time_series_covid19_confirmed_global.csv"
deaths_global_csv_url = f"{base_url}time_series_covid19_deaths_global.csv"
recovered_global_csv_url = f"{base_url}time_series_covid19_recovered_global.csv"

country_mapping = {
    "Afghanistan": "AF",
    "Albania": "AL",
    "Algeria": "DZ",
    "Andorra": "AD",
    "Angola": "AO",
    "Antigua and Barbuda": "AG",
    "Argentina": "AR",
    "Armenia": "AM",
    "Australia": "AU",
    "Austria": "AT",
    "Azerbaijan": "AZ",
    "Bahamas": "BS",
    "Bahrain": "BH",
    "Bangladesh": "BD",
    "Barbados": "BB",
    "Belarus": "BY",
    "Belgium": "BE",
    "Benin": "BJ",
    "Bhutan": "BT",
    "Bolivia": "BO",
    "Bosnia and Herzegovina": "BA",
    "Brazil": "BR",
    "Brunei": "BN",
    "Bulgaria": "BG",
    "Burkina Faso": "BF",
    "Cabo Verde": "CV",
    "Cambodia": "KH",
    "Cameroon": "CM",
    "Canada": "CA",
    "Central African Republic": "CF",
    "Chad": "TD",
    "Chile": "CL",
    "China": "CN",
    "Colombia": "CO",
    "Congo (Brazzaville)": "CG",
    "Congo (Kinshasa)": "CD",
    "Costa Rica": "CR",
    "Cote d'Ivoire": "CI",
    "Croatia": "HR",
    "Cuba": "CU",
    "Cyprus": "CY",
    "Czechia": "CZ",
    "Denmark": "DK",
    "Djibouti": "DJ",
    "Dominican Republic": "DO",
    "Ecuador": "EC",
    "Egypt": "EG",
    "El Salvador": "SV",
    "Equatorial Guinea": "GQ",
    "Eritrea": "ER",
    "Estonia": "EE",
    "Eswatini": "SZ",
    "Ethiopia": "ET",
    "Fiji": "FJ",
    "Finland": "FI",
    "France": "FR",
    "Gabon": "GA",
    "Gambia": "GM",
    "Georgia": "GE",
    "Germany": "DE",
    "Ghana": "GH",
    "Greece": "GR",
    "Guatemala": "GT",
    "Guinea": "GN",
    "Guyana": "GY",
    "Haiti": "HT",
    "Holy See": "VA",
    "Honduras": "HN",
    "Hungary": "HU",
    "Iceland": "IS",
    "India": "IN",
    "Indonesia": "ID",
    "Iran": "IR",
    "Iraq": "IQ",
    "Ireland": "IE",
    "Israel": "IL",
    "Italy": "IT",
    "Jamaica": "JM",
    "Japan": "JP",
    "Jordan": "JO",
    "Kazakhstan": "KZ",
    "Kenya": "KE",
    "Korea, South": "KR",
    "Kuwait": "KW",
    "Kyrgyzstan": "KG",
    "Latvia": "LV",
    "Lebanon": "LB",
    "Liberia": "LR",
    "Liechtenstein": "LI",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Madagascar": "MG",
    "Malaysia": "MY",
    "Maldives": "MV",
    "Malta": "MT",
    "Mauritania": "MR",
    "Mauritius": "MU",
    "Mexico": "MX",
    "Moldova": "MD",
    "Monaco": "MC",
    "Mongolia": "MN",
    "Montenegro": "ME",
    "Morocco": "MA",
    "Namibia": "NA",
    "Nepal": "NP",
    "Netherlands": "NL",
    "New Zealand": "NZ",
    "Nicaragua": "NI",
    "Niger": "NE",
    "Nigeria": "NG",
    "North Macedonia": "MK",
    "Norway": "NO",
    "Oman": "OM",
    "Pakistan": "PK",
    "Panama": "PA",
    "Papua New Guinea": "PG",
    "Paraguay": "PY",
    "Peru": "PE",
    "Philippines": "PH",
    "Poland": "PL",
    "Portugal": "PT",
    "Qatar": "QA",
    "Romania": "RO",
    "Russia": "RU",
    "Rwanda": "RW",
    "Saint Lucia": "LC",
    "Saint Vincent and the Grenadines": "VC",
    "San Marino": "SM",
    "Saudi Arabia": "SA",
    "Senegal": "SN",
    "Serbia": "RS",
    "Seychelles": "SC",
    "Singapore": "SG",
    "Slovakia": "SK",
    "Slovenia": "SI",
    "Somalia": "SO",
    "South Africa": "ZA",
    "Spain": "ES",
    "Sri Lanka": "LK",
    "Sudan": "SD",
    "Suriname": "SR",
    "Sweden": "SE",
    "Switzerland": "CH",
    "Taiwan*": "TW",
    "Tanzania": "TZ",
    "Thailand": "TH",
    "Togo": "TG",
    "Trinidad and Tobago": "TT",
    "Tunisia": "TN",
    "Turkey": "TR",
    "Uganda": "UG",
    "Ukraine": "UA",
    "United Arab Emirates": "AE",
    "United Kingdom": "GB",
    "Uruguay": "UY",
    "US": "US",
    "Uzbekistan": "UZ",
    "Venezuela": "VE",
    "Vietnam": "VN",
    "Zambia": "ZM",
    "Zimbabwe": "ZW",
    "Dominica": "DM",
    "Grenada": "GD",
    "Mozambique": "MZ",
    "Syria": "SY",
    "Timor-Leste": "TL",
    "Belize": "BZ",
    "Laos": "LA",
    "Libya": "LY",
    "West Bank and Gaza": "PS",
    "Guinea-Bissau": "GW",
    "Mali": "ML",
    "Saint Kitts and Nevis": "KN",
    "Kosovo": "XK",  # NOTE: This is not an ISO code, but an unofficial code used by the European Commission.
    "Burma": "MM",
}


class Payload(BaseModel):
    action: str


class Args(BaseModel):
    payload: Payload


def get_country_totals(url):
    r = requests.get(url)
    r.raise_for_status()
    f = StringIO(r.text)

    # Province/State
    # Country/Region
    # Lat
    # Long
    # 1/22/20,1/23/20...

    entries = []
    days = 0

    csv_reader = csv.DictReader(f)
    for row in csv_reader:

        if days == 0:
            column_names = list(row.keys())
            days = len(column_names) - 4

        values = list(row.values())

        entry = {
            "state": values[0],
            "country": values[1],
            "lat": values[2],
            "lon": values[3],
            "counts": []
        }

        for i in range(days):
            entry["counts"].append(values[i + 4])

        entries.append(entry)

    country_totals = {}

    for entry in entries:
        country = entry["country"]
        if country not in country_mapping:
            print(f"Skipping country without mapping: {country}")
            continue

        code = country_mapping[country]
        if code not in country_totals:
            country_totals[code] = [0] * days

        counts = entry["counts"]
        assert len(counts) == days
        for i in range(days):
            country_totals[code][i] = counts[i]

    return country_totals


refresh_jhu = APIRouter()


@refresh_jhu.post("/", response_model=None)
async def handle_refresh_request(args: Args, response: Response) -> None:
    assert args.payload.action == "refresh"

    # Connect to database.
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        print("Getting time series for charts")
        country_confirmed_totals = get_country_totals(confirmed_global_csv_url)
        country_deaths_totals = get_country_totals(deaths_global_csv_url)
        country_recovered_totals = get_country_totals(recovered_global_csv_url)

        total_confirmed = 0
        total_deaths = 0
        total_recovered = 0

        series_length = len(country_confirmed_totals["GB"])
        print("Series length", series_length)

        total_confirmed_time_series = [0] * series_length
        total_deaths_time_series = [0] * series_length
        total_recovered_time_series = [0] * series_length

        print("Processing time series for storing in db")
        for code in country_confirmed_totals.keys():
            confirmed = int(country_confirmed_totals[code][-1])
            deaths = int(country_deaths_totals[code][-1])
            recovered = int(country_recovered_totals[code][-1])

            total_confirmed += confirmed
            total_deaths += deaths
            total_recovered += recovered

            for i in range(series_length):
                total_confirmed_time_series[i] += int(country_confirmed_totals[code][i])
                total_deaths_time_series[i] += int(country_deaths_totals[code][i])
                total_recovered_time_series[i] += int(country_recovered_totals[code][i])

            cur.execute("""
                UPDATE country SET
                    covid_confirmed = %s,
                    covid_deaths = %s,
                    covid_recovered = %s,
                    covid_confirmed_time_series = %s,
                    covid_deaths_time_series = %s,
                    covid_recovered_time_series = %s
                WHERE iso_alpha2 = %s""", (confirmed, deaths, recovered,
                                           json.dumps(country_confirmed_totals[code]),
                                           json.dumps(country_deaths_totals[code]),
                                           json.dumps(country_recovered_totals[code]),
                                           code))

        print("Updating world totals")
        cur.execute("""
            UPDATE region SET
                covid_confirmed = %s,
                covid_deaths = %s,
                covid_recovered = %s,
                covid_confirmed_time_series = %s,
                covid_deaths_time_series = %s,
                covid_recovered_time_series = %s
            WHERE alpha3 = 'WLD'""", (total_confirmed, total_deaths, total_recovered,
                                      json.dumps(total_confirmed_time_series),
                                      json.dumps(total_deaths_time_series),
                                      json.dumps(total_recovered_time_series)))

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
