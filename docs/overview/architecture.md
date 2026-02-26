# GerustThuis Architectuur

## Overzicht

GerustThuis is een AI-powered thuismonitoringsysteem voor ouderen en hun mantelzorgers. Het systeem detecteert activiteitspatronen via sensoren en waarschuwt mantelzorgers bij afwijkingen, zonder camera's of microfoons.

## Huidige Architectuur (Cloud-only)

De huidige implementatie draait volledig in de cloud via Philips Hue + Supabase:

```
Philips Hue Bridge
      │ ZigBee (sensoren + lampen)
      │
      ▼
┌─────────────────────────────────────┐
│   Supabase Edge Functions           │
│   (hue-sync-state, elke 5 min)     │
│   - Hue v1 + v2 API polling        │
│   - State change detection          │
│   - Token refresh                   │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│   Supabase PostgreSQL               │
│   - activity_events (ruwe events)   │
│   - room_activity (5-min aggregat)  │
│   - daily_activity_stats (dag)      │
│   - RLS via get_accessible_config_ids() │
└───────────┬─────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│   Vue 3 Portaal (Vercel)            │
│   - Dashboard (heatmap, status)     │
│   - Patronen (dagritme, trends)     │
│   - Analyse (z-score anomaly)       │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│   React PWA (Vite + Tailwind)       │
│   - Overzicht (status, activiteit)  │
│   - Familie, Meldingen, Instellingen│
└─────────────────────────────────────┘
            │
            ▼
      ┌─────────────┐
      │ Mantelzorger│
      └─────────────┘
```

## Toekomstige Architectuur (Lokaal + Cloud)

De geplande architectuur voegt een lokale Raspberry Pi gateway toe voor betere privacy en realtime detectie:

```
Aqara Sensoren
      │ Zigbee
      ▼
┌─────────────────┐
│  Zigbee2MQTT    │
└────────┬────────┘
         │ MQTT
         ▼
┌─────────────────────────────────────┐
│         Python Processor            │
│   (lokale event verwerking)         │
└───────────┬───────────┬─────────────┘
            │           │
     Ruwe events    Aggregaties
            │           │
            ▼           ▼
┌───────────────┐ ┌─────────────────┐
│    SQLite     │ │    Supabase     │
│   (Lokaal)    │ │    (Cloud)      │
└───────┬───────┘ └────────┬────────┘
        │                  │
        ▼                  ▼
┌───────────────┐ ┌─────────────────┐
│ Lokale Alerts │ │  Web Dashboard  │
│  (speaker)    │ │   Vue 3 App     │
└───────────────┘ └─────────────────┘
```

### Voordelen van lokale gateway

| Principe | Beschrijving |
|----------|--------------|
| **Privacy/AVG** | Ruwe bewegingsdata blijft lokaal op de Pi. Alleen samenvattingen naar de cloud. |
| **Betrouwbaarheid** | Pi werkt door bij internet-uitval. |
| **Latency** | Kritieke detectie (geen beweging) draait lokaal. |
| **Kosten** | Minder cloud-calls, Supabase free tier gaat langer mee. |

> **Status:** De lokale gateway is nog niet geïmplementeerd. Zie [sensor specificaties](../hardware/sensors.md) voor geplande hardware.

## Privacy Model

### Huidige situatie (cloud-only)

Alle data gaat via Supabase (cloud). Data is beveiligd met:
- Row Level Security (RLS) per huishouden
- OAuth tokens voor Hue API
- Supabase Auth voor gebruikers

### Toekomstig (lokaal + cloud)

| Data | Lokaal (Pi) | Cloud (Supabase) |
|------|-------------|-------------------|
| Ruwe sensor events | Ja (14 dagen) | Nee |
| Aggregaties per uur | Ja | Ja |
| Dagelijkse stats | Ja | Ja |
| Alert meldingen | Ja | Ja |
| Sensor status | Ja | Ja |

## Componenten

Zie de hoofd [ARCHITECTURE.md](../../ARCHITECTURE.md) voor de volledige componentbeschrijving.
