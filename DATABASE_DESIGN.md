# GerustThuis Database Design

Actuele database structuur in Supabase (gerustthuis-supabase).

**Laatst bijgewerkt:** 2026-01-31

---

## Tabellen Overzicht

```
┌─────────────────┐     ┌─────────────────┐
│   hue_config    │────<│   hue_devices   │
│  (OAuth tokens) │     │ (lampen/sensors)│
└────────┬────────┘     └────────┬────────┘
         │                       │
         │              ┌────────┴────────┐
         │              │                 │
         │     ┌────────▼────────┐  ┌─────▼─────────────┐
         │     │ activity_events │  │ physical_devices  │
         │     │  (alle events)  │  │ (sensor grouping) │
         │     └────────┬────────┘  └───────────────────┘
         │              │
         │     ┌────────┴────────────────────┐
         │     │                             │
         │     ▼                             ▼
         │  ┌────────────────┐    ┌─────────────────────┐
         │  │ room_activity  │    │ daily_activity_stats│
         │  │(5-min aggregat)│    │   (dag statistiek)  │
         │  └───────┬────────┘    └─────────────────────┘
         │          │
         │  ┌───────▼────────────┐
         └─>│room_activity_hourly│
            │      (view)        │
            └────────────────────┘
```

---

## Tabellen

### 1. `hue_config` - OAuth configuratie per gebruiker

```sql
CREATE TABLE hue_config (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email        VARCHAR(255) NOT NULL UNIQUE,
    access_token      TEXT NOT NULL,
    refresh_token     TEXT NOT NULL,
    token_expires_at  TIMESTAMPTZ NOT NULL,
    bridge_username   VARCHAR(255),        -- Whitelist ID van Hue Bridge
    bridge_id         VARCHAR(255),        -- Bridge identifier
    status            VARCHAR(20) DEFAULT 'active',  -- active, error, expired
    last_sync_at      TIMESTAMPTZ,         -- Laatste succesvolle poll
    last_error        TEXT,                -- Foutmelding bij problemen
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);
```

**Status waarden:**
- `active` - Normaal werkend
- `error` - Token refresh gefaald
- `expired` - Token verlopen en niet ververst

---

### 2. `hue_devices` - Individuele devices met huidige state

```sql
CREATE TABLE hue_devices (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id           UUID REFERENCES hue_config(id) ON DELETE CASCADE,
    hue_id              VARCHAR(255) NOT NULL,    -- v1 API ID ("1", "2", etc)
    hue_unique_id       VARCHAR(255),             -- MAC-based unique ID
    device_type         VARCHAR(50) NOT NULL,     -- Zie device types
    name                VARCHAR(255),
    room_name           VARCHAR(255),
    last_state          JSONB DEFAULT '{}',       -- Huidige state snapshot
    last_state_at       TIMESTAMPTZ,
    physical_device_id  UUID REFERENCES physical_devices(id),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(config_id, hue_unique_id)
);

CREATE INDEX idx_hue_devices_config ON hue_devices(config_id);
CREATE INDEX idx_hue_devices_type ON hue_devices(device_type);
CREATE INDEX idx_hue_devices_room ON hue_devices(room_name);
```

**Device types:**
| Type | Beschrijving |
|------|--------------|
| `light` | Lamp of lichtgroep |
| `motion_sensor` | Bewegingssensor |
| `contact_sensor` | Deur/raam sensor |
| `temperature_sensor` | Temperatuur |
| `light_sensor` | Lichtsterkte |
| `button` | Dimmer, schakelaar |

**last_state voorbeelden:**

```jsonc
// Lamp
{
  "on": true,
  "bri": 254,
  "ct": 369,
  "reachable": true
}

// Motion sensor
{
  "presence": true,
  "temperature": 21.5,    // Verrijkt met temp sensor data
  "lightlevel": 17000,    // Verrijkt met light sensor data
  "lastupdated": "2024-01-15T14:30:00"
}

// Contact sensor
{
  "open": false,          // false = dicht, true = open
  "lastupdated": "2024-01-15T14:30:00"
}
```

---

### 3. `physical_devices` - Groepering van multi-capability sensoren

```sql
CREATE TABLE physical_devices (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id           UUID REFERENCES hue_config(id) ON DELETE CASCADE,
    mac_prefix          VARCHAR(23) NOT NULL,     -- Eerste 23 chars van MAC
    name                VARCHAR(255),
    room_name           VARCHAR(255),
    manufacturer        VARCHAR(100) DEFAULT 'Philips',
    model               VARCHAR(100),
    battery_level       INTEGER,                  -- 0-100%
    battery_updated_at  TIMESTAMPTZ,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(config_id, mac_prefix)
);
```

