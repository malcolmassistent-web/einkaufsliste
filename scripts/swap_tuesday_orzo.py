"""Apply the approved Tuesday recipe swap to the *live* Firestore week safely.

Run only via the manual GitHub Actions workflow. No wholesale list replacement.
"""
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

import firebase_admin
from firebase_admin import credentials, firestore

EXPECTED_TITLE = "Vegetarischer Wochenplan · 9.–13. November 2026"
OLD_RECIPE_START = "Dienstag – Gefüllte Paprika mit Couscous und Feta"
NEW_RECIPE = """Dienstag – Mediterrane Orzo-Pfanne mit Feta
Für 2 Personen · ca. 25 Minuten
Zutaten: 200 g Orzo (Kritharaki), 200 g Kirschtomaten, 1 kleine Zucchini, 150 g Feta, 1 kleine Zwiebel, 2 Knoblauchzehen, 400 ml Gemüsebrühe, 1 EL Olivenöl, 1 TL italienische Kräuter, Salz, Pfeffer.
Zubereitung:
1. Zwiebel und Knoblauch fein hacken, Zucchini würfeln und Kirschtomaten halbieren.
2. Zwiebel und Knoblauch in Olivenöl anschwitzen, Zucchini 3 Minuten mitbraten.
3. Orzo und Tomaten zugeben, mit Gemüsebrühe aufgießen.
4. 12–15 Minuten sanft köcheln lassen, regelmäßig umrühren und bei Bedarf Wasser nachgießen.
5. Feta darüberbröseln und mit Kräutern, Salz und Pfeffer abschmecken."""
# Only exact original shopping-list entries may be changed.
REPLACE = {
    "Paprika — 3 Stück (davon 2 große)": "Paprika — 1 Stück",
    "Kirschtomaten — 400 g": "Kirschtomaten — 450 g",
    "Knoblauch — 2 Zehen": "Knoblauch — 4 Zehen",
    "Gemüsebrühe — für 350 ml": "Gemüsebrühe — für 600 ml",
    "Zucchini — 1 Stück (ca. 250 g)": "Zucchini — 2 Stück (ca. 500 g)",
    "Couscous — 120 g": None,
}
NEW_ITEM = "Orzo (Kritharaki) — 200 g"

secret = json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT"])
if secret.get("project_id") != "einkaufsplanung-malcolm-nele":
    raise RuntimeError("Unexpected Firebase project")
firebase_admin.initialize_app(credentials.Certificate(secret))
db = firestore.client()
week_ref = db.document("lists/shared/meta/currentWeek")
items_ref = db.collection("lists/shared/items")
transaction = db.transaction()

@firestore.transactional
def apply(tx):
    week_snap = week_ref.get(transaction=tx)
    if not week_snap.exists:
        raise RuntimeError("Current week missing")
    week = week_snap.to_dict()
    if week.get("title") != EXPECTED_TITLE or week.get("publish_on") != "2026-11-05":
        raise RuntimeError("Current week differs; refusing to modify")
    recipes = week.get("recipes")
    if not isinstance(recipes, list) or len(recipes) != 5:
        raise RuntimeError("Unexpected recipe structure")
    if recipes[1] == NEW_RECIPE:
        print("Recipe already updated; no changes made")
        return
    if not isinstance(recipes[1], str) or not recipes[1].startswith(OLD_RECIPE_START):
        raise RuntimeError("Tuesday recipe changed; refusing to overwrite")
    snapshots = list(tx.get(items_ref))
    by_name = {}
    for snap in snapshots:
        data = snap.to_dict()
        if data.get("name") in by_name:
            raise RuntimeError("Duplicate item name; manual review required")
        by_name[data.get("name")] = snap
    if any(old not in by_name for old in REPLACE):
        raise RuntimeError("Shopping list differs; refusing to overwrite")
    if NEW_ITEM in by_name or any(new in by_name for new in REPLACE.values() if new):
        raise RuntimeError("Replacement item already exists; manual review required")
    if any(by_name[old].to_dict().get("checked") for old in REPLACE):
        raise RuntimeError("A changed item is checked; manual review required")
    # All reads are complete before transaction writes.
    new_recipes = list(recipes)
    new_recipes[1] = NEW_RECIPE
    tx.update(week_ref, {"recipes": new_recipes, "updatedAt": datetime.now(ZoneInfo("Europe/Berlin")).isoformat()})
    for old, new in REPLACE.items():
        ref = by_name[old].reference
        if new is None:
            tx.delete(ref)
        else:
            tx.update(ref, {"name": new})
    highest_order = max((s.to_dict().get("order", 0) for s in snapshots), default=0)
    tx.set(items_ref.document(), {"name": NEW_ITEM, "checked": False, "order": highest_order + 1})
    print("UPDATED: Tuesday recipe and 7 shopping list operations")

apply(transaction)
