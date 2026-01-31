# GerustThuis Architectuur

## Overzicht

GerustThuis is een thuismonitoring systeem voor ouderen. Het systeem verzamelt sensordata en detecteert activiteitspatronen.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Home Assistant │────▶│  Raspberry Pi   │────▶│    Supabase     │
│    (sensoren)   │     │ (gerustthuis-   │     │    (cloud)      │
│                 │     │     device)     │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │    InfluxDB     │
                        │    (lokaal)     │
                        └─────────────────┘
```

## Componenten

### 1. gerustthuis-device (Raspberry Pi)

Python applicatie die draait op een Raspberry Pi.

**Bestanden:**
- `main.py` - Entry point
- `src/ha_client.py` - Home Assistant WebSocket verbinding
- `src/cloud_sync.py` - Supabase synchronisatie
- `src/influx_client.py` - Lokale InfluxDB opslag
- `src/activity_detector.py` - Inactiviteitsdetectie

**Flow:**
1. Verbindt met Home Assistant via WebSocket
2. Ontvangt state_changed events voor geconfigureerde sensoren
3. Schrijft naar InfluxDB (lokaal, real-time)
4. Queued events voor Supabase (cloud, elke 5 min)

### 2. gerustthuis-cloud (Frontend + Supabase)

Vue.js frontend met Supabase backend.

**Supabase functies:**
- `supabase/functions/hue-token-exchange/` - Hue OAuth flow
- `supabase/functions/hue-link-bridge/` - Bridge koppeling

### 3. hue-simple (Hue Package)

Standalone Philips Hue integratie.

**Bestanden:**
- `packages/hue/client.js` - HueClient class
- `packages/hue/auth.js` - HueAuth class (OAuth)
- `server.js` - Proxy server voor lokale Hue API

---

## Database Schema (v2)

### Tabellen

```
┌─────────────────────┐
│  integration_types  │  (reference)
├─────────────────────┤
│ code (PK)           │  hue, home_assistant, homey
│ name                │
│ description         │
└─────────────────────┘

┌─────────────────────┐
│    item_types       │  (reference)
├─────────────────────┤
│ code (PK)           │  motion_sensor, contact_sensor, light, etc.
│ name                │
│ category            │  sensor, actuator, bridge
└─────────────────────┘

┌─────────────────────┐
│   integrations      │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │  → auth.users
│ type                │  → integration_types.code
│ name                │
│ config (JSONB)      │  tokens, bridge_ip, etc.
│ status              │  active, migrated, error
│ last_sync_at        │
└─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐
│      items          │
├─────────────────────┤
│ id (PK)             │
│ integration_id (FK) │  → integrations.id
│ external_id         │  sensor.badkamer_temp / abc-def-123
│ type                │  → item_types.code
│ name                │
│ location            │
│ config (JSONB)      │
│ state (JSONB)       │  huidige status
└─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐
│   measurements      │
├─────────────────────┤
│ id (PK)             │
│ item_id (FK)        │  → items.id
│ value (JSONB)       │  {"motion": true, "temperature": 21.5}
│ recorded_at         │
│ source              │  sync, webhook, manual
└─────────────────────┘
```

### Data Model

Een fysieke sensor kan meerdere metingen hebben in één JSONB value:

```json
// Hue Motion Sensor (SML003)
{
  "motion": true,
  "temperature": 21.5,
  "lux": 150,
  "battery": 85
}

// Contact Sensor
{
  "contact": true
}
```

### Integraties

Dezelfde fysieke sensor kan via meerdere integraties binnenkomen:

| Integration | external_id | Beschrijving |
|-------------|-------------|--------------|
| home_assistant | `binary_sensor.badkamer_beweging` | Via Home Assistant |
| hue | `c2e812a7-4b0e-4bb4-b5a7-1e70684c6bc9` | Direct via Hue API |

Beide zijn valide en worden apart opgeslagen. De `integration_id` zorgt voor scheiding.

---

## Hue Integratie

### Authenticatie Flow

1. **OAuth2** via Philips Hue Remote API
2. **Link button** activeren op bridge
3. **Username** aanmaken voor lokale API toegang

```javascript
// packages/hue/auth.js
const auth = new HueAuth({ clientId, clientSecret, redirectUri });
const authUrl = auth.getAuthorizeUrl();
// User authorizes...
const tokens = await auth.exchangeCode(code);
const username = await auth.createUsername(tokens.access_token);
```

### Lokale API v2 (CLIP)

```javascript
// packages/hue/client.js
const hue = new HueClient({ bridgeIp: '192.168.86.23', username: '...' });

// Devices ophalen
const devices = await hue.getDevices();
const motion = await hue.getMotionSensors();
const lights = await hue.getLights();

// Lamp bedienen
await hue.setLightOn(lightId, true);
await hue.setLightBrightness(lightId, 80);

// Device identificeren (knippert)
await hue.identifyDevice(deviceId);
```

### Device Types

| Hue Resource | Item Type | Opmerkingen |
|--------------|-----------|-------------|
| motion | motion_sensor | Onderdeel van SML001/SML003 |
| temperature | (gecombineerd) | Onderdeel van motion sensor device |
| light_level | (gecombineerd) | Onderdeel van motion sensor device |
| contact | contact_sensor | SOC001 |
| light | light | Lampen |
| button | button | Dimmers, schakelaars |
| device | - | Parent device met services |

---

## Raspberry Pi Setup

### Vereisten

- Python 3.9+
- Home Assistant met Long-Lived Access Token
- InfluxDB 2.x (lokaal)
- Supabase project

### Configuratie

```yaml
# config.yaml
home_assistant:
  url: http://homeassistant.local:8123
  token: YOUR_LONG_LIVED_TOKEN

supabase:
  url: https://your-project.supabase.co
  key: YOUR_SUPABASE_ANON_KEY
  user_id: YOUR_USER_ID
  sync_interval: 300  # 5 minuten

influxdb:
  url: http://localhost:8086
  token: YOUR_INFLUX_TOKEN
  org: gerustthuis
  bucket: sensors

sensors:
  - entity_id: binary_sensor.badkamer_beweging
    type: motion
    room: Badkamer
  - entity_id: binary_sensor.voordeur_contact
    type: door
    room: Hal
  - entity_id: sensor.woonkamer_temperature
    type: temperature
    room: Woonkamer
```

### Starten

```bash
cd gerustthuis-device
pip install -r requirements.txt
python main.py
```

---

## Supabase Configuratie

### Environment Variables

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
```

### Row Level Security

- Users zien alleen eigen data (`auth.uid() = user_id`)
- Legacy data (user_id = NULL) is public voor development

### Migraties

Migratie scripts staan in `gerustthuis-cloud/supabase/migrations/`.

---

## Huidige Status

### Sensoren in Database

| Type | Aantal | Bron |
|------|--------|------|
| motion_sensor | 12 | Home Assistant |
| contact_sensor | 3 | Home Assistant |

### Te Doen

- [ ] Raspberry Pi code updaten voor v2 schema
- [ ] Hue devices toevoegen aan database
- [ ] Dashboard bouwen met realtime updates
