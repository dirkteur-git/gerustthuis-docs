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
│   ├── App.vue                     # Root layout met bottom TabBar (mobile-first)
│   ├── main.js                     # App initialisatie
│   ├── router.js                   # Vue Router config
│   ├── style.css                   # Tailwind imports
│   ├── services/
│   │   ├── supabase.js             # Barrel re-export (backwards compat)
│   │   ├── client.js               # Supabase client + activityDb/integrationsDb
│   │   ├── state.js                # Gedeelde userState reactive
│   │   ├── auth.js                 # signIn, signOut, getCurrentUser, ...
│   │   ├── household.js            # loadUserProfile, leden, uitnodigingen, ...
│   │   ├── devices.js              # getHueConfig, sensoren, kamers, ...
│   │   ├── residents.js            # getResident
│   │   ├── messages.js             # family board + notificaties
│   │   └── activity.js             # getRecentEvents
│   ├── composables/
│   │   ├── useDataQuality.js       # Statistische berekeningen (z-scores, dagstart, ...)
│   │   └── useDashboardData.js     # Data loading voor Dashboard (5 queries + refresh)
│   ├── components/
│   │   ├── Logo.vue                # Gedeeld logo component
│   │   ├── TabBar.vue              # Bottom tab navigatie (4 tabs)
│   │   ├── ActivityHeatmap.vue     # 7-dagen heatmap met hover tooltip
│   │   ├── PatronenDagritme.vue    # Dagritme card + uurchart
│   │   ├── PatronenVandaag.vue     # Vandaag vs normaal vergelijking
│   │   └── PatronenTrends.vue      # 5 sparkline trend charts
│   └── views/
│       ├── Dashboard.vue           # Status banner + KPIs + heatmap (tab: Overzicht)
│       ├── Familie.vue             # Bewoner, familieleden, familiegroep (tab: Familie)
│       ├── Meldingen.vue           # Notifications per huishouden (tab: Meldingen)
│       ├── Instellingen.vue        # Integraties beheer (tab: Instellingen)
│       ├── Login.vue               # Login/registratie
│       ├── Woning.vue              # Kamers en devices (sub-pagina via Instellingen)
│       ├── Patronen.vue            # Patroonherkenning (sub-pagina via Overzicht)
│       ├── Trends.vue              # Website analytics (verborgen admin route)
│       ├── HueConnect.vue          # Hue OAuth start
│       ├── HueCallback.vue         # Hue OAuth callback
│       └── AcceptInvitation.vue    # Uitnodiging accepteren
├── public/
├── index.html
├── vite.config.js                  # Incl. vite-plugin-pwa configuratie
└── package.json
```

---

## Views en Database Gebruik

### Dashboard.vue - Heatmap Overzicht

**Doel:** 7-dagen activiteit heatmap, status banner, recente activiteit, offline sensoren

**Auto-refresh:** Elke 5 minuten wordt alle data herladen via `setInterval`.

**Tabellen/Views gebruikt:**

| Tabel | Query | Doel |
|-------|-------|------|
| `daily_activity_stats` | `SELECT * WHERE date = today` | Vandaag statistieken |
| `daily_activity_stats` | `SELECT total_events, first_activity, last_activity, events_per_hour WHERE date >= 14 dagen geleden` | Baseline gemiddelden |
| `room_activity_hourly` | `SELECT room_name, hour, total_events WHERE hour >= 7 dagen geleden` | Heatmap data |
| `activity_events` | `SELECT room_name, device_type, recorded_at ORDER BY recorded_at DESC LIMIT 50` | Recente activiteit |
| `hue_devices` | `SELECT name, room_name, last_state_at WHERE device_type IN (motion_sensor, contact_sensor) AND last_state_at < 90 min geleden` | Offline sensoren |

**Data flow:**

```
onMounted()
    │
    ├── loadTodayStats()
    │     └── daily_activity_stats (vandaag) + activity_events fallback
    │
    ├── loadAverageStats()
    │     └── daily_activity_stats (14 dagen, baseline)
    │
    ├── loadHeatmapData()
    │     └── room_activity_hourly (7 dagen)
    │
    ├── loadRecentActivity()
    │     └── activity_events (laatste 50)
    │
    └── loadOfflineSensors()
          └── hue_devices (last_state_at > 90 min)

    + setInterval(refreshAllData, 5 * 60 * 1000)
