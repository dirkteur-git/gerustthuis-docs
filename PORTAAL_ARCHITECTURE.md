# GerustThuis Portaal Architectuur

Frontend applicatie documentatie voor het login portaal.

---

## Getting Started

### Prerequisites

- Node.js 18+
- npm of pnpm
- Supabase project met schema (zie DATABASE_DESIGN.md)
- Philips Hue Developer account (voor OAuth)

### Installatie

```bash
cd gerustthuis-portaal
npm install
```

### Environment Variables

Maak `.env.local` aan:

```bash
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
VITE_HUE_CLIENT_ID=your_hue_client_id
```

### Development

```bash
npm run dev
# Open http://localhost:5173
```

### Build

```bash
npm run build
npm run preview  # Test production build
```

---

## Tech Stack

| Component | Technologie |
|-----------|-------------|
| Framework | Vue 3 (Composition API) |
| Build Tool | Vite |
| Styling | Tailwind CSS |
| Database | Supabase |
| Auth | Supabase Auth |

---

## Project Structuur

```
gerustthuis-portaal/
├── src/
│   ├── App.vue                 # Root layout met sidebar
│   ├── main.js                 # App initialisatie
│   ├── router.js               # Vue Router config
│   ├── style.css               # Tailwind imports
│   ├── services/
│   │   └── supabase.js         # Database client + helpers
│   ├── composables/
│   │   └── useDataQuality.js   # Gedeelde berekeningen
│   └── views/
│       ├── Dashboard.vue       # Heatmap overzicht
│       ├── Login.vue           # Login/registratie
│       ├── Woning.vue          # Kamers en devices
│       ├── Patronen.vue        # Patroonherkenning (dagritme, trends)
│       ├── Analyse.vue         # Anomaly detection (Z-scores)
│       ├── Instellingen.vue    # Integraties beheer
│       ├── HueConnect.vue      # Hue OAuth start
│       ├── HueCallback.vue     # Hue OAuth callback
│       └── AcceptInvitation.vue # Uitnodiging accepteren
├── public/
├── index.html
├── vite.config.js
└── package.json
```

---

## Views en Database Gebruik

### Dashboard.vue - Heatmap Overzicht

**Doel:** 7-dagen activiteit heatmap met kamer filter

**Tabellen/Views gebruikt:**

| Tabel | Query | Doel |
|-------|-------|------|
| `hue_devices` | `SELECT room_name WHERE room_name IS NOT NULL` | Unieke kamers voor filter |
| `physical_devices` | `SELECT id, battery_updated_at` | Motion sensor health check |
| `hue_devices` | `SELECT id, last_state_at WHERE device_type = 'contact_sensor'` | Deur sensor health check |
| `room_activity_hourly` | `SELECT room_name, hour, motion_events, door_events, updated_at WHERE hour >= 7 dagen geleden` | Heatmap data |

**Data flow:**

```
onMounted()
    │
    ├── loadRooms()
    │     └── hue_devices.room_name (distinct)
    │
    ├── loadSensorHealth()
    │     ├── physical_devices (motion sensors)
    │     └── hue_devices WHERE device_type = 'contact_sensor'
    │
    └── loadHeatmapData()
          └── room_activity_hourly (7 dagen)
```

**Sensor health berekening:**
```javascript
// Sensor is "actief" als laatste update < 90 minuten geleden
const ninetyMinutesAgo = new Date(Date.now() - 90 * 60 * 1000)

// Motion sensors - check last_state_at van hue_devices
activeMotion = motionSensors.filter(d =>
  d.last_state_at > ninetyMinutesAgo
).length

// Contact sensors (standalone)
activeContact = contactSensors.filter(d =>
  d.last_state_at > ninetyMinutesAgo
).length

sensorscore = ((activeMotion + activeContact) / total) * 100
```

> **Let op:** We checken `last_state_at` van `hue_devices` (niet `battery_updated_at` van `physical_devices`), omdat `last_state_at` elke 5 minuten wordt geüpdatet bij state changes, terwijl `battery_updated_at` alleen elk uur wordt geüpdatet.

**Heatmap aggregatie:**
```javascript
// Voor elke dag (7 dagen):
//   Voor elk uur (0-23):
//     count = motion_events + door_events
//     roomCounts = { "Woonkamer": 5, "Hal": 3, ... }
```

