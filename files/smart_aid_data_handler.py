"""
Smart Aid: AI Resource Navigator
Data Handling Module - Iqra's Task
Collects, cleans, and structures datasets: food banks, clinics, NGOs
Output: CSV and JSON formats
"""

import csv
import json
import os
import re
from datetime import datetime

# ─────────────────────────────────────────────
# SAMPLE DATASET (replace with real scraped data)
# In production: fetch from govt portals, NGO sites, etc.
# ─────────────────────────────────────────────

RAW_FOOD_BANKS = [
    {"name": "Saylani Welfare Trust", "city": "Karachi", "address": "Saylani House, M.A Jinnah Road", "phone": "021-32462351", "services": "Daily langar, ration packages", "lat": "24.8607", "lng": "67.0011", "hours": "Mon-Sun 08:00-20:00", "verified": True},
    {"name": "Edhi Foundation Food Center", "city": "Lahore", "address": "Edhi Complex, Allama Iqbal Road", "phone": "042-37656565", "services": "Free meals, emergency rations", "lat": "31.5204", "lng": "74.3587", "hours": "Mon-Sun 07:00-21:00", "verified": True},
    {"name": "Khidmat-e-Khalq Foundation", "city": "Islamabad", "address": "G-7 Markaz, Blue Area", "phone": "051-2876543", "services": "Food packages, cooked meals", "lat": "33.7294", "lng": "73.0931", "hours": "Mon-Sat 09:00-18:00", "verified": True},
    {"name": "Rizq Foundation", "city": "Lahore", "address": "DHA Phase 5, Lahore", "phone": "0311-7477497", "services": "Rescued food redistribution", "lat": "31.4697", "lng": "74.4024", "hours": "Mon-Sun 10:00-22:00", "verified": True},
    {"name": "Robin Hood Army Lahore", "city": "Lahore", "address": "Volunteers-based, city-wide", "phone": "N/A", "services": "Weekend surplus food distribution", "lat": "31.5204", "lng": "74.3587", "hours": "Sat-Sun 18:00-21:00", "verified": True},
    {"name": "Al-Mustafa Welfare Trust", "city": "Multan", "address": "Hussain Agahi, Multan", "phone": "061-4510600", "services": "Daily meals, ramzan packages", "lat": "30.1575", "lng": "71.5249", "hours": "Mon-Sun 08:00-20:00", "verified": True},
    {"name": "", "city": "Peshawar", "address": "Saddar Road", "phone": "abc-123", "services": None, "lat": "34.0151", "lng": "71.5249", "hours": "", "verified": False},  # dirty row
]

RAW_CLINICS = [
    {"name": "Akhuwat Health Services", "city": "Lahore", "address": "Township, Lahore", "phone": "042-35168498", "specialties": "General OPD, maternal health", "lat": "31.4697", "lng": "74.2728", "hours": "Mon-Sat 08:00-14:00", "free": True, "verified": True},
    {"name": "HOPE Free Clinic", "city": "Karachi", "address": "Orangi Town, Karachi", "phone": "021-36659991", "specialties": "Pediatrics, gynecology, general", "lat": "24.9296", "lng": "66.9750", "hours": "Mon-Fri 09:00-17:00", "free": True, "verified": True},
    {"name": "Shaukat Khanum OPDS", "city": "Lahore", "address": "7A Block R-3, Johar Town", "phone": "042-35945100", "specialties": "Oncology, free for deserving", "lat": "31.4504", "lng": "74.2703", "hours": "Mon-Sat 08:00-16:00", "free": False, "verified": True},
    {"name": "LRBT Eye Hospital", "city": "Lahore", "address": "Bhati Gate, Lahore", "phone": "042-37673588", "specialties": "Ophthalmology, free surgery", "lat": "31.5788", "lng": "74.3090", "hours": "Mon-Fri 08:00-15:00", "free": True, "verified": True},
    {"name": "Umang Mental Health", "city": "Lahore", "address": "Gulberg III, Lahore", "phone": "0311-7786264", "specialties": "Mental health, counseling", "lat": "31.5085", "lng": "74.3338", "hours": "Mon-Sat 10:00-18:00", "free": False, "verified": True},
    {"name": "Indus Hospital", "city": "Karachi", "address": "Korangi Crossing, Karachi", "phone": "021-35112709", "specialties": "Full hospital, 100% free", "lat": "24.8266", "lng": "67.1391", "hours": "Mon-Sun 24hrs", "free": True, "verified": True},
    {"name": "Free Clinic", "city": "", "address": "Unknown", "phone": "0300-0000000", "specialties": "", "lat": None, "lng": None, "hours": "", "free": True, "verified": False},  # dirty row
]