**Doel:** Hue motion sensoren hebben 3 capabilities (motion, temp, light) die als aparte "sensors" in de API komen. Deze tabel groepeert ze op fysiek apparaat.

**Voorbeeld:**
```
Physical Device: "Hal Sensor" (mac_prefix: 00:17:88:01:0b:12:34)
  └── hue_devices: motion_sensor (presence)
  └── hue_devices: temperature_sensor (verborgen, data naar motion)
  └── hue_devices: light_sensor (verborgen, data naar motion)
```

---

### 4. `activity_events` - Alle activiteit events (append-only log)

```sql
CREATE TABLE activity_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id       UUID REFERENCES hue_config(id) ON DELETE CASCADE,
    device_id       UUID REFERENCES hue_devices(id) ON DELETE CASCADE,
    device_type     VARCHAR(50) NOT NULL,     -- light, motion_sensor, contact_sensor, button
    room_name       VARCHAR(255),
    is_on           BOOLEAN NOT NULL,         -- true = actief, false = inactief
    recorded_at     TIMESTAMPTZ NOT NULL,     -- Wanneer event plaatsvond
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_activity_events_config ON activity_events(config_id);
CREATE INDEX idx_activity_events_time ON activity_events(recorded_at DESC);
CREATE INDEX idx_activity_events_room ON activity_events(room_name);
```

**Device types en is_on betekenis:**
| Device Type | is_on = true | is_on = false |
|-------------|--------------|---------------|
| `light` | Lamp AAN | Lamp UIT |
| `motion_sensor` | Beweging gedetecteerd | - |
| `contact_sensor` | Deur OPEN | Deur DICHT |
| `button` | Knop ingedrukt | - |

**Retentie:** Events ouder dan 90 dagen worden automatisch verwijderd.

---

### 5. `room_activity` - 5-minuten aggregatie per kamer

```sql
CREATE TABLE room_activity (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id         UUID REFERENCES hue_config(id) ON DELETE CASCADE,
    room_name         VARCHAR(255) NOT NULL,
    activity_window   TIMESTAMPTZ NOT NULL,   -- 5-minuten window start
    trigger_types     TEXT[],                  -- ['light', 'motion_sensor', etc]
    trigger_count     INTEGER DEFAULT 1,
    first_trigger_at  TIMESTAMPTZ,
    last_trigger_at   TIMESTAMPTZ,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(config_id, room_name, activity_window)
);

CREATE INDEX idx_room_activity_config ON room_activity(config_id);
CREATE INDEX idx_room_activity_window ON room_activity(activity_window DESC);
CREATE INDEX idx_room_activity_room ON room_activity(room_name);
```

**Aggregatie logica:**
- Events worden gegroepeerd per 5-minuten window (bijv. 14:00, 14:05, 14:10)
- `trigger_types` bevat alle unieke device types in dat window
- `trigger_count` telt het aantal events in dat window
- Wordt realtime bijgewerkt door `hue-sync-state` Edge Function

**Wordt gebruikt voor:** Dashboard heatmap via `room_activity_hourly` view

---

### 6. `daily_activity_stats` - Dagelijkse statistieken per bewoner

```sql
CREATE TABLE daily_activity_stats (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id             UUID NOT NULL REFERENCES hue_config(id) ON DELETE CASCADE,
    date                  DATE NOT NULL,
    first_activity        TIME,                    -- Tijdstip eerste event
    last_activity         TIME,                    -- Tijdstip laatste event
    total_events          INTEGER DEFAULT 0,       -- Totaal aantal events
    events_per_hour       INTEGER[],               -- Array met counts per uur (24 elementen)
    active_hours          INTEGER DEFAULT 0,       -- Uren met ≥1 event
    rooms_active          INTEGER DEFAULT 0,       -- Unieke kamers met activiteit
    rooms_available       INTEGER DEFAULT 0,       -- Totaal kamers met sensoren
    longest_gap_minutes   INTEGER DEFAULT 0,       -- Langste gap tussen events
    night_events          INTEGER DEFAULT 0,       -- Events 23:00-06:00
    night_active_hours    INTEGER DEFAULT 0,       -- Actieve uren 23:00-06:00
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(config_id, date)
);

CREATE INDEX idx_daily_activity_stats_config ON daily_activity_stats(config_id);
CREATE INDEX idx_daily_activity_stats_date ON daily_activity_stats(date DESC);
```