---

### Instellingen.vue - Integraties Beheer

**Doel:** Hue koppeling status en beheer

**Tabellen gebruikt:**

| Tabel | Query | Doel |
|-------|-------|------|
| `hue_config` | `SELECT * WHERE user_email = current_user.email` | Hue koppeling status |

**Getoonde velden:**
- `status` - active/error/expired
- `last_sync_at` - Laatste poll timestamp
- `last_error` - Foutmelding indien error

---

### HueConnect.vue - OAuth Start

**Doel:** Redirect naar Philips Hue login

**Geen database queries** - alleen OAuth URL generatie

**Flow:**
1. Genereer random `state` (CSRF protection)
2. Sla state op in localStorage
3. Redirect naar `https://api.meethue.com/v2/oauth2/authorize`

---

### HueCallback.vue - OAuth Callback

**Doel:** Verwerk OAuth callback en roep Edge Function aan

**Edge Function:** `hue-token-exchange`

**Payload naar Edge Function:**
```javascript
{
  code: "authorization_code_from_url",
  user_email: "user@example.com",
  user_id: "supabase_user_id"
}
```

**Response:**
```javascript
{
  success: true,
  config_id: "uuid",
  bridge_username: "whitelist_id"
}
```

---

### Login.vue - Authenticatie

**Doel:** Login en registratie

**Supabase Auth functies:**
- `supabase.auth.signInWithPassword({ email, password })`
- `supabase.auth.signUp({ email, password })`

**Geen custom tabellen** - alleen Supabase Auth

---

## Supabase Service (supabase.js)

Alle database interactie gaat via deze service.

### Auth Functies

```javascript
// Huidige gebruiker ophalen
export async function getCurrentUser() {
  const { data: { user } } = await supabase.auth.getUser()
  return user
}

// Inloggen
export async function signIn(email, password)

// Uitloggen
export async function signOut()

// Auth state listener
export function onAuthStateChange(callback)
```

### Hue Config Functies

```javascript
// Hue koppeling voor huidige gebruiker
export async function getHueConfig()
// Query: SELECT * FROM hue_config WHERE user_email = current_user.email

// Opslaan/updaten
export async function saveHueConfig(config)
// Query: UPSERT INTO hue_config ON CONFLICT (user_email)
```

### Device Functies

```javascript
// Alle devices (optioneel gefilterd op type)
export async function getDevices(type = null)
// Query: SELECT * FROM hue_devices [WHERE device_type = type]

// Alleen lampen
export async function getLights()
// Query: SELECT * FROM hue_devices WHERE device_type = 'light'

// Alleen sensoren (niet-lampen)
export async function getSensors()
// Query: SELECT * FROM hue_devices WHERE device_type != 'light'

// Physical devices met capabilities (geneste query)
export async function getPhysicalDevices()
// Query: SELECT *, capabilities:hue_devices(...) FROM physical_devices

// Alle sensoren: physical devices + standalone
export async function getAllSensors()
// Combineert physical_devices en hue_devices zonder physical_device_id

// Unieke kamers
export async function getRooms()
// Query: SELECT DISTINCT room_name FROM hue_devices

// Devices per kamer
export async function getDevicesByRoom(roomName)
// Query: physical_devices + hue_devices WHERE room_name = roomName
```

### Event Functies

```javascript
// Recente events met device info
export async function getRecentEvents(limit = 50)
// Query: SELECT *, hue_devices(name, device_type, room_name)
//        FROM activity_events ORDER BY recorded_at DESC LIMIT 50
```

---

## Database Queries Samenvatting

### Per View

| View | Tabellen | Queries |
|------|----------|---------|
| Dashboard | hue_devices, physical_devices, room_activity_hourly | 3 |
| Instellingen | hue_config | 1 |
| HueConnect | - | 0 |
| HueCallback | - (via Edge Function) | 0 |
| Login | - (Supabase Auth) | 0 |

### Per Tabel (Read)

| Tabel | Gebruikt door |
|-------|---------------|
| `hue_config` | Instellingen, HueCallback |
| `hue_devices` | Dashboard (rooms, contact sensors) |
| `physical_devices` | Dashboard (motion sensor health) |
| `room_activity_hourly` | Dashboard (heatmap) |
| `activity_events` | (beschikbaar via getRecentEvents, nog niet in UI) |