```

**Status banner logica:**
```javascript
// Z-score based status (rolling comparison tot huidig uur)
// Berekent z-scores voor: totalEvents, activeHours, longestGap, nightEvents, dagstart
const maxZ = Math.max(...Object.values(zScores).map(Math.abs))

// maxZ >= 2.0                        → "Sterk afwijkend" (rood)
// maxZ >= 1.0                        → "Let even op" (amber)
// 0 events + verwacht > 10           → "Erg rustig"
// < 7 dagen data                     → "We leren nog"
// anders                             → "Normale dag" (groen)
```

**Rolling vergelijking:** De status banner vergelijkt alleen activiteit tot het huidige uur met de baseline voor datzelfde uurvenster. Dit voorkomt valse alarmen vroeg op de dag.

**Heatmap aggregatie:**
```javascript
// Voor elke dag (7 dagen):
//   Voor elk uur (0-23):
//     count = total_events (per kamer opgeteld)
//     rooms = { "Woonkamer": 5, "Hal": 3, ... }
```

---

### Instellingen.vue - Integraties Beheer

**Doel:** Hue koppeling status en beheer

**Tabellen gebruikt:**

| Tabel | Query | Doel |
|-------|-------|------|
| `hue_config` | Via householdConfigId of eerste accessible config | Hue koppeling status |

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

## Services Architectuur

Alle database interactie gaat via domein-specifieke service bestanden. `supabase.js` is een barrel re-export — bestaande imports werken ongewijzigd.

### Domein-indeling

| Bestand | Inhoud |
|---------|--------|
| `services/client.js` | Supabase client, `activityDb()`, `integrationsDb()` |
| `services/state.js` | Gedeelde `userState` reactive (profiel, huishoudens, rol) |
| `services/auth.js` | `signIn`, `signOut`, `getCurrentUser`, `onAuthStateChange` |
| `services/household.js` | `loadUserProfile`, `switchHousehold`, `getHouseholdMembers`, uitnodigingen |
| `services/devices.js` | `getHueConfig`, `saveHueConfig`, sensoren, kamers |
| `services/residents.js` | `getResident` |
| `services/messages.js` | `getFamilyBoardMessages`, `postFamilyBoardMessage`, notificaties |
| `services/activity.js` | `getRecentEvents` |
| `services/supabase.js` | Barrel re-export van alles bovenstaande |

### Auth

```javascript
export async function getCurrentUser()   // supabase.auth.getUser()
export async function signIn(email, password)
export async function signOut()          // + reset userState
export function onAuthStateChange(callback)
```

### Hue Config & Devices

```javascript
export async function getHueConfig()     // via householdConfigId of eerste accessible
export async function saveHueConfig(config)  // UPSERT ON CONFLICT (user_email)
export async function getDevices(type?)
export async function getAllSensors()    // physical_devices + standalone
export async function getRooms()
export async function getDevicesByRoom(roomName)
```

### Events & Berichten

```javascript
export async function getRecentEvents(limit = 50)
export async function getFamilyBoardMessages(limit = 30)
export async function postFamilyBoardMessage(message)
export async function getNotifications(limit = 50)
export async function markNotificationRead(id)
export async function markAllNotificationsRead()
```

---

## Database Queries Samenvatting

### Per View

| View | Tabellen | Queries |
|------|----------|---------|
| Dashboard | daily_activity_stats, room_activity_hourly, activity_events, hue_devices | 5 |
| Patronen | daily_activity_stats | 1 |
| Familie | residents, family_board_messages, household_members, user_profiles | 4 |
| Meldingen | notifications | 2 |
| Instellingen | hue_config, households, household_members, household_invitations | 4 |
| HueConnect | - | 0 |
| HueCallback | - (via Edge Function) | 0 |
| Login | - (Supabase Auth) | 0 |

> **Analyse** is verplaatst naar `gerustthuis-admin_portal` — geen onderdeel van portaal.

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

**Gedeelde user state** via `services/state.js`:

```javascript
export const userState = reactive({
  profile: null,           // user_profiles record
  households: [],          // alle huishoudens van de user
  currentHousehold: null,  // actief huishouden (met config_id)
  currentRole: null,       // 'admin' | 'viewer'
  loaded: false,
})
```

**Dashboard data** via `composables/useDashboardData.js`:

```javascript
const { heatmapData, recentActivity, todayStats, averageStats,
        historicalDays, offlineSensors, refreshAllData } = useDashboardData()