**Kolom beschrijvingen:**
| Kolom | Beschrijving |
|-------|--------------|
| `first_activity` | Tijdstip (TIME) van eerste event die dag |
| `last_activity` | Tijdstip (TIME) van laatste event die dag |
| `events_per_hour` | Array[24] met event counts per uur (index 0 = 00:00-01:00) |
| `active_hours` | Aantal uren met minimaal 1 event |
| `rooms_active` | Aantal unieke kamers met activiteit |
| `rooms_available` | Totaal aantal kamers met sensoren voor deze bewoner |
| `longest_gap_minutes` | Langste periode zonder events tussen first en last activity |
| `night_events` | Events tussen 23:00-06:00 |
| `night_active_hours` | Uren met activiteit tussen 23:00-06:00 |

**Wordt bijgewerkt door:** `calculate_daily_activity_stats()` functie

---

## Views

### `room_activity_hourly` - Uurlijkse activiteit per kamer (RLS-enabled)

```sql
CREATE OR REPLACE VIEW room_activity_hourly AS
SELECT
    ra.config_id,
    ra.room_name,
    date_trunc('hour', ra.activity_window) AS hour,
    COUNT(*) AS event_count,                    -- Elke 5-min window = 1 event
    MAX(ra.last_trigger_at) AS last_event
FROM room_activity ra
JOIN hue_config hc ON ra.config_id = hc.id
WHERE hc.user_email = auth.jwt() ->> 'email'   -- RLS filter op user
GROUP BY ra.config_id, ra.room_name, date_trunc('hour', ra.activity_window)
ORDER BY hour DESC, ra.room_name;
```

**Let op:** Gebruikt `COUNT(*)` zodat elke 5-minuten window als 1 event telt (niet SUM van trigger_count).

### `room_activity_daily` - Dagelijkse samenvatting

```sql
SELECT
    room_name,
    date_trunc('day', hour) as day,
    SUM(event_count) as total_events,
    COUNT(DISTINCT hour) as active_hours
FROM room_activity_hourly
GROUP BY room_name, date_trunc('day', hour);
```

### `room_summary` - Huidige status per kamer

```sql
SELECT
    room_name,
    COUNT(*) FILTER (WHERE device_type = 'light') as light_count,
    COUNT(DISTINCT physical_device_id) FILTER (WHERE device_type = 'motion_sensor') as motion_sensor_count,
    COUNT(*) FILTER (WHERE device_type = 'contact_sensor') as door_sensor_count,
    COUNT(*) FILTER (WHERE device_type = 'light' AND (last_state->>'on')::boolean) as lights_on,
    MAX(last_state_at) as last_activity
FROM hue_devices
GROUP BY room_name;
```

### `recent_activity_by_room` - Laatste 24 uur activiteit

```sql
SELECT
    ae.room_name,
    ae.recorded_at,
    ae.device_type,
    ae.is_on as triggered,
    hd.name as sensor_name
FROM activity_events ae
JOIN hue_devices hd ON ae.device_id = hd.id
WHERE ae.recorded_at > NOW() - INTERVAL '24 hours'
ORDER BY ae.recorded_at DESC;
```

### `physical_devices_with_capabilities` - Fysieke devices met nested capabilities

```sql
SELECT
    p.*,
    jsonb_agg(jsonb_build_object(
        'id', d.id,
        'device_type', d.device_type,
        'hue_id', d.hue_id,
        'last_state', d.last_state,
        'last_state_at', d.last_state_at
    )) as capabilities,
    MAX(d.last_state_at) as last_activity
FROM physical_devices p
LEFT JOIN hue_devices d ON d.physical_device_id = p.id
GROUP BY p.id;
```

---

## Edge Functions

Supabase Edge Functions:

| Function | Trigger | Beschrijving |
|----------|---------|--------------|
| `hue-sync-state` | Cron (*/5 * * * *) | Detecteert lamp/sensor state changes, schrijft naar `activity_events` en `room_activity` |
| `hue-token-exchange` | HTTP | OAuth token exchange voor Hue koppeling |

### hue-sync-state Flow