---

## Belangrijke Queries

### Heatmap Data Query

```javascript
const { data } = await supabase
  .from('room_activity_hourly')
  .select('room_name, hour, motion_events, door_events, updated_at')
  .gte('hour', sevenDaysAgo.toISOString())
```

**Retourneert:**
```javascript
[
  { room_name: "Woonkamer", hour: "2024-01-15T14:00:00Z", motion_events: 5, door_events: 2 },
  { room_name: "Hal", hour: "2024-01-15T14:00:00Z", motion_events: 3, door_events: 0 },
  // ...
]
```

### Sensor Health Query

```javascript
// Motion sensors (physical devices)
const { data: physicalDevices } = await supabase
  .from('physical_devices')
  .select('id, battery_updated_at')

// Contact sensors (standalone)
const { data: contactSensors } = await supabase
  .from('hue_devices')
  .select('id, last_state_at')
  .eq('device_type', 'contact_sensor')
```

### Room List Query

```javascript
const { data } = await supabase
  .from('hue_devices')
  .select('room_name')
  .not('room_name', 'is', null)

// Deduplicate in JavaScript:
const rooms = [...new Set(data.map(d => d.room_name))].sort()
```

---

## State Management

**Geen centralized state** - elke view beheert eigen state via Vue refs:

```javascript
// Dashboard.vue
const loading = ref(true)
const rooms = ref([])
const selectedRooms = ref([])
const heatmapData = ref([])
const sensorHealth = ref({ active: 0, total: 0 })
const lastRefreshTime = ref(null)
```

**Data wordt één keer geladen bij mount:**
```javascript
onMounted(async () => {
  await Promise.all([
    loadRooms(),
    loadSensorHealth(),
    loadHeatmapData()
  ])
  loading.value = false
})
```

---

## Bekende Beperkingen

### 1. Geen Auto-Refresh

Data wordt **alleen bij mount** geladen. Geen:
- Polling interval
- Real-time subscriptions
- Handmatige refresh knop

**Oplossing:** Implementeer polling + refresh knop. Zie [ROADMAP.md](ROADMAP.md).

```javascript
// Toe te voegen aan Dashboard.vue
let refreshInterval = null

onMounted(async () => {
  await refreshAllData()
  refreshInterval = setInterval(refreshAllData, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
```

### Geïmplementeerde Views

Alle views zijn geïmplementeerd:

| View | Functie |
|------|---------|
| `Dashboard.vue` | 7-dagen heatmap, dagstatistieken, recente activiteit, offline sensoren |
| `Patronen.vue` | Dagritme analyse, vandaag vs normaal, weekpatroon, trends |
| `Analyse.vue` | Z-score anomaly detection, score breakdown, events per uur |
| `Woning.vue` | Kamers overzicht, devices per kamer, activiteit per kamer |
| `Instellingen.vue` | Hue koppeling, huishouden beheer, gebruikers (superadmin) |
| `AcceptInvitation.vue` | Uitnodiging voor huishouden accepteren |

### Multi-tenant (geïmplementeerd)

Household-based multi-tenancy via `get_accessible_config_ids()`. Elke user ziet alleen data van eigen huishouden. Superadmin (dirk@boostix.nl) kan alle huishoudens bekijken.

---

## Environment Variables

```bash
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxx
VITE_HUE_CLIENT_ID=xxx
```

---

## Routes

| Route | View | Auth Required |
|-------|------|---------------|
| `/login` | Login.vue | Nee |
| `/` | Dashboard.vue | Ja |
| `/patronen` | Patronen.vue | Ja |
| `/analyse` | Analyse.vue | Ja |
| `/woning` | Woning.vue | Ja |
| `/instellingen` | Instellingen.vue | Ja |
| `/hue` | HueConnect.vue | Ja |
| `/hue/callback` | HueCallback.vue | Ja |
| `/uitnodiging/:token` | AcceptInvitation.vue | Nee |

**Route guard in router.js:**
```javascript
router.beforeEach(async (to, from, next) => {
  const { data: { session } } = await supabase.auth.getSession()

  if (to.path === '/login' && session) {
    next('/')  // Al ingelogd → dashboard
  } else if (to.path !== '/login' && !session) {
    next('/login')  // Niet ingelogd → login
  } else {
    next()
  }
})
```
