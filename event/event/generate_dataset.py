import random
import csv

# ----------------------------
# Multipliers (same for all)
# ----------------------------
PACKAGES = {"simple": 1.00, "basic": 1.25, "luxury": 1.70}
LOCATION_MULT = {"tier2": 1.00, "metro": 1.12, "rural": 0.93, "premium": 1.20}

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def calc_total(items, guests, pkg, loc, selected_ids):
    pkg_mult = PACKAGES[pkg]
    loc_mult = LOCATION_MULT[loc]
    total = 0.0
    for it in items:
        if it["id"] not in selected_ids:
            continue
        base_cost = it["base"] * guests if it["type"] == "perGuest" else it["base"]
        total += base_cost * pkg_mult * loc_mult
    return total

def gen_event_row(event_cfg):
    items = event_cfg["items"]

    # guests distribution per event
    guests = int(clamp(random.gauss(event_cfg["guests_mu"], event_cfg["guests_sigma"]),
                       event_cfg["guests_min"], event_cfg["guests_max"]))

    pkg = random.choices(["simple", "basic", "luxury"], weights=event_cfg["pkg_weights"], k=1)[0]
    loc = random.choices(["rural", "tier2", "metro", "premium"], weights=event_cfg["loc_weights"], k=1)[0]

    all_ids = [x["id"] for x in items]

    selected = set()

    # must-have items
    for must_id in event_cfg.get("must_have", []):
        if must_id in all_ids:
            selected.add(must_id)

    # select N items
    target_count = int(clamp(random.gauss(event_cfg["services_mu"], event_cfg["services_sigma"]),
                             event_cfg["services_min"], event_cfg["services_max"]))
    while len(selected) < target_count:
        selected.add(random.choice(all_ids))

    selected_ids = sorted(selected)
    services_count = len(selected_ids)

    rule_total = calc_total(items, guests, pkg, loc, selected_ids)

    # add real-world noise + season uplift
    noise_scale = {"simple": 0.10, "basic": 0.12, "luxury": 0.15}[pkg]
    noise = random.uniform(-noise_scale, noise_scale)
    peak = random.random() < event_cfg.get("peak_prob", 0.25)
    season_uplift = event_cfg.get("peak_uplift", 0.06) if peak else 0.0

    total_budget = rule_total * (1.0 + noise + season_uplift)
    total_budget = int(round(total_budget / 500.0) * 500)

    return {
        "event": event_cfg["name"],
        "guests": guests,
        "package": pkg,
        "location": loc,
        "services_count": services_count,
        "selected_services": "|".join(selected_ids),
        "rule_total": int(round(rule_total)),
        "total_budget": total_budget
    }

def write_dataset(filename, event_cfg, rows=300):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "event","guests","package","location","services_count",
                "selected_services","rule_total","total_budget"
            ]
        )
        writer.writeheader()
        for _ in range(rows):
            writer.writerow(gen_event_row(event_cfg))
    print(f"✅ {filename} generated (rows={rows})")