```
1. Fetch alle active hue_configs
2. Per config:
   a. Refresh OAuth token indien nodig
   b. Fetch lights, groups, sensors (v1 API)
   c. Fetch contact sensors (v2 API)
   d. Vergelijk current_state met last_state per device
   e. Bij change → INSERT in activity_events
   f. Aggregeer naar room_activity per 5-min window
```

### room_activity Aggregatie

Events worden realtime geaggregeerd in `room_activity`:
- Elke 5-minuten window wordt een aparte row
- `trigger_types[]` bevat alle device types in dat window
- `trigger_count` telt het aantal events
- Dashboard view (`room_activity_hourly`) groepeert per uur en telt windows als events

---

## Database Functies

### `calculate_daily_activity_stats(config_id, date)`

Berekent dagelijkse statistieken voor één bewoner op één dag.

```sql
SELECT calculate_daily_activity_stats(
    'config-uuid'::uuid,
    '2026-01-31'::date
);
```

**Berekent:**
- Eerste en laatste activiteit van de dag
- Totaal events en events per uur (array[24])
- Actieve uren en actieve kamers
- Langste gap tussen events
- Nachtactiviteit (23:00-06:00)

### `refresh_daily_activity_stats(config_id, days_back)`

Batch functie voor meerdere dagen/configs.

```sql
-- Herbereken laatste 7 dagen voor alle configs
SELECT * FROM refresh_daily_activity_stats(NULL, 7);

-- Herbereken laatste 30 dagen voor specifieke config
SELECT * FROM refresh_daily_activity_stats('config-uuid', 30);
```

---

## Row Level Security (RLS)

RLS is ingeschakeld op alle tabellen voor multi-tenant isolatie.

### hue_config

```sql
-- Users zien alleen hun eigen config
CREATE POLICY "Users view own config" ON hue_config
    FOR SELECT TO authenticated
    USING (user_email = auth.jwt() ->> 'email');
```

### activity_events en room_activity

```sql
-- Users zien alleen events van hun eigen config
CREATE POLICY "Users view own events" ON activity_events
    FOR SELECT TO authenticated
    USING (config_id IN (
        SELECT id FROM hue_config
        WHERE user_email = auth.jwt() ->> 'email'
    ));

CREATE POLICY "Users view own room activity" ON room_activity
    FOR SELECT TO authenticated
    USING (config_id IN (
        SELECT id FROM hue_config
        WHERE user_email = auth.jwt() ->> 'email'
    ));

CREATE POLICY "Users view own daily stats" ON daily_activity_stats
    FOR SELECT TO authenticated
    USING (config_id IN (
        SELECT id FROM hue_config
        WHERE user_email = auth.jwt() ->> 'email'
    ));
```

### Views met RLS

De `room_activity_hourly` view heeft een ingebouwde RLS filter:
```sql
WHERE hc.user_email = auth.jwt() ->> 'email'
```

Dit zorgt ervoor dat meerdere gebruikers dezelfde Hue bridge kunnen gebruiken zonder elkaars data te zien.

**Rollen:**
- `authenticated` - Ingelogde gebruikers (SELECT, gefilterd op user_email)
- `service_role` - Backend/Edge Functions (full access)

---

## Data Flow

```
Hue Bridge (v1 + v2 API)
    │
    ▼
hue-sync-state (elke 5 min)
    │
    ├──► hue_devices.current_state (UPDATE - altijd)
    │
    ├──► hue_devices.last_state (UPDATE - alleen bij change)
    │
    ├──► activity_events (INSERT bij state change)
    │         │
    │         ▼
    └──► room_activity (UPSERT per 5-min window)
                  │
                  ▼
         room_activity_hourly (VIEW - groepeert per uur)
                  │
                  ▼
         Dashboard heatmap (7 dagen)
```

**Realtime aggregatie:** Events worden direct geaggregeerd naar `room_activity`
(geen aparte cron job nodig). De `room_activity_hourly` view groepeert on-the-fly.

---

## Dashboard Queries

### Heatmap data (7 dagen) - met RLS

```sql
SELECT room_name, hour, event_count, last_event
FROM room_activity_hourly
WHERE hour > NOW() - INTERVAL '7 days'
ORDER BY hour DESC, room_name;
```

> View filtert automatisch op ingelogde user via `auth.jwt() ->> 'email'`

### Sensor health check

```sql
SELECT
    p.name,
    p.room_name,
    p.battery_level,
    p.battery_level < 20 as low_battery,
    d.last_state_at,
    d.last_state_at < NOW() - INTERVAL '90 minutes' as stale
FROM physical_devices p
JOIN hue_devices d ON d.physical_device_id = p.id
WHERE d.device_type = 'motion_sensor';
```

