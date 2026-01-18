# GerustThuis Architectuur

## Overzicht

GerustThuis is een AI-powered thuismonitoringsysteem voor ouderen en hun mantelzorgers. Het systeem detecteert activiteitspatronen via sensoren en waarschuwt mantelzorgers bij afwijkingen, zonder camera's of microfoons.

## Design Principes

| Principe | Beschrijving |
|----------|--------------|
| **Privacy/AVG** | Ruwe bewegingsdata blijft lokaal op de Pi. Alleen samenvattingen naar de cloud. |
| **Betrouwbaarheid** | Pi werkt door bij internet-uitval. Gateway heartbeat naar cloud voor "Pi offline" detectie. |
| **Kosten** | Supabase free tier gaat lang mee met alleen geaggregeerde data. |
| **Latency** | Kritieke detectie (geen beweging) draait lokaal, niet afhankelijk van cloud roundtrip. |

## Data Flow

```
Aqara Sensoren
      │ Zigbee
      ▼
┌─────────────────┐
│  Zigbee2MQTT    │
└────────┬────────┘
         │ MQTT
         ▼
┌─────────────────┐
│    Mosquitto    │
└────────┬────────┘
         │
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
└───────────────┘ └────────┬────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Mantelzorger│
                    └─────────────┘
```

## Componenten

### 1. Sensoren (Zigbee/WiFi/Z-Wave)

Zie [Sensor Specificaties](../hardware/sensors.md)

### 2. Raspberry Pi Gateway

**Stack:**
- Zigbee2MQTT (Zigbee → MQTT bridge)
- Mosquitto (MQTT broker, met credentials)
- Python processor (event verwerking)
- SQLite (lokale opslag)
- Systemd services (auto-start)

**Security:**
- MQTT: Mosquitto met username/password (`allow_anonymous false`)
- API Key: Opgeslagen in `/etc/gerustthuis/.env` (root:root 600)
- Zigbee2MQTT: Eigen user/pass voor MQTT verbinding
- Supabase: Service key (niet anon key) voor gateway sync

### 3. Cloud (Supabase)

Zie [Database Schema](../database/schema.md)

### 4. Frontend

**Technologie:**
- Vue 3 + Composition API
- Vite
- Tailwind CSS
- Vercel hosting

## Privacy Model

### Wat ziet wie?

| Data | Bewoner (lokaal) | Mantelzorger (app) | Cloud |
|------|------------------|-------------------|-------|
| Live sensordata | Ja (op WiFi) | Nee | Nee |
| Welke kamer actief | Ja | Nee | Nee |
| Exacte tijden | Ja | Nee | Alleen samenvattingen |
| Bewegingshistorie | Ja (14 dagen) | Nee | Nee |
| Alert meldingen | Ja | Ja | Ja |
| Sensor status | Ja | Ja | Ja |
| Batterijniveaus | Ja | Ja | Ja |
| Hub online status | Ja | Ja | Ja |

### Toegangsregels

- **Lokaal netwerk (WiFi):** Volledige toegang tot live dashboard en historische data
- **Op afstand (internet):** Alleen alerts, sensor health, en hub status
- **Ruwe data:** Verlaat nooit de woning, blijft op de Pi

### Baseline Learning

Het systeem leert 7 dagen het normale patroon:
- Gemiddelde opstaantijd
- Gemiddelde laatste activiteit
- Normale kamervolgorde
- Typische koelkast-openingen

Na de baseline week worden afwijkingen pas gemeld.
