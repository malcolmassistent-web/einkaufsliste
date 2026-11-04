# Automatische Wochenveröffentlichung – Entwurf (noch nicht aktiv)

Ziel: Mittwoch Rezeptvorschläge in ChatGPT, beliebige Überarbeitung, ausschließlich nach ausdrücklicher Freigabe veröffentlichen; Donnerstag ab 08:00 Europe/Berlin. Ohne Freigabe keine Änderung. Firebase Spark beibehalten.

## Geprüfter Bestand (2026-11-04)
- GitHub Pages mit index.html; Firebase Authentication und Firestore.
- Webseite enthält bereits Admin-Veröffentlichungsformular, Wochenplan-Dokument und synchronisierte Einkaufsliste.
- GitHub-Connector kann Repository lesen. Schreibrechte werden gesondert getestet.

## Vorgesehene sichere Architektur
1. Freigegebener Plan wird als versioniertes JSON in einen geschützten Übergabekanal geschrieben, inklusive Woche, 5 Rezepten, Zutaten, Kochanleitungen, Freigabezeit und Freigabekennung. Die ChatGPT-zu-GitHub-Übergabe muss tatsächlich getestet werden; eine Chat-Nachricht allein ist kein automatischer Trigger.
2. GitHub Actions prüft donnerstags (Europe/Berlin, Sommer-/Winterzeit beachten) auf einen gültigen, noch nicht veröffentlichten freigegebenen Plan. GitHub-Zeitpläne können verzögert starten; 08:00 ist Zielzeit, keine sekundengenaue Garantie.
3. Workflow authentifiziert sich serverseitig mit in GitHub Actions Secrets hinterlegten Firebase-Service-Credentials, prüft JSON und Zielwoche, veröffentlicht atomar in Firestore und protokolliert die Plan-ID zur Vermeidung doppelter Veröffentlichungen.
4. Kein Plan oder ungültige Freigabe: keine Änderung. Bereits veröffentlichter Plan: keine Wiederholung. Bei Fehler: aktuelle Liste erhalten, Fehlermeldung.
5. Sicherheitsregeln: Nutzer dürfen Listen abhaken; Veröffentlichungsrechte nur für Malcolm bzw. vertrauenswürdigen Server. Firestore-Regeln vor Livebetrieb prüfen.

## Vor Aktivierung offen
- ChatGPT-Freigabe nachweislich und sicher in den Übergabekanal bringen.
- GitHub Actions Secrets und Firebase Admin-Zugriff konfigurieren, ohne Schlüssel im öffentlichen Repository abzulegen.
- Webseite/Firestore-Schema auf sichere, konsistente Wochenumschaltung und Vermeidung der alten Initialdaten-Rücksetzung prüfen.
- Test mit Dummy-Woche und beiden Accounts, erst danach Zeitplan aktivieren.

**Status: Planung. Keine produktive Automatisierung aktiviert, keine Einkaufslisten verändert.**
