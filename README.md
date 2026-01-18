# GerustThuis Documentatie

Centrale documentatie voor het GerustThuis ecosysteem.

## Repositories

| Repository | Beschrijving |
|------------|--------------|
| [gerustthuis-website](https://github.com/dirkteur-git/gerustthuis-website) | Marketing website (particulier + zakelijk) |
| [gerustthuis-cloud](https://github.com/dirkteur-git/gerustthuis-cloud) | Dashboards, API, Supabase backend |
| [gerustthuis-device](https://github.com/dirkteur-git/gerustthuis-device) | Raspberry Pi gateway software |
| [gerustthuis-docs](https://github.com/dirkteur-git/gerustthuis-docs) | Deze repository |

## Documentatie Structuur

```
docs/
├── overview/           # Project overzicht en architectuur
├── hardware/           # Sensoren en Raspberry Pi setup
├── database/           # Database schemas (SQLite + Supabase)
└── deployment/         # Deployment handleidingen
```

## Quick Links

- [Architectuur Overzicht](docs/overview/architecture.md)
- [Data Flow](docs/overview/data-flow.md)
- [Sensor Specificaties](docs/hardware/sensors.md)
- [Database Schema](docs/database/schema.md)

## Over GerustThuis

GerustThuis is een AI-powered thuismonitoringsysteem voor ouderen en hun mantelzorgers. Het systeem detecteert activiteitspatronen via sensoren en waarschuwt mantelzorgers bij afwijkingen, zonder camera's of microfoons.

### Privacy-first Design

- Ruwe bewegingsdata blijft lokaal op de Raspberry Pi
- Alleen samenvattingen gaan naar de cloud
- Geen camera's of microfoons
- Mantelzorger ziet alleen alerts, niet exacte bewegingen
