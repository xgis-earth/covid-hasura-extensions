from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from io import StringIO
from app.db import get_conn
import psycopg2
import traceback
import requests
import csv
import json


url = "https://raw.githubusercontent.com/dsbbfinddx/FINDCov19TrackerData/master/processed/coronavirus_tests.csv"

country_codes = {
    "Andorra": "AD",
    "United Arab Emirates (the)": "AE",
    "United Arab Emirates": "AE",
    "Afghanistan": "AF",
    "Antigua and Barbuda": "AG",
    "Anguilla": "AI",
    "Albania": "AL",
    "Armenia": "AM",
    "Angola": "AO",
    "Antarctica": "AQ",
    "Argentina": "AR",
    "American Samoa": "AS",
    "Austria": "AT",
    "Australia": "AU",
    "Aruba": "AW",
    "Åland Islands": "AX",
    "Azerbaijan": "AZ",
    "Bosnia and Herzegovina": "BA",
    "Barbados": "BB",
    "Bangladesh": "BD",
    "Belgium": "BE",
    "Burkina Faso": "BF",
    "Bulgaria": "BG",
    "Bahrain": "BH",
    "Burundi": "BI",
    "Benin": "BJ",
    "Saint Barthélemy": "BL",
    "Bermuda": "BM",
    "Brunei Darussalam": "BN",
    "Brunei": "BN",
    "Bolivia (Plurinational State of)": "BO",
    "Bolivia": "BO",
    "onaire, Sint Eustatius and Saba": "BQ",
    "Brazil": "BR",
    "Bahamas (the)": "BS",
    "Bahamas": "BS",
    "The Bahamas": "BS",
    "Bhutan": "BT",
    "Bouvet Island": "BV",
    "Botswana": "BW",
    "Belarus": "BY",
    "Belize": "BZ",
    "Canada": "CA",
    "Cocos (Keeling) Islands (the)": "CC",
    "Congo (the Democratic Republic of the)": "CD",
    "Democratic Republic of the Congo": "CD",
    "Central African Republic (the)": "CF",
    "Central African Republic": "CF",
    "Congo (the)": "CG",
    "Republic of the Congo": "CG",
    "Switzerland": "CH",
    "Cote d'Ivoire": "CI",
    "Côte d'Ivoire": "CI",
    "Cook Islands (the)": "CK",
    "Chile": "CL",
    "Cameroon": "CM",
    "China": "CN",
    "Mainland China": "CN",
    "Colombia": "CO",
    "Costa Rica": "CR",
    "Cuba": "CU",
    "Cabo Verde": "CV",
    "Cape Verde": "CV",
    "Curaçao": "CW",
    "Christmas Island": "CX",
    "Cyprus": "CY",
    "Czech Republic": "CZ",
    "Czechia": "CZ",
    "Germany": "DE",
    "Djibouti": "DJ",
    "Denmark": "DK",
    "Dominica": "DM",
    "Dominican Republic (the)": "DO",
    "Dominican Republic": "DO",
    "Algeria": "DZ",
    "Ecuador": "EC",
    "Estonia": "EE",
    "Egypt": "EG",
    "Western Sahara": "EH",
    "Eritrea": "ER",
    "Spain": "ES",
    "Ethiopia": "ET",
    "Finland": "FI",
    "Fiji": "FJ",
    "Falkland Islands (the)": "FK",
    "Micronesia (Federated States of)": "FM",
    "Faroe Islands (the)": "FO",
    "Faroe Islands": "FO",
    "France": "FR",
    "Gabon": "GA",
    "UK": "GB",
    "United Kingdom of Great Britain and Northern Ireland (the)": "GB",
    "Grenada": "GD",
    "Georgia": "GE",
    "French Guiana": "GF",
    "Guernsey": "GG",
    "Ghana": "GH",
    "Gibraltar": "GI",
    "Greenland": "GL",
    "Gambia (the)": "GM",
    "The Gambia": "GM",
    "Guinea": "GN",
    "Guadeloupe": "GP",
    "Equatorial Guinea": "GQ",
    "Greece": "GR",
    "South Georgia and the South Sandwich Islands": "GS",
    "Guatemala": "GT",
    "Guam": "GU",
    "Guinea Bissau": "GW",
    "Guinea-Bissau": "GW",
    "Guyana": "GY",
    "Hong Kong": "HK",
    "Heard Island and McDonald Islands": "HM",
    "Honduras": "HN",
    "Croatia": "HR",
    "Haiti": "HT",
    "Hungary": "HU",
    "Indonesia": "ID",
    "Ireland": "IE",
    "Israel": "IL",
    "Isle of Man": "IM",
    "India": "IN",
    "British Indian Ocean Territory (the)": "IO",
    "Iraq": "IQ",
    "Iran (Islamic Republic of)": "IR",
    "Iceland": "IS",
    "Italy": "IT",
    "Jersey": "JE",
    "Jamaica": "JM",
    "Jordan": "JO",
    "Japan": "JP",
    "Kenya": "KE",
    "Kyrgyzstan": "KG",
    "Cambodia": "KH",
    "Kiribati": "KI",
    "Comoros (the)": "KM",
    "Comoros": "KM",
    "Saint Kitts and Nevis": "KN",
    "Korea (the Democratic People's Republic of)": "KP",
    "Korea (the Republic of)": "KR",
    "Republic of Korea": "KR",
    "Kuwait": "KW",
    "Cayman Islands (the)": "KY",
    "Kazakhstan": "KZ",
    "Lao People's Democratic Republic (the)": "LA",
    "Lao People's Democratic Republic": "LA",
    "Lebanon": "LB",
    "Saint Lucia": "LC",
    "Liechtenstein": "LI",
    "Sri Lanka": "LK",
    "Liberia": "LR",
    "Lesotho": "LS",
    "Lithuania": "LT",
    "Luxembourg": "LU",
    "Latvia": "LV",
    "Libya": "LY",
    "Morocco": "MA",
    "Monaco": "MC",
    "Moldova (the Republic of)": "MD",
    "Moldova": "MD",
    "Montenegro": "ME",
    "Saint Martin (French part)": "MF",
    "Madagascar": "MG",
    "Marshall Islands (the)": "MH",
    "North Macedonia": "MK",
    "Mali": "ML",
    "Myanmar": "MM",
    "Mongolia": "MN",
    "Macao": "MO",
    "Northern Mariana Islands (the)": "MP",
    "Martinique": "MQ",
    "Mauritania": "MR",
    "Montserrat": "MS",
    "Malta": "MT",
    "Mauritius": "MU",
    "Maldives": "MV",
    "Malawi": "MW",
    "Mexico": "MX",
    "Malaysia": "MY",
    "Mozambique": "MZ",
    "Namibia": "NA",
    "New Caledonia": "NC",
    "Niger (the)": "NE",
    "Niger": "NE",
    "Norfolk Island": "NF",
    "Nigeria": "NG",
    "Nicaragua": "NI",
    "Netherlands (the)": "NL",
    "Netherlands": "NL",
    "Norway": "NO",
    "Nepal": "NP",
    "Nauru": "NR",
    "Niue": "NU",
    "New Zealand": "NZ",
    "Oman": "OM",
    "Panama": "PA",
    "Peru": "PE",
    "French Polynesia": "PF",
    "Papua New Guinea": "PG",
    "Philippines (the)": "PH",
    "Philippines": "PH",
    "Pakistan": "PK",
    "Poland": "PL",
    "Saint Pierre and Miquelon": "PM",
    "Pitcairn": "PN",
    "Puerto Rico": "PR",
    "Occupied Palestinian Territory": "PS",
    "Palestine, State of": "PS",
    "West Bank and Gaza": "PS",
    "Portugal": "PT",
    "Palau": "PW",
    "Paraguay": "PY",
    "Qatar": "QA",
    "Réunion": "RE",
    "Romania": "RO",
    "Serbia": "RS",
    "Russia": "RU",
    "Russian Federation (the)": "RU",
    "Rwanda": "RW",
    "Saudi Arabia": "SA",
    "Solomon Islands": "SB",
    "Seychelles": "SC",
    "Sudan (the)": "SD",
    "Sudan": "SD",
    "Sweden": "SE",
    "Singapore": "SG",
    "Saint Helena, Ascension and Tristan da Cunha": "SH",
    "Slovenia": "SI",
    "valbard and Jan Mayen": "SJ",
    "Slovakia": "SK",
    "Sierra Leone": "SL",
    "San Marino": "SM",
    "Senegal": "SN",
    "Somalia": "SO",
    "Suriname": "SR",
    "South Sudan": "SS",
    "Sao Tome and Principe": "ST",
    "El Salvador": "SV",
    "Saint Martin": "SX",
    "Sint Maarten (Dutch part)": "SX",
    "Syria": "SY",
    "Syrian Arab Republic (the)": "SY",
    "Eswatini": "SZ",
    "Turks and Caicos Islands (the)": "TC",
    "Chad": "TD",
    "French Southern Territories (the)": "TF",
    "Togo": "TG",
    "Thailand": "TH",
    "Tajikistan": "TJ",
    "Tokelau": "TK",
    "Timor-Leste": "TL",
    "Timor-Leste [aa]": "TL",
    "Turkmenistan": "TM",
    "Tunisia": "TN",
    "Tonga": "TO",
    "Turkey": "TR",
    "Trinidad and Tobago": "TT",
    "Tuvalu": "TV",
    "Taiwan (Province of China)": "TW",
    "Taiwan": "TW",
    "Tanzania, the United Republic of": "TZ",
    "United Republic of Tanzania": "TZ",
    "Ukraine": "UA",
    "Uganda": "UG",
    "United States Minor Outlying Islands (the)": "UM",
    "United States of America (the)": "US",
    "USA": "US",
    "Uruguay": "UY",
    "Uzbekistan": "UZ",
    "Holy See (the)": "VA",
    "Holy See": "VA",
    "Saint Vincent and the Grenadines": "VC",
    "St. Vincent and the Grenadines": "VC",
    "Venezuela (Bolivarian Republic of)": "VE",
    "Venezuela": "VE",
    "Virgin Islands (British)": "VG",
    "Virgin Islands (U.S.)": "VI",
    "Viet Nam": "VN",
    "Vietnam": "VN",
    "Vanuatu": "VU",
    "Wallis and Futuna": "WF",
    "Samoa": "WS",
    "Kosovo": "XK",
    "Yemen": "YE",
    "Mayotte": "YT",
    "South Africa": "ZA",
    "Zambia": "ZM",
    "Zimbabwe": "ZW",
}


class Payload(BaseModel):
    action: str


class Args(BaseModel):
    payload: Payload


refresh_tests = APIRouter()


@refresh_tests.post("/", response_model=None)
async def handle_refresh_request(args: Args, response: Response) -> None:
    assert args.payload.action == "refresh"

    # Connect to database.
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        print("Preparing counts for storing in db")
        counts = {}

        r = requests.get(url)
        r.raise_for_status()
        f = StringIO(r.text)

        # country
        # date
        # new_tests
        # tests_cumulative
        # source

        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            country = row["country"]
            if country not in counts:
                counts[country] = []

            if row["tests_cumulative"] == "NA":
                print(f"Skipping \"{country}\" because tests_cumulative value is NA")
                continue

            counts[country].append({
                "date": row["date"],
                "count": row["tests_cumulative"]
            })

        for country in counts:
            if country not in country_codes:
                print(f"Skipping \"{country}\" because country is not in country-code lookup")
                continue

            code = country_codes[country]

            cur.execute("""
                UPDATE country SET
                    covid_tests = %s,
                    covid_tests_time_series = %s
                WHERE iso_alpha2 = %s""", (counts[country][-1]["count"],
                                           json.dumps(counts[country]),
                                           code))

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
