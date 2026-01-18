# Database Schema

## Overzicht

GerustThuis gebruikt twee databases:
1. **SQLite** (lokaal op Raspberry Pi) - ruwe sensor events
2. **Supabase** (cloud) - samenvattingen, alerts, configuratie

## Lokale Database (SQLite)

**Locatie:** Raspberry Pi (`/var/lib/gerustthuis/data.db`)

### `sensor_events`

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | INTEGER | Primary key |
| timestamp | DATETIME | Event tijdstip |
| device_id | TEXT | Zigbee device ID |
| event_type | TEXT | motion, contact, vibration |
| value | TEXT | true/false of numeriek |
| battery | INTEGER | Batterij percentage |

### `hourly_summary`

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | INTEGER | Primary key |
| hour | DATETIME | Uur (afgerond) |
| device_id | TEXT | Zigbee device ID |
| event_count | INTEGER | Aantal events |
| first_event | DATETIME | Eerste event in uur |
| last_event | DATETIME | Laatste event in uur |

**Retention:** 7-14 dagen (configureerbaar)

---

## Cloud Database (Supabase)

**URL:** Configureerbaar per deployment

### `households`

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | uuid | Primary key |
| name | text | Naam huishouden |
| timezone | text | Tijdzone |
| thresholds_json | jsonb | Alert configuratie |
| created_at | timestamp | Aanmaakdatum |

### `gateways`

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | uuid | Primary key |
| household_id | uuid | FK naar households |
| api_key_hash | text | Hashed API key (bcrypt) |
| last_seen | timestamp | Laatste heartbeat |
| version | text | Software versie |
| status | text | online, offline, degraded |

### `gateway_health`

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | uuid | Primary key |
| gateway_id | uuid | FK naar gateways |
| recorded_at | timestamp | Meetmoment |
| cpu_temp | float | CPU temperatuur (°C) |
| cpu_usage | float | CPU gebruik (%) |
| memory_usage | float | RAM gebruik (%) |
| disk_usage | float | Disk gebruik (%) |
| uptime_seconds | int | Uptime in seconden |
| zigbee_devices | int | Aantal gekoppelde devices |
| mqtt_connected | boolean | MQTT broker status |

### `daily_summaries`

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | uuid | Primary key |
| household_id | uuid | FK naar households |
| date | date | Datum |
| first_activity | time | Eerste activiteit |
| last_activity | time | Laatste activiteit |
| total_events | int | Totaal events |
| rooms_visited | jsonb | Array van bezochte kamers met counts |
| anomaly_score | float | Afwijkingsscore (0-1) |
| anomaly_flags | jsonb | Welke anomalieën gedetecteerd |

### `alerts`

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | uuid | Primary key |
| household_id | uuid | FK naar households |
| type | text | no_activity, anomaly, battery_low |
| severity | text | info, warning, critical |
| message | text | Beschrijving |
| acknowledged | boolean | Gezien door mantelzorger |
| created_at | timestamp | Aanmaakdatum |

### `organizations` (B2B)

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | uuid | Primary key |
| name | text | Organisatie naam |
| slug | text | URL-friendly naam |
| contact_email | text | Contact email |
| contact_phone | text | Contact telefoon |
| address | jsonb | Adresgegevens |
| settings | jsonb | Organisatie instellingen |
| created_at | timestamp | Aanmaakdatum |

### `rooms` (B2B)

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | uuid | Primary key |
| organization_id | uuid | FK naar organizations |
| name | text | Kamer naam |
| floor | int | Verdieping |
| resident_id | uuid | FK naar residents |
| sensors | jsonb | Gekoppelde sensoren |
| status | text | active, inactive |
| created_at | timestamp | Aanmaakdatum |

### `residents` (B2B)

| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | uuid | Primary key |
| organization_id | uuid | FK naar organizations |
| first_name | text | Voornaam |
| last_name | text | Achternaam |
| room_id | uuid | FK naar rooms |
| date_of_birth | date | Geboortedatum |
| notes | text | Notities |
| emergency_contacts | jsonb | Noodcontacten |
| created_at | timestamp | Aanmaakdatum |

---

## Row Level Security (RLS)

Alle tabellen hebben RLS policies:

- **households:** Alleen leden van het huishouden
- **organizations:** Alleen medewerkers van de organisatie
- **alerts:** Alleen voor eigen household/organization
- **gateways:** Alleen eigenaar household
