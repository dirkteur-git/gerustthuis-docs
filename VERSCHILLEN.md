# Documentatie Verschillen Rapport

> Gegeneerd op 2026-02-14 door vergelijking van alle MD-bestanden met de actuele codebase.
> **Status: ALLE FIXES DOORGEVOERD op 2026-02-14**

## Samenvatting

Alle 13 must-fix items en 5 should-fix items zijn doorgevoerd. Daarnaast zijn opgeruimd:
- `CREDENTIALS.md` uit git tracking verwijderd (bevatte echte wachtwoorden/tokens)
- `index.html` verwijderd (verouderde architectuur pagina met oude repo namen)
- `.gitignore` aangemaakt
- `README.md` bijgewerkt met ARCHITECTURE.md link en gerustthuis-app repo

---

## Overzicht per document

| Document | Vorige Status | Huidige Status | Fixes |
|----------|---------------|----------------|-------|
| ARCHITECTURE.md | Verouderd | Bijgewerkt | Edge functions, room_activity_hourly, views, Tailwind, projectplan, app |
| DATABASE_DESIGN.md | Verouderd | Bijgewerkt | room_activity_hourly TABLE, superadmin, pg_cron, kolomtypes |
| PORTAAL_ARCHITECTURE.md | Incompleet | Bijgewerkt | tabelnaam, z-score, rolling comparison, households, components |
| ANOMALY_DETECTION.md | Goed | Bijgewerkt | utility functions lijst compleet, Dashboard beschrijving |
| HUE_INTEGRATION.md | Verouderd | Bijgewerkt | battery verwijderd, functienaam, device discovery, status herstel |
| ROADMAP.md | Redelijk | Bijgewerkt | migratielijst compleet, nieuwe items |
| docs/database/schema.md | Verouderd | Bijgewerkt | VIEW→TABLE, pg_cron |
| docs/overview/architecture.md | Incompleet | Bijgewerkt | iOS app, functienaam |
| Brandbook.md | Correct | Correct | - |
| README.md | Correct | Bijgewerkt | ARCHITECTURE.md link, gerustthuis-app repo |

---

## Doorgevoerde wijzigingen

### ARCHITECTURE.md
1. Edge functions tabel bijgewerkt: `hue-sync-state` (was `hue-poll-state`), `hue-poll-battery` verwijderd
2. `room_activity_hourly` als TABLE gedocumenteerd (was VIEW)
3. Portaal Tailwind versie: v3 (was ongespecificeerd, implying v4)
4. Ontbrekende views toegevoegd (HueConnect, HueCallback, AcceptInvitation, Login)
5. `gerustthuis-projectplan` sectie toegevoegd
6. `gerustthuis-app` (iOS) sectie toegevoegd
7. `room_activity_hourly` toegevoegd aan kerntabellen lijst
8. Data flow diagram bijgewerkt

### DATABASE_DESIGN.md
1. `room_activity_hourly` herschreven van VIEW naar TABLE met RLS
2. `get_accessible_config_ids()` functie al correct (geen superadmin)
3. pg_cron jobs sectie toegevoegd met `aggregate_hourly_activity()` en `refresh_daily_activity_stats()`
4. `first_activity`/`last_activity` kolomtype: TIME → TEXT
5. Data flow: room_activity_hourly als TABLE, pg_cron aggregatie
6. RLS sectie bijgewerkt: TABLE met eigen policies
7. `rooms_available` beschrijving verduidelijkt
8. Datum bijgewerkt naar 2026-02-14

### PORTAAL_ARCHITECTURE.md
1. `getRecentEvents()` tabelnaam: `activity_events` → `raw_events`
2. Status banner: z-score-gebaseerde detectie gedocumenteerd
3. Rolling vergelijking uitgelegd
4. Household multi-tenancy sectie toegevoegd (state, functies, config selectie)
5. Hue config query: via householdConfigId / accessible configs
6. `/analyse` route notitie toegevoegd (developer view)
7. `components/` directory aan project structuur toegevoegd
8. Dashboard fallback gedocumenteerd
9. Per View tabel uitgebreid met Patronen en Analyse

### HUE_INTEGRATION.md
1. `hue-poll-battery` sectie volledig verwijderd
2. Automatisch status herstel: claim vervangen door "niet geïmplementeerd" notitie
3. `hue-poll-state` → `hue-sync-state` overal hernoemd
4. Device discovery sectie toegevoegd
5. V2 API `hue-application-key` header gedocumenteerd
6. `hasStateChanged()` notitie: ongebruikt, per device type eigen logica
7. Temperature/light sensors: notitie dat ze niet actief gemonitord worden
8. Polling schedule: alleen `hue-sync-state` (battery row verwijderd)

### ANOMALY_DETECTION.md
1. Alle 15 utility functions + 4 constanten gedocumenteerd
2. Dashboard.vue beschrijving: z-score status banner (was "simpele ratio-check")
3. Datum bijgewerkt naar 2026-02-14

### ROADMAP.md
1. Multi-tenant RLS migratielijst: 005, 007, 010-018 (was 010-017)
2. Data Pipeline migraties: 015-020 (was 015-017)
3. Nieuwe completed items: Aggregatie Automatisering, Sensor Type Tracking, 18-Feature Anomaly Detection, iOS App
4. Changelog v0.3.0 uitgebreid

### docs/database/schema.md
1. `room_activity_hourly`: VIEW → TABLE met RLS (pg_cron)

### docs/overview/architecture.md
1. `hue-poll-state` → `hue-sync-state` in diagram
2. iOS App (Expo) toegevoegd aan architectuur diagram

### README.md
1. `ARCHITECTURE.md` link toegevoegd aan documentatie tabel
2. `gerustthuis-app` repo toegevoegd aan repositories tabel

### Opruiming
1. `CREDENTIALS.md` uit git tracking verwijderd (bevatte wachtwoorden, API tokens)
2. `.gitignore` aangemaakt met CREDENTIALS.md
3. Verouderde `index.html` verwijderd (verwees naar niet-bestaande repo's)