### Laatste activiteit per kamer

```sql
SELECT DISTINCT ON (room_name)
    room_name,
    last_state_at,
    name as device_name,
    device_type
FROM hue_devices
WHERE last_state_at IS NOT NULL
ORDER BY room_name, last_state_at DESC;
```

### Recente events (24 uur)

```sql
SELECT
    ae.room_name,
    hd.name,
    ae.device_type,
    ae.is_on,
    ae.recorded_at
FROM activity_events ae
JOIN hue_devices hd ON ae.device_id = hd.id
WHERE ae.recorded_at > NOW() - INTERVAL '24 hours'
ORDER BY ae.recorded_at DESC
LIMIT 100;
```

---

## Households & Multi-tenancy

### Tabellen

**households**
| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | UUID | Primary key |
| name | TEXT | Huishouden naam |
| config_id | UUID | FK naar hue_config (gekoppelde Bridge) |
| created_at | TIMESTAMPTZ | Aangemaakt |

**household_members**
| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | UUID | Primary key |
| household_id | UUID | FK naar households |
| user_id | UUID | FK naar auth.users |
| role | TEXT | admin / viewer |
| invited_by | UUID | Uitgenodigd door |
| joined_at | TIMESTAMPTZ | Lid geworden |

**user_profiles**
| Kolom | Type | Beschrijving |
|-------|------|--------------|
| id | UUID | PK = auth.users.id |
| display_name | TEXT | Weergavenaam |
| active_household_id | UUID | Actief huishouden |
| created_at | TIMESTAMPTZ | Aangemaakt |

### Access Control: `get_accessible_config_ids()`

Centrale SQL functie die bepaalt welke hue_config IDs een user mag zien:

```sql
-- Stap 1: Check households via household_members
-- Stap 2: Fallback op directe hue_config.user_email match
-- Stap 3: Superadmin (dirk@boostix.nl) ziet alles
```

Alle RLS policies gebruiken: `config_id IN (SELECT get_accessible_config_ids())`

---

## Migratie Bestanden

SQL migraties in `gerustthuis-supabase/supabase/migrations/`:

1. `001_initial_schema.sql` - Basis tabellen (hue_config, hue_devices, activity_events, room_activity)
2. `002_cron_jobs.sql` - Cron jobs voor polling
3. `003_room_activity_aggregation.sql` - Room activity aggregatie functies
4. `004_room_activity_hourly_table.sql` - room_activity_hourly tabel + aggregate functie
5. `005_rls_policies.sql` - Row Level Security policies
6. `006_daily_activity_stats.sql` - daily_activity_stats tabel + berekeningsfuncties
7. `007_sensor_health.sql` - Sensor health monitoring
8. `008_physical_devices.sql` - Physical devices groepering
9. `009_user_profiles.sql` - User profiles tabel
10. `010_households.sql` - Households multi-tenancy
11. `011_households_v2.sql` - Households verbeteringen
12. `012_clean_rebuild_auth_households.sql` - Auth en households rebuild
13. `013_fix_signup_trigger.sql` - Fix signup trigger
14. `014_superadmin_user_profiles.sql` - Superadmin RLS op user_profiles
15. `015_link_config_to_household.sql` - Auto-link hue_config aan household
16. `016_fix_missing_tables.sql` - Herstel room_activity_hourly + RLS
17. `017_populate_aggregated_data.sql` - Vul aggregatie tabellen + fix RLS

---

## Indexen Samenvatting

| Tabel | Index | Kolommen |
|-------|-------|----------|
| hue_devices | idx_hue_devices_config | config_id |
| hue_devices | idx_hue_devices_type | device_type |
| hue_devices | idx_hue_devices_room | room_name |
| hue_devices | idx_hue_devices_physical | physical_device_id |
| activity_events | idx_activity_events_config | config_id |
| activity_events | idx_activity_events_time | recorded_at DESC |
| activity_events | idx_activity_events_room | room_name |
| room_activity | idx_room_activity_config | config_id |
| room_activity | idx_room_activity_window | activity_window DESC |
| room_activity | idx_room_activity_room | room_name |
| physical_devices | idx_physical_devices_config | config_id |
| physical_devices | idx_physical_devices_room | room_name |
| daily_activity_stats | idx_daily_activity_stats_config | config_id |
| daily_activity_stats | idx_daily_activity_stats_date | date DESC |
