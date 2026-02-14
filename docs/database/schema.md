# Database Schema

## Overzicht

GerustThuis gebruikt **Supabase PostgreSQL** als enige database. Alle tabellen zijn beveiligd met Row Level Security (RLS).

Zie [DATABASE_DESIGN.md](../../DATABASE_DESIGN.md) voor het volledige schema met alle kolommen, indexen en queries.

## Tabellen

### Sensordata

| Tabel | Beschrijving |
|-------|--------------|
| `hue_config` | OAuth tokens en bridge configuratie per gebruiker |
| `hue_devices` | Alle Hue devices (lampen, sensoren, knoppen) met huidige state |
| `physical_devices` | Groepering van multi-capability sensoren (motion + temp + light) |
| `activity_events` | Ruwe sensor events (append-only log) |
| `room_activity` | 5-minuten aggregaties per kamer |
| `daily_activity_stats` | Dagelijkse statistieken per bewoner |

### Aggregatie Tabellen

| Tabel | Beschrijving |
|-------|--------------|
| `room_activity_hourly` | Uurlijkse aggregatie per kamer (TABLE met RLS, gevuld door pg_cron) |

### Gebruikers & Multi-tenancy

| Tabel | Beschrijving |
|-------|--------------|
| `user_profiles` | Gebruikersprofiel (display_name, active_household_id) |
| `households` | Huishoudens (naam, gekoppelde config_id) |
| `household_members` | Lidmaatschap met rollen (admin/viewer) |
| `household_invitations` | Uitnodigingen voor huishoudens |

## Row Level Security

Alle tabellen gebruiken RLS. De centrale functie `get_accessible_config_ids()` bepaalt welke data een gebruiker mag zien op basis van:
1. Household membership (via `household_members`)
2. Directe email match op `hue_config` (fallback)

## Toekomstig: Lokale Database

> **Nog niet geïmplementeerd.** Bij introductie van de Raspberry Pi gateway wordt een lokale SQLite database toegevoegd:

| Tabel | Beschrijving |
|-------|--------------|
| `sensor_events` | Ruwe Zigbee sensor events (lokaal, 14 dagen retentie) |
| `hourly_summary` | Uurlijkse aggregatie per device |

De lokale database houdt de ruwe data. Alleen aggregaties worden naar Supabase gesynchroniseerd.
