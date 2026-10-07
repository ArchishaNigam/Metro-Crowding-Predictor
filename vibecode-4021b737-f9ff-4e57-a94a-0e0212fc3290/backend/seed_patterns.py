#!/usr/bin/env python3
"""Fetch DMRC GTFS data from GitHub and seed stations + timetable patterns."""

import sqlite3
import csv
import urllib.request
import io
from collections import defaultdict

GTFS_BASE = "https://raw.githubusercontent.com/Krtvy/delhi-metro-route-finder/main/"
DB_PATH = "/tmp/master.db"

WINDOWS = [
    ("05:00", "08:00", "low"),
    ("08:00", "11:00", "high"),
    ("11:00", "17:00", "medium"),
    ("17:00", "21:00", "high"),
    ("21:00", "23:59", "medium"),
]

def download_csv(name):
    url = GTFS_BASE + name
    with urllib.request.urlopen(url) as f:
        return list(csv.DictReader(io.TextIOWrapper(f)))

def main():
    print("Fetching stops.csv ...")
    stops_rows = download_csv("stops.csv")
    stops = {r["stop_id"]: r["stop_name"].strip() for r in stops_rows}
    print(f"  {len(stops)} stops")

    print("Fetching trips.csv ...")
    trips_rows = download_csv("trips.csv")
    trip_daytype = {}
    for r in trips_rows:
        sid = r["service_id"]
        if sid == "weekday":
            trip_daytype[r["trip_id"]] = "weekday"
        else:
            trip_daytype[r["trip_id"]] = "weekend"
    print(f"  {len(trip_daytype)} trips")

    print("Processing stop_times.csv to extract consecutive station pairs ...")
    prev_trip = None
    prev_stop = None
    prev_dep = None
    segments = defaultdict(set)
    with urllib.request.urlopen(GTFS_BASE + "stop_times.csv") as f:
        reader = csv.DictReader(io.TextIOWrapper(f))
        for row in reader:
            tid = row["trip_id"]
            if tid not in trip_daytype:
                continue
            sid = row["stop_id"]
            dep = row["departure_time"][:5]
            if tid == prev_trip and prev_stop is not None and prev_stop != sid:
                day_type = trip_daytype[tid]
                segments[(prev_stop, sid, day_type)].add(prev_dep)
            prev_trip = tid
            prev_stop = sid
            prev_dep = dep
        process_last = prev_trip and prev_stop

    print(f"  {len(segments)} unique station-pair segments")

    print("Connecting to DB ...")
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()

    print("Seeding stations ...")
    station_ids = {}
    used_stops = set()
    for (o, d, _) in segments:
        used_stops.add(o)
        used_stops.add(d)
    for sid in sorted(used_stops):
        name = stops[sid]
        existing = cur.execute("SELECT id FROM stations WHERE name = ?", (name,)).fetchone()
        if existing:
            station_ids[sid] = existing[0]
        else:
            cur.execute("INSERT INTO stations (name) VALUES (?)", (name,))
            station_ids[sid] = cur.lastrowid
    db.commit()
    print(f"  {len(station_ids)} stations in DB")

    print("Clearing existing timetable patterns ...")
    cur.execute("DELETE FROM timetable_patterns")
    db.commit()

    print("Building timetable patterns ...")
    patterns = set()
    for (origin_sid, dest_sid, day_type), deps in segments.items():
        oid = station_ids.get(origin_sid)
        did = station_ids.get(dest_sid)
        if oid is None or did is None or oid == did:
            continue
        for start, end, level in WINDOWS:
            has_trip = any(start <= d < end for d in deps)
            if has_trip:
                patterns.add((oid, did, day_type, start, end, level))

    print(f"  {len(patterns)} unique patterns to insert")
    inserted = 0
    for oid, did, day_type, start, end, level in sorted(patterns):
        try:
            cur.execute(
                "INSERT INTO timetable_patterns (origin_station_id, destination_station_id, day_type, start_time, end_time, baseline_crowding_level) VALUES (?, ?, ?, ?, ?, ?)",
                (oid, did, day_type, start, end, level),
            )
            inserted += 1
        except sqlite3.IntegrityError as e:
            pass

    db.commit()
    db.close()
    print(f"  {inserted} timetable patterns inserted")
    print("Done!")

if __name__ == "__main__":
    main()