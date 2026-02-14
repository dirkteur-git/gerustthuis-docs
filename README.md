# GerustThuis Documentatie

Centrale documentatie voor het GerustThuis ecosysteem.

## Repositories

| Repository | Beschrijving |
|------------|--------------|
| [gerustthuis-portaal](https://github.com/dirkteur-git/gerustthuis-portaal) | Vue 3 dashboard app (activiteit, patronen, instellingen) |
| [gerustthuis-supabase](https://github.com/dirkteur-git/gerustthuis-supabase) | Database migraties en Supabase Edge Functions |
| [gerustthuis-website](https://github.com/dirkteur-git/gerustthuis-website) | Marketing website (particulier + zakelijk) |
| [gerustthuis-app](https://github.com/dirkteur-git/gerustthuis-app) | React Native + Expo iOS app voor mantelzorgers |
| [gerustthuis-docs](https://github.com/dirkteur-git/gerustthuis-docs) | Deze repository - documentatie en brandbook |
| [gerustthuis-projectplan](https://github.com/dirkteur-git/gerustthuis-projectplan) | Intern projectplan (10 fasen) |

## Documentatie

| Document | Beschrijving |
|----------|--------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Systeemarchitectuur en componenten overzicht |
| [DATABASE_DESIGN.md](DATABASE_DESIGN.md) | Database schema, tabellen, RLS policies |
| [PORTAAL_ARCHITECTURE.md](PORTAAL_ARCHITECTURE.md) | Frontend architectuur en views |
| [HUE_INTEGRATION.md](HUE_INTEGRATION.md) | Philips Hue API integratie |
| [ANOMALY_DETECTION.md](ANOMALY_DETECTION.md) | Patroonherkenning en anomaly detection |
| [ROADMAP.md](ROADMAP.md) | Feature roadmap en backlog |
| [Brandbook.md](Brandbook.md) | Huisstijl en branding |

## Over GerustThuis

GerustThuis is een AI-powered thuismonitoringsysteem voor ouderen en hun mantelzorgers. Het systeem detecteert activiteitspatronen via Philips Hue sensoren en waarschuwt mantelzorgers bij afwijkingen, zonder camera's of microfoons.

### Architectuur

```
Philips Hue Bridge → Supabase Edge Functions (polling) → PostgreSQL → Vue 3 Portaal
```

### Privacy-first Design

- Geen camera's of microfoons
- Data per huishouden geïsoleerd via Row Level Security
- Mantelzorger ziet patronen en afwijkingen, niet exacte bewegingen
