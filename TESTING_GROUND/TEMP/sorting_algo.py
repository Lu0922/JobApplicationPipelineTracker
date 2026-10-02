# TESTING_GROUND/TEMP/sorting_algo.py
from datetime import datetime, timedelta, date

def generate_application_timeline(jobs_list: list, buffer_days: int = 3, today_date: date = None) -> list:
    """
    1. Filters out past-deadline, inactive, and applied entries.
    2. Maps available execution windows between consecutive single vacancy deadlines.
    3. Allocates pool entries into open slots based on capacity and deadlines without infinite loops.
    4. Outputs a unified, chronological timeline trace.
    """
    if today_date is None:
        today_date = date.today()

    def parse_date(item):
        d = item.get("closing_date") if isinstance(item, dict) else item
        return datetime.strptime(d, "%Y-%m-%d").date() if isinstance(d, str) else d

    # 1. Filter out completed and legacy records
    active_jobs = []
    for job in jobs_list:
        state = job.get("progress_state", "TODO").upper()
        if state in ("SUBMITTED", "APPLIED", "ARCHIVED"):
            continue
        if parse_date(job) < today_date:
            continue
        active_jobs.append(job)

    # Segregate and sort streams chronologically
    singles = sorted([j for j in active_jobs if j["type"].upper() == "SINGLE"], key=parse_date)
    pools = sorted([j for j in active_jobs if j["type"].upper() in ("POOL", "REGISTER")], key=parse_date)

    timeline_events = []
    current_time_cursor = today_date
    allocated_pool_ids = set()

    # 2. Iterate through single deadlines
    for single_job in singles:
        single_deadline = parse_date(single_job)
        crunch_start = single_deadline - timedelta(days=buffer_days)
        
        # Pull pools that expire before or on this single deadline
        for idx, pool_job in enumerate(pools):
            pool_id = id(pool_job)  # Use unique memory address reference if 'id' key is missing
            if pool_id in allocated_pool_ids:
                continue
                
            pool_deadline = parse_date(pool_job)
            if pool_deadline > single_deadline:
                continue

            # Allocate an open work window before the crunch zone kicks in
            if current_time_cursor < crunch_start:
                window_size = (crunch_start - current_time_cursor).days
                timeline_events.append({
                    "event_type": "WINDOW",
                    "days_available": window_size,
                    "description": f"🟢 Open Window: {window_size} days left before {single_job['company']} crunch"
                })
                current_time_cursor = crunch_start

            # Force allocate pool inside the current structural time block
            notes = "⚠️ Priority Pool Insertion: Must complete before deadline cutoff!" if pool_deadline <= single_deadline else ""
            timeline_events.append({
                "event_type": "JOB",
                "data": pool_job,
                "notes": notes
            })
            allocated_pool_ids.add(pool_id)

        # Map out the high-intensity crunch window preceding the single milestone
        if current_time_cursor < single_deadline:
            gap_days = (single_deadline - current_time_cursor).days
            timeline_events.append({
                "event_type": "WINDOW",
                "days_available": gap_days,
                "description": f"🚨 Crunch Window: {gap_days} days to lock down single submission"
            })
            current_time_cursor = single_deadline
            
        timeline_events.append({"event_type": "JOB", "data": single_job, "notes": ""})

    # 3. Clean up remaining long-term assets (Registers) closing out past the final single deadline
    for pool_job in pools:
        pool_id = id(pool_job)
        if pool_id in allocated_pool_ids:
            continue
            
        pool_deadline = parse_date(pool_job)
        gap_days = (pool_deadline - current_time_cursor).days
        
        if gap_days > 0:
            timeline_events.append({
                "event_type": "WINDOW",
                "days_available": gap_days,
                "description": f"🟢 Open Window: {gap_days} days available before register tracking cutoff"
            })
            current_time_cursor = pool_deadline
            
        timeline_events.append({"event_type": "JOB", "data": pool_job, "notes": ""})
        allocated_pool_ids.add(pool_id)

    return timeline_events

if __name__ == "__main__":
    mock_db_payload = [
        {"company": "WA Museum", "title": "Admin Assistant", "closing_date": "2026-10-08", "type": "POOL", "progress_state": "TODO"},
        {"company": "DFES", "title": "Admin Officer", "closing_date": "2026-10-09", "type": "SINGLE", "progress_state": "TODO"},
        {"company": "HSS", "title": "Supply Clerk", "closing_date": "2026-10-09", "type": "SINGLE", "progress_state": "TODO"},
        {"company": "WA Museum", "title": "Engagement Register", "closing_date": "2026-12-10", "type": "REGISTER", "progress_state": "TODO"}
    ]
    
    timeline = generate_application_timeline(mock_db_payload, buffer_days=3, today_date=date(2026, 10, 1))
    
    print("🗓️ PIPELINE WORKFLOW TIMELINE TRACK:")
    for entry in timeline:
        if entry["event_type"] == "WINDOW":
            print(f"  {entry['description']}")
        else:
            j = entry["data"]
            notes = f" -> {entry['notes']}" if entry["notes"] else ""
            print(f"📌 [{j['type']}] {j['company']} - {j['title']} (Closes: {j['closing_date']}){notes}")
