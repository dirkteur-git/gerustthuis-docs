# GerustThuis Documentatie

Centrale documentatie voor het GerustThuis ecosysteem.

> **Broncode staat in aparte repo's. Alle documentatie staat hier.**

---

## Repositories

| Repository | Beschrijving | Documentatie |
|------------|--------------|--------------|
| [gerustthuis-portaal](https://github.com/dirkteur-git/gerustthuis-portaal) | Vue 3 dashboard voor mantelzorgers (activiteit, patronen, instellingen) | [PORTAAL_ARCHITECTURE.md](PORTAAL_ARCHITECTURE.md) |
| [gerustthuis-app](https://github.com/dirkteur-git/gerustthuis-app) | React + Vite PWA voor mantelzorgers (mobiel) | [APP_DESIGN.md](APP_DESIGN.md) |
| [gerustthuis-supabase](https://github.com/dirkteur-git/gerustthuis-supabase) | Database migraties en Supabase Edge Functions | [DATABASE_DESIGN.md](DATABASE_DESIGN.md) |
| [gerustthuis-website](https://github.com/dirkteur-git/gerustthuis-website) | Marketing website (oud — Vue 3, legacy) | [Brandbook.md](Brandbook.md) |
| [gerustthuis-website-nuxt](https://github.com/dirkteur-git/gerustthuis-website-nuxt) | Marketing website (actief — Nuxt 3, SSG) | [Brandbook.md](Brandbook.md) |
| [gerustthuis-admin](https://github.com/dirkteur-git/gerustthuis-admin) | Admin portaal (projectplan, beheer, rapportages) | [ADMIN_PORTAAL.md](ADMIN_PORTAAL.md) |
| [gerustthuis-docs](https://github.com/dirkteur-git/gerustthuis-docs) | Deze repository — documentatie en brandbook | — |

---

## Documentatie

### Architectuur & Systeem

| Document | Beschrijving |
|----------|--------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Systeemoverzicht: componenten, data flow, deployment |
| [DATABASE_DESIGN.md](DATABASE_DESIGN.md) | Database schema, tabellen, RLS policies |
| [HUE_INTEGRATION.md](HUE_INTEGRATION.md) | Philips Hue API integratie (OAuth, polling, devices) |
| [ANOMALY_DETECTION.md](ANOMALY_DETECTION.md) | Patroonherkenning en anomaly detection (18 features) |

### Frontend

| Document | Beschrijving |
|----------|--------------|
| [PORTAAL_ARCHITECTURE.md](PORTAAL_ARCHITECTURE.md) | Vue 3 dashboard — views, componenten, data flow |
| [APP_DESIGN.md](APP_DESIGN.md) | PWA app — schermen, design tokens, privacy-principes |

### Product & Strategie

| Document | Beschrijving |
|----------|--------------|
| [USER_STORIES.md](USER_STORIES.md) | Personages (bewoner, mantelzorger, installateur) en user stories |
| [ROADMAP.md](ROADMAP.md) | Feature status en geplande verbeteringen |
| [ADMIN_PORTAAL.md](ADMIN_PORTAAL.md) | Admin portaal: scope, database, fases |

### Branding & Design

| Document | Beschrijving |
|----------|--------------|
| [Brandbook.md](Brandbook.md) | Huisstijl: kleuren, typografie, logo, tone of voice |

### Technisch (docs/)

| Document | Beschrijving |
|----------|--------------|
| [docs/overview/architecture.md](docs/overview/architecture.md) | Architectuuroverzicht met toekomstig lokaal model |
| [docs/overview/alerts.md](docs/overview/alerts.md) | Alert systeem: types, triggers, privacy |
| [docs/database/schema.md](docs/database/schema.md) | Database schema samenvatting |
| [docs/hardware/sensors.md](docs/hardware/sensors.md) | Sensor specificaties en plaatsingsadvies |
| [docs/legal/privacyverklaring.md](docs/legal/privacyverklaring.md) | Privacyverklaring |
| [docs/legal/cookieverklaring.md](docs/legal/cookieverklaring.md) | Cookieverklaring |
| [docs/legal/company.md](docs/legal/company.md) | Bedrijfsgegevens BoostiX / GerustThuis |

---

## Over GerustThuis

GerustThuis is een thuismonitoringsysteem voor ouderen en hun mantelzorgers. Het systeem detecteert activiteitspatronen via Philips Hue sensoren en geeft mantelzorgers rust — zonder camera's of microfoons.

### Architectuur (huidig)

```
Philips Hue Bridge
       │
       ▼
Supabase Edge Functions (polling elke 5 min)
       │
       ▼
Supabase PostgreSQL (RLS per huishouden)
       │
       ├──► Vue 3 Portaal (dashboard, desktop)
       │
       └──► React PWA (mobiele app, mantelzorgers)
```

### Privacy-first

- Geen camera's of microfoons
- Data per huishouden geïsoleerd via Row Level Security
- App toont patronen per dagdeel — geen exacte tijdstippen
- Bewoner heeft geen account en ziet geen data

### Bedrijf

BoostiX (handelsnaam GerustThuis) — KVK 90087291
Zie [docs/legal/company.md](docs/legal/company.md)
