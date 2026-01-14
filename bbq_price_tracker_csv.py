"""
bbq_price_tracker_csv.py

Collects Big Buffet Non-Veg pricing data from BBQ Nation’s APIs and exports
a pivot-style CSV file.

Output:
    bbq_bigbuffet_pivot.csv

Examples:
    python bbq_price_tracker_csv.py --start-date today --days 5
    python bbq_price_tracker_csv.py --start-date today --end-date 2026-02-01
"""

import requests
import datetime
import time
import csv
import argparse
import sys
from collections import OrderedDict


BRANCH_ID = "128"
BUFFET_URL = "https://www.barbequenation.com/api/v1/menu-buffet-price"
SLOT_URL = "https://www.barbequenation.com/api/v1/slots"

REQUEST_DELAY = 0.5


def parse_date(value: str) -> datetime.date:
    if value.lower() == "today":
        return datetime.date.today()
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError("Date must be YYYY-MM-DD or 'today'")


def get_slots(date_str: str, dinner_type: str):
    time.sleep(REQUEST_DELAY)
    payload = {
        "reservation_date": date_str,
        "branch_id": BRANCH_ID,
        "dinner_type": dinner_type,
    }
    r = requests.post(SLOT_URL, json=payload)
    r.raise_for_status()
    return r.json()["results"]["preferred_branch"]["slots_available"]


def fetch_bigbuffet_nonveg(date_str: str, slot_id: str, reservation_time: str):
    time.sleep(REQUEST_DELAY)
    payload = {
        "branch_id": BRANCH_ID,
        "reservation_date": date_str,
        "slot_id": slot_id,
        "reservation_time": reservation_time,
    }

    r = requests.post(BUFFET_URL, json=payload)
    r.raise_for_status()

    for b in r.json()["results"]["buffets"]["buffet_data"]:
        name = b["displayName"].strip().upper()
        if name in {"BIG BUFFET NON-VEG", "NON-VEG"}:
            return b["totalAmount"]

    return None


def date_range(start: datetime.date, end: datetime.date):
    for i in range((end - start).days + 1):
        yield (start + datetime.timedelta(days=i)).strftime("%Y-%m-%d")


def build_csv(pivot: OrderedDict):
    all_slots = sorted({slot for d in pivot.values() for slot in d.keys()})
    dates = list(pivot.keys())

    with open("bbq_bigbuffet_pivot.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["slot"] + dates)

        for slot in all_slots:
            w.writerow([slot] + [pivot[d].get(slot, "") for d in dates])

    print("CSV generated → bbq_bigbuffet_pivot.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="BBQ buffet price CSV tracker")

    parser.add_argument("--start-date", required=True, type=parse_date,
                        help="YYYY-MM-DD or 'today'")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--days", type=int, help="Number of days from start date")
    group.add_argument("--end-date", type=parse_date, help="YYYY-MM-DD or 'today'")

    args = parser.parse_args()

    start = args.start_date

    if args.days:
        if args.days < 1:
            print("Days must be >= 1")
            sys.exit(1)
        end = start + datetime.timedelta(days=args.days - 1)
    else:
        end = args.end_date
        if end < start:
            print("End date cannot be before start date.")
            sys.exit(1)

    pivot = OrderedDict()

    for date in date_range(start, end):
        print(f"Processing {date}")
        pivot[date] = {}

        all_slots = get_slots(date, "LUNCH")

        for s in all_slots:
            price = fetch_bigbuffet_nonveg(date, s["slot_id"], s["slot_start_time"])
            if price is not None:
                pivot[date][s["slot_start_time"]] = price

    build_csv(pivot)


if __name__ == "__main__":
    main()
