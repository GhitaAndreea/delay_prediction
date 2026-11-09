import argparse
import pandas as pd
import numpy as np
import json
from pathlib import Path

DELAY_THRESHOLD_MIN = 15

KEEP_COLUMNS = [
    "id", "flightNumber", "airline", "airlineName", 
    "destination", "destinationName", "scheduled_dt", 
    "actual_dt", "dep_delay_min", "delayed_15",
    "boardingGate", "isSchengen", "codeshare_count", 
]


def load_raw(path: Path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data.get("flights", []))
    print(f"Loaded {len(df)} rows (API reported total: {data.get('total')})\n")
    return df

def clean(df: pd.DataFrame):
    report = []

    def filter_step(data: pd.DataFrame, mask: pd.Series, label: str) -> pd.DataFrame:
        removed = int((~mask).sum())
        remaining = int(mask.sum())
        report.append({"step": label, "removed": removed, "remaining":remaining})
        print(f"{label:<42} removed {removed:>6}  remaining {remaining:>6}")
        return data.loc[mask]

    df = filter_step(df, df["airport"] == "henri-coanda", "Keep only Henri Coanda flights")
    df = filter_step(df, ~df.duplicated(subset="id"), "Remove duplicate flights")

    cancelled = df[df["status"] == "cancelled"].copy()
    df = filter_step(df, df["status"] != "cancelled", "Set aside canceled flights")

    df = filter_step(
        df, 
        (df["status"] == "departed") & df["actualTime"].notna(), "Drop flights with np final departure",
    )

    df = df.copy()

    fmt = "%Y-%m-%d %H:%M"
    df["scheduled_dt"] = pd.to_datetime(df["scheduledDateTime"], format=fmt, errors="coerce")
    df["actual_dt"] = pd.to_datetime(df["scheduledDate"] + " " + df["actualTime"], format=fmt, errors="coerce")

    df = filter_step(
        df,
        df["scheduled_dt"].notna() & df["actual_dt"].notna(), "Drop rows with unreadable times",
    )

    diff = df["actual_dt"] - df["scheduled_dt"]
    next_day = diff < pd.Timedelta(hours=-12)
    prev_day = diff > pd.Timedelta(hours=12)

    df.loc[next_day, "actual_dt"] += pd.Timedelta(days=1)
    df.loc[prev_day, "actual_dt"] -= pd.Timedelta(days=1)

    df["dep_delay_min"] = (df["actual_dt"] - df["scheduled_dt"]).dt.total_seconds() / 60
    df["delayed_15"] = (df["dep_delay_min"] >= DELAY_THRESHOLD_MIN).astype(int)

    df["codeshare_count"] = df["codeShareFlights"].apply(lambda x: len(x) if isinstance(x, list) else 0)

    selected_cols = [c for c in KEEP_COLUMNS if c in df.columns]
    return df[selected_cols], cancelled, report

def print_summary(df: pd.DataFrame):
    print("\n--- Summary of the clean dataset ---")
    print(f"Flights:          {len(df)}")
    print(f"Period:           {df['scheduled_dt'].min():%Y-%m-%d} to {df['scheduled_dt'].max():%Y-%m-%d}")
    print(f"Delayed 15+ min:  {df['delayed_15'].mean():.1%}")
    print(f"Median delay:     {df['dep_delay_min'].median():.0f} min")
    print(f"Delay range:      {df['dep_delay_min'].min():.0f} to {df['dep_delay_min'].max():.0f} min")


def main(): 
    parser = argparse.ArgumentParser(description="Clean LROP dep")
    parser.add_argument("--input", default="../data/raw/raw_flights.json")
    parser.add_argument("--outdir", default="../data/processed")
    args = parser.parse_args()

    raw = load_raw(Path(args.input))
    clean_df, cancelled, report = clean(raw)
    print_summary(clean_df)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    clean_df.to_csv(outdir / "departures_clean.csv", index=False)
    cancelled.drop(columns=["codeShareFlights"], errors="ignore").to_csv(
        outdir / "departures_cancelled.csv", index=False
    )
    (outdir / "cleaning_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nSaved clean data, cancelled flights and the report to {outdir}/")


if __name__ == "__main__":
    main()
