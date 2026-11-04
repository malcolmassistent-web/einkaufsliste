# Automatische Veröffentlichung – Einrichtung

**Stand:** GitHub Actions und Veröffentlichungsskript sind vorbereitet. **Ohne ausdrücklich freigegebenen Plan und gültiges Firebase-Secret erfolgt keine Veröffentlichung.**

## Ablauf
1. Mittwoch: Rezepte in ChatGPT abstimmen. Änderungen jederzeit möglich.
2. Erst nach der ausdrücklichen Nachricht „Wochenplan freigeben“ wird ein Plan als `approved/next-week.json` vorgemerkt. Das muss durch einen Schreibvorgang in GitHub erfolgen – eine Chat-Nachricht allein genügt nicht.
3. Donnerstag ab 08:00 Uhr (Europe/Berlin): GitHub Actions prüft Freigabe, Datum und vollständige Daten. Danach ersetzt es die Einkaufsliste und den Wochenplan atomar in Firestore. Alle Häkchen werden auf `false` gesetzt.
4. Fehlt eine Freigabe, bleibt die bestehende Liste unverändert.

## Einmalige Einrichtung
GitHub Repository → Settings → Secrets and variables → Actions → New repository secret.
Name: `FIREBASE_SERVICE_ACCOUNT`. Wert: **vollständiger JSON-Inhalt eines Firebase-Service-Account-Schlüssels** für das Projekt `einkaufsplanung-malcolm-nele`. Niemals Schlüssel in den Chat oder als Datei in das öffentliche Repository hochladen. Service-Account-Schlüssel sind hochprivilegiert; nach Möglichkeit einen eigens für diese Aufgabe angelegten Account mit minimalen Firestore-Berechtigungen nutzen.

Danach mit einem Testplan und einem manuellen Workflow-Lauf testen. Erst dann echten Wochenplan freigeben.

## JSON-Format der Freigabe
```json
{
  "approved": true,
  "approved_by": "Malcolm",
  "approval_recorded_at": "2026-11-04T18:00:00+01:00",
  "publish_on": "2026-11-05",
  "title": "9.–13. November 2026",
  "recipes": ["Montag · Gericht\\nZutaten ...\\n1. ...", "Dienstag · ...", "Mittwoch · ...", "Donnerstag · ...", "Freitag · ..."],
  "items": ["Brokkoli — 600 g", "Reis — 500 g"]
}
```

Das Beispiel ist **kein** freigegebener Plan und wird nicht in `approved/next-week.json` abgelegt.

**Hinweis:** GitHub Actions-Zeitpläne können sich verzögern. Der Job wird an mehreren UTC-Zeitpunkten gestartet; dank Datumssperre und Veröffentlichungsmarker wird dieselbe Woche nicht mehrfach veröffentlicht. Die bestehende ChatGPT-Donnerstags-Automation erzeugt aktuell noch eigene Ausgaben und muss nach erfolgreichem Test an den neuen Ablauf angepasst werden.