RAW_NGOS = [
    {"name": "Edhi Foundation", "city": "National", "address": "Edhi Village, Karachi", "phone": "021-32620815", "focus": "Emergency relief, healthcare, orphans, elderly", "website": "https://edhi.org", "lat": "24.8874", "lng": "67.0491", "verified": True},
    {"name": "Saylani Welfare International Trust", "city": "National", "address": "Karachi", "phone": "021-32462351", "focus": "Food, education, skill development", "website": "https://saylaniwelfare.com", "lat": "24.8607", "lng": "67.0011", "verified": True},
    {"name": "Akhuwat Foundation", "city": "National", "address": "Township, Lahore", "phone": "042-35168498", "focus": "Microfinance, healthcare, education", "website": "https://akhuwat.org.pk", "lat": "31.4697", "lng": "74.2728", "verified": True},
    {"name": "Rizq Foundation", "city": "National", "address": "Lahore", "phone": "0311-7477497", "focus": "Food rescue, surplus redistribution", "website": "https://rizqapp.com", "lat": "31.4697", "lng": "74.3587", "verified": True},
    {"name": "Orangi Pilot Project", "city": "Karachi", "address": "Orangi Town, Karachi", "phone": "021-36655926", "focus": "Sanitation, housing, health, education", "website": "https://oppinstitutions.org", "lat": "24.9296", "lng": "66.9750", "verified": True},
    {"name": "", "city": "Unknown", "address": "", "phone": "123", "focus": None, "website": "", "lat": None, "lng": None, "verified": False},  # dirty row
]

# ─────────────────────────────────────────────
# CLEANING FUNCTIONS
# ─────────────────────────────────────────────

def is_valid_phone(phone):
    """Validate Pakistani phone number format."""
    if not phone:
        return False
    cleaned = re.sub(r'[\s\-\(\)]', '', str(phone))
    patterns = [
        r'^0[0-9]{9,10}$',          # 03XX-XXXXXXX
        r'^[0-9]{2,4}[0-9]{7,8}$',  # landline
        r'^N/A$',
    ]
    return any(re.match(p, cleaned) for p in patterns)

def is_valid_coordinates(lat, lng):
    """Check if coordinates are within Pakistan bounds."""
    try:
        lat, lng = float(lat), float(lng)
        return 23.5 <= lat <= 37.5 and 60.5 <= lng <= 77.5
    except (TypeError, ValueError):
        return False

def clean_text(value):
    """Strip whitespace and normalize."""
    if not value:
        return ""
    return str(value).strip().title()

def clean_record(record, record_type):
    """Generic record cleaner. Returns None if record is invalid."""
    name = clean_text(record.get("name", ""))
    if not name:
        return None  # No name = discard

    city = clean_text(record.get("city", ""))
    phone = str(record.get("phone", "")).strip()
    lat = record.get("lat")
    lng = record.get("lng")

    # Validate coordinates
    coords_valid = is_valid_coordinates(lat, lng)

    cleaned = {
        "id": f"{record_type[:2].upper()}-{abs(hash(name + city)) % 100000:05d}",
        "name": name,
        "city": city if city else "Unknown",
        "address": clean_text(record.get("address", "")),
        "phone": phone if is_valid_phone(phone) else "Not Available",
        "hours": record.get("hours", "").strip() or "Not Specified",
        "latitude": float(lat) if coords_valid else None,
        "longitude": float(lng) if coords_valid else None,
        "coordinates_available": coords_valid,
        "verified": bool(record.get("verified", False)),
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
    }

    # Type-specific fields
    if record_type == "food_bank":
        services = record.get("services") or ""
        cleaned["services"] = services.strip() if services else "General food aid"

    elif record_type == "clinic":
        specialties = record.get("specialties") or ""
        cleaned["specialties"] = specialties.strip() if specialties else "General OPD"
        cleaned["free_services"] = bool(record.get("free", False))

    elif record_type == "ngo":
        focus = record.get("focus") or ""
        cleaned["focus_areas"] = focus.strip() if focus else "General welfare"
        cleaned["website"] = record.get("website", "").strip() or "Not Available"

    return cleaned