// Dashboard roept aan in onMounted + setInterval(5 min):
await refreshAllData()
```

**View-lokale state** — elke view beheert eigen `loading`, `hasConfig`, en UI-state via Vue `ref()`.

---

## Geïmplementeerde Views

### Tab Views (TabBar navigatie)

| View | Tab | Functie |
|------|-----|---------|
| `Dashboard.vue` | Overzicht | 7-dagen heatmap, status banner, recente activiteit, offline sensoren, auto-refresh (5 min) |
| `Familie.vue` | Familie | Bewoner banner, familieleden lijst, familiegroep berichten (realtime) |
| `Meldingen.vue` | Meldingen | Notificaties gegroepeerd per datum, mark-as-read, realtime updates |
| `Instellingen.vue` | Instellingen | Hue koppeling, huishouden beheer, gebruikers |

### Sub-pagina's (geen tab, bereikbaar via links in tab-views)

| View | Bereikbaar via | Functie |
|------|----------------|---------|
| `Patronen.vue` | Overzicht → "Bekijk volledige tijdlijn" | Dagritme analyse, vandaag vs normaal, weekpatroon, trends |
| `Woning.vue` | Instellingen → "Sensoren & Kamers" | Kamers overzicht, devices per kamer |
| `Trends.vue` | Verborgen route `/trends` | Website analytics via GA4 |

### Overig

| View | Functie |
|------|---------|
| `AcceptInvitation.vue` | Uitnodiging voor huishouden accepteren |
| `HueConnect.vue` | Hue OAuth start |
| `HueCallback.vue` | Hue OAuth callback |

> **Let op:** `Analyse.vue` is verplaatst naar `gerustthuis-admin_portal` — dit is een developer/admin tool en hoort niet bij de mantelzorger-interface.

## Household Multi-tenancy

Het portaal ondersteunt meerdere huishoudens per gebruiker via `supabase.js`:

### State Management

```javascript
// Reactive user state
const userState = reactive({
  profile: null,          // user_profiles record
  households: [],         // Alle huishoudens van de user
  currentHousehold: null, // Actief huishouden
  currentRole: null       // admin / viewer
})
```

### Functies

| Functie | Beschrijving |
|---------|--------------|
| `loadUserProfile()` | Laadt profiel + huishoudens bij login |
| `switchHousehold(id)` | Wisselt actief huishouden |
| `inviteToHousehold(email, role)` | Stuurt uitnodiging |
| `acceptInvitation(token)` | Accepteert uitnodiging |

### Hue Config Selectie

De Hue configuratie wordt opgehaald via:
1. `householdConfigId` van het actieve huishouden
2. Fallback: eerste config uit `get_accessible_config_ids()`

## Bekende Beperkingen

- Patronen heeft geen auto-refresh (alleen Dashboard heeft dit via setInterval 5 min)
- Familie en Meldingen hebben realtime via Supabase channel; Dashboard is polling-based
- Geen handmatige refresh knop op Patronen

---

## Environment Variables

```bash
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxx
VITE_HUE_CLIENT_ID=xxx
```

---

## Routes

| Route | View | Auth Required | Zichtbaar in |
|-------|------|---------------|-------------|
| `/login` | Login.vue | Nee | - |
| `/` | Dashboard.vue | Ja | Tab: Overzicht |
| `/familie` | Familie.vue | Ja | Tab: Familie |
| `/meldingen` | Meldingen.vue | Ja | Tab: Meldingen |
| `/instellingen` | Instellingen.vue | Ja | Tab: Instellingen |
| `/patronen` | Patronen.vue | Ja | Link in Overzicht |
| `/woning` | Woning.vue | Ja | Link in Instellingen |
| `/trends` | Trends.vue | Ja | Verborgen (admin) |
| `/hue` | HueConnect.vue | Ja | Doorgestuurd vanuit Instellingen |
| `/hue/callback` | HueCallback.vue | Ja | OAuth callback |
| `/uitnodiging/:token` | AcceptInvitation.vue | Nee | E-maillink |

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
