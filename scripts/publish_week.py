"""Publish an explicitly approved weekly plan to Firestore (GitHub Actions only)."""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import firebase_admin
from firebase_admin import credentials, firestore

TZ = ZoneInfo("Europe/Berlin")
PLAN_PATH = Path("approved/next-week.json")


def fail(message):
    print("NOT PUBLISHED:", message)
    sys.exit(0)


def main():
    now = datetime.now(TZ)
    if now.weekday() != 3 or now.hour < 8:
        fail("Only Thursdays after 08:00 Europe/Berlin are eligible.")
    if not PLAN_PATH.is_file():
        fail("No approved plan file exists.")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    if plan.get("approved") is not True:
        fail("Plan lacks explicit approval.")
    if not isinstance(plan.get("approved_by"), str) or plan["approved_by"] != "Malcolm":
        fail("Approval identity missing.")
    if not isinstance(plan.get("approval_recorded_at"), str) or not plan["approval_recorded_at"].strip():
        fail("Approval record missing.")
    publication_date = plan.get("publish_on")
    if publication_date != now.date().isoformat():
        fail("Plan is not approved for this Thursday.")
    title = plan.get("title")
    recipes = plan.get("recipes")
    items = plan.get("items")
    if not isinstance(title, str) or not 3 <= len(title.strip()) <= 90:
        fail("Invalid week title.")
    if not isinstance(recipes, list) or len(recipes) != 5 or not all(isinstance(x, str) and 20 <= len(x) <= 12000 for x in recipes):
        fail("Five complete recipes required.")
    if not isinstance(items, list) or not 1 <= len(items) <= 200 or not all(isinstance(x, str) and 2 <= len(x.strip()) <= 120 for x in items):
        fail("Invalid shopping list.")
    if len(set(items)) != len(items):
        fail("Duplicate shopping items; consolidate quantities first.")
    secret = os.environ.get("FIREBASE_SERVICE_ACCOUNT")
    if not secret:
        raise RuntimeError("Missing FIREBASE_SERVICE_ACCOUNT GitHub Actions secret.")
    service_account = json.loads(secret)
    if service_account.get("project_id") != "einkaufsplanung-malcolm-nele":
        raise RuntimeError("Service account project does not match.")
    firebase_admin.initialize_app(credentials.Certificate(service_account))
    db = firestore.client()
    week_ref = db.document("lists/shared/meta/currentWeek")
    old_items = list(db.collection("lists/shared/items").stream())
    if len(old_items) + len(items) + 1 > 490:
        raise RuntimeError("Too many Firestore batch operations.")
    current = week_ref.get()
    if current.exists and current.to_dict().get("publish_on") == publication_date:
        fail("This week's plan was already published.")
    batch = db.batch()
    for old in old_items:
        batch.delete(old.reference)
    for index, name in enumerate(items):
        batch.set(db.document(f"lists/shared/items/week-{index + 1:03d}"),
                  {"name": name.strip(), "checked": False, "order": index})
    batch.set(week_ref, {
        "title": title.strip(),
        "recipes": recipes,
        "publish_on": publication_date,
        "approved_by": "Malcolm",
        "updatedAt": datetime.now(TZ).isoformat(),
    })
    batch.commit()
    print(f"PUBLISHED: {title}, {len(items)} items, {len(recipes)} recipes.")


if __name__ == "__main__":
    main()
