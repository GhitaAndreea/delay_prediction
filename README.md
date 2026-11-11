# Flight Delay Prediction at Bucharest Henri Coanda Airport

**Source**: Predict if a flight departing from Bucharest Henri Coanda International Airport (ICAO: LROP) will be delayed, based on information about the flight such as: 
- operator
- destination
- gate 
- departure time
- day of the week 
- season 
- special event 
- flight frequency
- congestion
- METAR notices

## Main Question

With the given known information about a departure from LROP, can a delay of **15 or more minutes** be predicted? 
- **Target**: `delay_15 = 1` if the actual departure is at least 15 min after the scheduled departure, otherwise `0`. The 15 min threshold is a standards used by EUROCONTROL. 
- **Methods**: classical ML only 

## Data

**Main source**: the public flight archive of Compania Nationala Aeroporturi Bucuresti (https://bucharestairports.ro/lista-zboruri/)

- **Contents:** [62,652] departure records from 26.10.2025 to 04.10.2026.

- **Fields per flight**: flight number, airline, destination, scheduled date and time, estimated time, actual time, status, gate, check-in counters, codeshare flight numbers

The raw data is not stored in this repository because of its size. See [`data/raw/README.md`](data/raw/README.md) for how it was obtained and where to download it.

### Data-quality findings

- Some past flights keep a non-final status ("scheduled", "boarding") with no actual departure time; they are removed.
- The actual departure time has no date of its own, so flights departing after midnight need correcting (e.g. scheduled 23:20, departed 00:29 is +69 minutes, not −23 hours).
- The `isSchengen` field does not match the destinations' real Schengen status, so it will be reversed.
- Codeshare flights are listed inside the operating flight's record, so each row is one physical flight.

## Repository structure

```
extraction/   scripts for crawling and data preprocessing
data/         raw data (link) and processed outputs
docs/         presentations and figures
```

## How to reproduce

Tested with Python 3.

pip install pandas numpy matplotlib

# 1. Put the raw export at data/raw/ (see data/raw/README.md), then clean it
python3 extraction/preprocessing.py --input data/raw/departures_raw.json

# 2. Print the key numbers and save the charts to docs/figures/
python3 extraction/descriptives.py


## Cleaning steps

`preprocess.py` performs these steps and records how many rows each removes in `data/processed/cleaning_report.json`:

1. Keep only Henri Coandă flights
2. Remove duplicate flights (same id)
3. Set aside cancelled flights (saved separately for analysis)
4. Remove flights without a final departure
5. Build full date-times and correct flights that cross midnight
6. Compute the departure delay in minutes and the target `delayed_15`

## Planned work (Phase 2)

- **Features:** hour, day of the week, month and season; Romanian public holidays and special events; destination country, Schengen status and distance; airport congestion per hour; weekly route frequency; weather at LROP from METAR reports; aircraft type if a data source is available.
- **Evaluation:** second data aquisition for test, precision, recall, F1, ROC-AUC, and a comparison between early prediction (information known days ahead) and late prediction (adding gate and weather).
- **Error analysis:** where and why the best model fails.
