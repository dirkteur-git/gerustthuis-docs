# Integratie Architectuur

GerustThuis werkt uitsluitend met **bestaande smart home ecosystemen** — hardware die huishoudens al hebben. GerustThuis installeert geen eigen kastjes of sensoren.

Zie [ADR-003](../decisions/ADR-003-hue-first-extensible.md) voor de beslissing en het principe.

---

## Principe: bestaande hubs als databron

```mermaid
flowchart LR
    HUE[Philips Hue Bridge\nAl in huis · ZigBee]
    IKEA[IKEA Dirigera\nAl in huis · Matter/ZigBee]
    AQARA[Aqara Hub M2/M3\nAl in huis · ZigBee/Matter]
    SONOFF[Sonoff\nAl in huis · WiFi · eWeLink]

    EDGE[Supabase Edge Function\nper ecosysteem]
    CFG[integrations.{naam}_config\nOAuth tokens + hub info]
    DEV[integrations.{naam}_devices\nDevice status]
    EVT[activity.activity_events]
    RA[activity.room_activity]

    HUE -->|Cloud API + OAuth| EDGE
    IKEA -->|Cloud API + OAuth| EDGE
    AQARA -->|Cloud of lokale API| EDGE
    SONOFF -->|eWeLink Cloud API| EDGE
    EDGE --> CFG
    EDGE --> DEV
    EDGE --> EVT
    EDGE --> RA
```

---

## Contract: wat elke integratie moet leveren

### 1. Config tabel (`integrations.{naam}_config`)

Bevat auth-gegevens en hub-informatie per huishouden.

| Kolom | Type | Beschrijving |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `household_id` | UUID | Koppeling naar `public.households` |
| `bridge_id` | TEXT | Unieke identifier van de hub |
| `access_token` | TEXT | OAuth access token |
| `refresh_token` | TEXT | OAuth refresh token |
| `token_expires_at` | TIMESTAMPTZ | Vervaltijd access token |
| `created_at` | TIMESTAMPTZ | — |
| `updated_at` | TIMESTAMPTZ | — |

**RLS:** Gebruiker ziet alleen eigen config via `get_accessible_config_ids()`.

### 2. Devices tabel (`integrations.{naam}_devices`)

Bevat alle bekende devices van de integratie, inclusief huidige staat.

| Kolom | Type | Beschrijving |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `config_id` | UUID | Koppeling naar config tabel |
| `device_id` | TEXT | Extern device-ID (hub-specifiek) |
| `device_type` | TEXT | `motion` / `contact` / `light` / `button` |
| `room_name` | TEXT | Kamernaam (vrije tekst, bijv. "Woonkamer") |
| `last_state` | JSONB | Laatste bekende staat |
| `last_seen_at` | TIMESTAMPTZ | Laatste succesvolle polling |
| `created_at` | TIMESTAMPTZ | — |
| `updated_at` | TIMESTAMPTZ | — |

### 3. Events schrijven naar `activity.activity_events`

Bij elke state-change schrijft de integratie een event.

| Kolom | Waarde |
|-------|--------|
| `config_id` | UUID van de integratie-config |
| `device_id` | Extern device-ID |
| `event_type` | `motion_detected` / `contact_opened` / `contact_closed` / `light_on` / `light_off` |
| `room_name` | Kamernaam van het device |
| `occurred_at` | Tijdstip van het event |
| `raw_data` | JSONB — optionele extra info |

### 4. Room activity bijwerken in `activity.room_activity`

Na elke polling UPSERT de integratie een 5-minuten window per kamer.

| Kolom | Waarde |
|-------|--------|
| `config_id` | UUID van de integratie-config |
| `room_name` | Kamernaam |
| `window_start` | Afgerond naar 5-minuten |
| `motion_count` | Aantal motion events in dit window |
| `contact_changes` | Aantal contact-state-changes in dit window |
| `lights_active` | Boolean — waren er lampen aan? |

