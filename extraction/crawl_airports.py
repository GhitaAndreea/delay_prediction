import pandas as pd
import requests

WIKIDATA_URL = "https://query.wikidata.org/sparql"
HEADERS = {"User-Agent": "LROP-delay-study/1.0 (university project; deaioana03@gmail.com)"}

flights = pd.read_csv("../data/processed/departures_clean.csv")
codes = sorted(set(flights["destination"].dropna()) | {"OTP"})
# print(codes)

values = " ".join(f'"{code}"' for code in codes)
query = f"""
SELECT ?iata ?coord ?country_code WHERE {{
  VALUES ?iata {{ {values} }}
  ?airport wdt:P238 ?iata ;
           wdt:P625 ?coord ;
           wdt:P17 ?country .
  ?country wdt:P297 ?country_code .
}}
"""

response = requests.get(WIKIDATA_URL, params={"query": query, "format": "json"}, headers=HEADERS, timeout=60)
response.raise_for_status()
rows = response.json()["results"]["bindings"]

records = []
for row in rows:
    lon, lat = row["coord"]["value"].removeprefix("Point(").removesuffix(")").split()
    records.append({"iata_code": row["iata"]["value"],
                    "country": row["country_code"]["value"],
                    "latitude": float(lat),
                    "longitude": float(lon)})
airports = pd.DataFrame(records)

counts = airports["iata_code"].value_counts()
several = counts[counts > 1].index.tolist()
missing = sorted(set(codes) - set(airports["iata_code"]))
print(f"Found {airports['iata_code'].nunique()} of {len(codes)} codes")
print("Several answers (first one kept, check by hand):", several)
print("Not found (add by hand):", missing)
 
airports = airports.drop_duplicates("iata_code")
airports.to_csv("../data/raw/airports_wikidata.csv", index=False)
