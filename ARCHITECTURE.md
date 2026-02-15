# GerustThuis Architectuur

## Overzicht

GerustThuis is een thuismonitoring systeem voor ouderen. Het systeem verzamelt sensordata via Philips Hue en detecteert activiteitspatronen.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Philips Hue    │────▶│   Supabase      │────▶│  Vue 3 Portaal  │
│    Bridge       │     │  Edge Functions  │     │   (Frontend)    │
│  (sensoren +    │     │  (elke 5 min)   │     │                 │
│   lampen)       │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   PostgreSQL    │
                        │   (Supabase)    │
                        └─────────────────┘
```

## Componenten

### 1. Philips Hue Bridge (Sensordata)

De Hue Bridge is de enige databron. Sensoren en lampen zijn via ZigBee verbonden met de Bridge.

**Sensor types:**
- Motion sensoren (bewegingsdetectie)
- Contact sensoren (deur open/dicht)
- Lampen (aan/uit als activiteitssignaal)
- Knoppen (schakelaars, dimmers)

Zie [HUE_INTEGRATION.md](HUE_INTEGRATION.md) voor API details.

### 2. Supabase Edge Functions (Backend)

TypeScript Edge Functions die elke 5 minuten draaien:

| Function | Schedule | Beschrijving |
|----------|----------|--------------|
| `hue-sync-state` | `*/5 * * * *` | Synchroniseer alle device states, detecteer changes, schrijf naar activity_events en room_activity |
| `hue-token-exchange` | On-demand | OAuth token exchange bij Hue koppeling |

**Locatie:** `gerustthuis-supabase/functions/`

**Gedeelde code:** `gerustthuis-supabase/functions/_shared/`
- `cors.ts` - CORS headers
- `hue-client.ts` - Hue API client, token refresh, state vergelijking

### 3. Supabase PostgreSQL (Database)

Alle data wordt opgeslagen in Supabase PostgreSQL met Row Level Security.

**Kerntabellen:**
- `hue_config` - OAuth tokens per gebruiker
- `hue_devices` - Alle devices met huidige state
- `physical_devices` - Gegroepeerde fysieke sensoren
- `activity_events` - Ruwe sensor events (append-only)
- `room_activity` - 5-minuten aggregaties per kamer
- `room_activity_hourly` - Uurlijkse aggregatie per kamer (TABLE met RLS)
- `daily_activity_stats` - Dagelijkse statistieken
- `households` - Multi-tenant huishoudens
- `household_members` - Gebruikersrollen per huishouden (admin/viewer/installer)
- `user_profiles` - Gebruikersprofielen
- `residents` - Bewonersprofielen (naam, relatie, foto)

Zie [DATABASE_DESIGN.md](DATABASE_DESIGN.md) voor volledig schema.

**Personages:**

| Personage | Beschrijving | Account |
|-----------|--------------|---------|
| Bewoner | De oudere die gemonitord wordt | Geen login, profiel in `residents` |
| Mantelzorger | De persoon die meekijkt | Account, rol `admin` of `viewer` |
| Installateur | De persoon die sensoren plaatst | Account, rol `installer` (beperkte toegang) |

Zie [USER_STORIES.md](USER_STORIES.md) voor user stories per personage.

### 4. Vue 3 Portaal (Frontend)

Dashboard applicatie voor mantelzorgers.

**Tech stack:** Vue 3, Vite, Tailwind CSS v3, Supabase JS client

**Views:**
- Dashboard - 7-dagen heatmap, status banner, recente activiteit
- Patronen - Dagritme, vandaag vs normaal, weekpatroon, trends
- Analyse - Developer view met z-score anomaly detection
- Woning - Kamers en devices overzicht
- Instellingen - Hue koppeling, huishouden beheer
- HueConnect - Hue Bridge koppeling starten
- HueCallback - OAuth callback na Hue autorisatie
- AcceptInvitation - Uitnodiging accepteren voor huishouden
- Login - Inlogpagina

Zie [PORTAAL_ARCHITECTURE.md](PORTAAL_ARCHITECTURE.md) voor frontend details.

### 5. Marketing Website

Vue 3 marketing website op apart domein.

**Tech stack:** Vue 3, Vite, Tailwind CSS v4, Pinia

**Locatie:** `gerustthuis-website/`

### 6. Admin Portaal

Vue 3 admin portaal met projectplan, beheer en rapportages.

**Tech stack:** Vue 3, Vite, Tailwind CSS, Supabase

**Locatie:** `gerustthuis-admin/`

### 7. iOS App (Mantelzorgers)

React Native + Expo iOS app voor mantelzorgers.

**Tech stack:** React Native, Expo SDK 54, TypeScript, Expo Router, Zustand

**Locatie:** `gerustthuis-app/`

---

## Data Flow

```
Hue Bridge (v1 + v2 API)
    │
    ▼
hue-sync-state (elke 5 min)
    │
    ├──► hue_devices.last_state (UPDATE - alleen bij change)
    │
    ├──► activity_events (INSERT bij state change)
    │         │
    │         ▼
    └──► room_activity (UPSERT per 5-min window)
                  │
                  ▼
         room_activity_hourly (TABLE - gevuld door pg_cron)
                  │
                  ▼
         Dashboard heatmap (7 dagen)

daily_activity_stats (berekend door pg_cron via calculate_daily_activity_stats())
         │
         ▼
    Patronen + Analyse views
```

---

## Authenticatie

### Gebruikers
- Supabase Auth (email/password)
- Automatische household aanmaak bij signup
- Uitnodigingssysteem voor mantelzorgers

### Hue Integratie
- OAuth 2.0 flow via Philips Hue Remote API
- Token refresh automatisch bij polling
- Zie [HUE_INTEGRATION.md](HUE_INTEGRATION.md)

---

## Multi-tenancy

Household-based multi-tenancy:

```
households
    │
    ├── household_members (user_id, role: admin/viewer)
    │
    └── config_id → hue_config → alle data tabellen
```

**Access control:** `get_accessible_config_ids()` SQL functie bepaalt welke config IDs een user mag zien. Alle RLS policies gebruiken deze functie.

---

## Deployment

| Component | Hosting |
|-----------|---------|
| Portaal | Vercel |
| Website | Vercel |
| Database | Supabase |
| Edge Functions | Supabase |

---

## Environment Variables

### Frontend (gerustthuis-portaal)
```bash
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxx
VITE_HUE_CLIENT_ID=xxx
```

### Backend (Supabase Edge Functions)
```bash
HUE_CLIENT_ID=xxx
HUE_CLIENT_SECRET=xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=xxx
```