---

## Huidige integraties

### Philips Hue (actief)

| Eigenschap | Waarde |
|------------|--------|
| Type | Cloud API (Hue Remote) |
| Auth | OAuth 2.0 |
| Polling | Elke 5 minuten via Supabase Edge Function `hue-sync-state` |
| API versie | v1 (clip) + v2 (events) |
| Config tabel | `integrations.hue_config` |
| Devices tabel | `integrations.hue_devices` |
| Docs | [hue-integration.md](hue-integration.md) |

---

## Toekomstige integraties

### IKEA Dirigera (volgende prioriteit)

| Eigenschap | Waarde |
|------------|--------|
| Hub | IKEA Dirigera (opvolger van Trådfri Gateway) |
| Type | Cloud API + lokale REST API |
| Auth | OAuth 2.0 |
| Sensor types | Motion, contact, licht, knop |
| Aanpak | Zelfde patroon als Hue: Edge Function + config/devices tabellen |
| Opmerking | Lokale API is ook beschikbaar — minder cloud-afhankelijk dan Hue |

### Aqara (gepland)

| Eigenschap | Waarde |
|------------|--------|
| Hub | Aqara Hub M2 of M3 |
| Type | Cloud API + lokale LAN API |
| Auth | OAuth 2.0 (Aqara cloud) of lokale token |
| Sensor types | Motion, contact, aanwezigheid (mmWave), licht, temperatuur, vochtigheid |
| Aanpak | Edge Function voor cloud API; lokale API als fallback |
| Opmerking | Aqara heeft goede sensor-variëteit, inclusief mmWave aanwezigheidsdetectie |

### Sonoff / eWeLink (gepland)

| Eigenschap | Waarde |
|------------|--------|
| Website | [sonoff.nl](https://www.sonoff.nl/) |
| Hub | NSPanel Pro of eWeLink cloud (geen aparte hub vereist) |
| Type | eWeLink Cloud API |
| Auth | eWeLink OAuth |
| Sensor types | Motion, contact (deur/raam), temperatuur, vochtigheid, slimme stekkers |
| Prijs | Goedkoopste sensoren op de markt — drempel voor nieuwe gebruikers laag |
| Aanpak | Edge Function via eWeLink API, zelfde patroon als Hue |
| Opmerking | Populair bij doe-het-zelvers; ook Matter-ondersteuning in nieuwere modellen |

### Apple HomeKit (gepland)

| Eigenschap | Waarde |
|------------|--------|
| Hub | HomePod mini, Apple TV 4K, iPad (thuis als hub) |
| Type | HomeKit Accessory Protocol (HAP) — lokaal + iCloud |
| Aanpak | HomeKit bridge of Matter-koppeling |
| Opmerking | Relevant voor iOS-heavy doelgroep; vereist extra technische aanpak |

---

## Een nieuwe integratie toevoegen

Checklist voor een nieuwe sensorintegratie:

```
□ Verificeer: werkt het met hardware die huishoudens al hebben?
  (Geen eigen kastje, geen monteur, geen huurkosten)

□ Maak migrations aan:
  □ integrations.{naam}_config tabel (met RLS)
  □ integrations.{naam}_devices tabel (met RLS)
  □ RLS policies die get_accessible_config_ids() uitbreiden

□ Schrijf de Edge Function:
  □ Auth flow (OAuth of lokale token opslag)
  □ Device discovery bij eerste koppeling
  □ Polling elke 5 min of event-listener
  □ State vergelijking (alleen bij change een event schrijven)
  □ Schrijf naar activity_events en room_activity

□ Frontend:
  □ Koppelpagina (OAuth flow of lokale setup wizard)
  □ De activiteitsdata zelf wijzigt niet — is al integratie-agnostisch

□ Docs:
  □ Voeg toe aan integrations.md (dit bestand)
  □ Voeg toe aan ADR-003 roadmap
```