# ----------------------------
# Event Configs (edit anytime)
# ----------------------------
EVENTS = {
    "wedding": {
        "name": "wedding",
        "items": [
            {"id":"bridegroom","type":"fixed","base":35000},
            {"id":"haldi","type":"fixed","base":25000},
            {"id":"sangeeth","type":"fixed","base":60000},
            {"id":"mehendi","type":"fixed","base":28000},
            {"id":"marriage","type":"fixed","base":90000},
            {"id":"food","type":"perGuest","base":650},
            {"id":"band","type":"fixed","base":20000},
            {"id":"makeup","type":"fixed","base":40000},
            {"id":"photo","type":"fixed","base":55000},
        ],
        "must_have": ["food"],
        "guests_mu": 250, "guests_sigma": 120, "guests_min": 50, "guests_max": 1200,
        "services_mu": 7, "services_sigma": 1.5, "services_min": 3, "services_max": 9,
        "pkg_weights": [0.45, 0.40, 0.15],
        "loc_weights": [0.10, 0.45, 0.35, 0.10],
        "peak_prob": 0.35, "peak_uplift": 0.06
    },

    "birthday_private_party": {
        "name": "birthday_private_party",
        "items": [
            {"id":"venue","type":"fixed","base":30000},
            {"id":"theme_decor","type":"fixed","base":18000},
            {"id":"balloon_decor","type":"fixed","base":12000},
            {"id":"cake","type":"fixed","base":6000},
            {"id":"snacks","type":"perGuest","base":250},
            {"id":"dj","type":"fixed","base":15000},
            {"id":"games_anchor","type":"fixed","base":10000},
            {"id":"photo","type":"fixed","base":20000},
            {"id":"return_gifts","type":"perGuest","base":120},
        ],
        "must_have": ["cake"],
        "guests_mu": 80, "guests_sigma": 50, "guests_min": 20, "guests_max": 400,
        "services_mu": 6, "services_sigma": 1.2, "services_min": 3, "services_max": 9,
        "pkg_weights": [0.55, 0.35, 0.10],
        "loc_weights": [0.15, 0.50, 0.28, 0.07],
        "peak_prob": 0.25, "peak_uplift": 0.04
    },

    "corporate_event": {
        "name": "corporate_event",
        "items": [
            {"id":"hall","type":"fixed","base":70000},
            {"id":"av","type":"fixed","base":35000},
            {"id":"stage_setup","type":"fixed","base":25000},
            {"id":"branding","type":"fixed","base":20000},
            {"id":"registration","type":"fixed","base":12000},
            {"id":"catering","type":"perGuest","base":450},
            {"id":"photo_video","type":"fixed","base":30000},
            {"id":"security","type":"fixed","base":12000},
            {"id":"staff","type":"perGuest","base":80},
        ],
        "must_have": ["catering","av"],
        "guests_mu": 180, "guests_sigma": 120, "guests_min": 30, "guests_max": 1000,
        "services_mu": 6, "services_sigma": 1.4, "services_min": 3, "services_max": 9,
        "pkg_weights": [0.30, 0.50, 0.20],
        "loc_weights": [0.05, 0.35, 0.45, 0.15],
        "peak_prob": 0.20, "peak_uplift": 0.05
    },

    "engagement_reception": {
        "name": "engagement_reception",
        "items": [
            {"id":"stage_decor","type":"fixed","base":45000},
            {"id":"lighting","type":"fixed","base":20000},
            {"id":"flowers","type":"fixed","base":22000},
            {"id":"catering","type":"perGuest","base":550},
            {"id":"music","type":"fixed","base":18000},
            {"id":"makeup","type":"fixed","base":25000},
            {"id":"photo_video","type":"fixed","base":45000},
            {"id":"invites","type":"fixed","base":8000},
            {"id":"return_gifts","type":"perGuest","base":100},
        ],
        "must_have": ["catering"],
        "guests_mu": 200, "guests_sigma": 110, "guests_min": 50, "guests_max": 900,
        "services_mu": 7, "services_sigma": 1.3, "services_min": 3, "services_max": 9,
        "pkg_weights": [0.35, 0.45, 0.20],
        "loc_weights": [0.08, 0.45, 0.37, 0.10],
        "peak_prob": 0.30, "peak_uplift": 0.05
    },
}

def main():
    rows_each = 350  # change if needed

    for key, cfg in EVENTS.items():
        filename = f"{key}_dataset.csv"
        write_dataset(filename, cfg, rows=rows_each)

    # Optional combined dataset for training one model
    combined = "all_events_dataset.csv"
    with open(combined, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "event","guests","package","location","services_count",
                "selected_services","rule_total","total_budget"
            ]
        )
        writer.writeheader()
        for key, cfg in EVENTS.items():
            for _ in range(rows_each):
                writer.writerow(gen_event_row(cfg))
    print(f"✅ {combined} generated (rows={rows_each * len(EVENTS)})")

if __name__ == "__main__":
    main()