def clean_dataset(raw_data, record_type):
    """Clean full dataset, return cleaned list + stats."""
    cleaned = []
    skipped = 0
    for record in raw_data:
        result = clean_record(record, record_type)
        if result:
            cleaned.append(result)
        else:
            skipped += 1
    return cleaned, skipped

# ─────────────────────────────────────────────
# EXPORT FUNCTIONS
# ─────────────────────────────────────────────

def save_csv(data, filename, fieldnames):
    """Save dataset as CSV."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)
    print(f"  [CSV] Saved: {filename} ({len(data)} records)")

def save_json(data, filename):
    """Save dataset as JSON."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [JSON] Saved: {filename} ({len(data)} records)")

def save_combined_json(food_banks, clinics, ngos, filename):
    """Save all categories in one combined JSON for RAG pipeline."""
    combined = []
    for item in food_banks:
        combined.append({**item, "category": "food_bank", "category_label": "Food Bank / Langar"})
    for item in clinics:
        combined.append({**item, "category": "clinic", "category_label": "Free / Low-Cost Clinic"})
    for item in ngos:
        combined.append({**item, "category": "ngo", "category_label": "NGO / Welfare Organization"})

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"  [JSON] Combined file saved: {filename} ({len(combined)} total records)")

# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

def run_pipeline():
    output_dir = "smart_aid_data"
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 55)
    print("  Smart Aid – Data Handling Pipeline")
    print("=" * 55)

    # ── Clean all datasets ──
    print("\n[1] Cleaning datasets...")
    food_banks, fb_skipped = clean_dataset(RAW_FOOD_BANKS, "food_bank")
    clinics, cl_skipped = clean_dataset(RAW_CLINICS, "clinic")
    ngos, ng_skipped = clean_dataset(RAW_NGOS, "ngo")

    print(f"  Food Banks : {len(food_banks)} clean, {fb_skipped} skipped")
    print(f"  Clinics    : {len(clinics)} clean, {cl_skipped} skipped")
    print(f"  NGOs       : {len(ngos)} clean, {ng_skipped} skipped")

    # ── Save individual CSV files ──
    print("\n[2] Saving CSV files...")
    fb_fields = ["id", "name", "city", "address", "phone", "services", "hours", "latitude", "longitude", "coordinates_available", "verified", "last_updated"]
    cl_fields = ["id", "name", "city", "address", "phone", "specialties", "free_services", "hours", "latitude", "longitude", "coordinates_available", "verified", "last_updated"]
    ng_fields = ["id", "name", "city", "address", "phone", "focus_areas", "website", "latitude", "longitude", "coordinates_available", "verified", "last_updated"]

    save_csv(food_banks, f"{output_dir}/food_banks.csv", fb_fields)
    save_csv(clinics, f"{output_dir}/clinics.csv", cl_fields)
    save_csv(ngos, f"{output_dir}/ngos.csv", ng_fields)

    # ── Save individual JSON files ──
    print("\n[3] Saving JSON files...")
    save_json(food_banks, f"{output_dir}/food_banks.json")
    save_json(clinics, f"{output_dir}/clinics.json")
    save_json(ngos, f"{output_dir}/ngos.json")

    # ── Save combined JSON for RAG ──
    print("\n[4] Saving combined dataset for RAG pipeline...")
    save_combined_json(food_banks, clinics, ngos, f"{output_dir}/smart_aid_combined.json")

    # ── Print quality report ──
    all_data = food_banks + clinics + ngos
    verified_count = sum(1 for r in all_data if r["verified"])
    coords_count = sum(1 for r in all_data if r["coordinates_available"])

    print("\n" + "=" * 55)
    print("  Data Quality Report")
    print("=" * 55)
    print(f"  Total records    : {len(all_data)}")
    print(f"  Verified records : {verified_count} ({verified_count/len(all_data)*100:.0f}%)")
    print(f"  With coordinates : {coords_count} ({coords_count/len(all_data)*100:.0f}%)")
    print(f"  Total skipped    : {fb_skipped + cl_skipped + ng_skipped} (missing name/invalid)")
    print(f"\n  Output folder    : ./{output_dir}/")
    print("=" * 55)
    print("\n  Files ready for:")
    print("   - Aroba  : smart_aid_combined.json  (RAG embeddings)")
    print("   - Zubair : food_banks.json / clinics.json / ngos.json (API)")
    print("   - Zubair : all JSON files have lat/lng for Maps API")
    print("=" * 55)



if __name__ == "__main__":
    run_pipeline()
