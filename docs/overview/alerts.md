# Alert Systeem

## Overzicht

GerustThuis heeft een twee-laags alert systeem: lokaal (realtime) en cloud (batch/trends).

## Anomalie Types

| Code | Naam | Trigger | Severity | Waar |
|------|------|---------|----------|------|
| `NO_MOTION` | Geen beweging | Geen sensor activiteit > X uur (dag) | critical | Lokaal |
| `LATE_START` | Laat opstaan | Eerste activiteit > 2u later dan gemiddeld | warning | Cloud |
| `EARLY_END` | Vroeg naar bed | Laatste activiteit > 2u eerder dan gemiddeld | info | Cloud |
| `NIGHT_UNREST` | Nachtelijke onrust | >3 bewegingen tussen 00:00-05:00 | warning | Lokaal |
| `FRIDGE_SKIP` | Koelkast overgeslagen | Koelkast niet geopend voor 12:00 | warning | Lokaal |
| `ROOM_MISSING` | Kamer overgeslagen | Belangrijke kamer (badkamer) niet bezocht | info | Cloud |
| `LOW_ACTIVITY` | Weinig activiteit | <50% van gemiddeld dagelijks events | warning | Cloud |
| `BATTERY_LOW` | Batterij laag | Sensor batterij <20% | info | Lokaal |
| `GATEWAY_OFFLINE` | Gateway offline | Geen heartbeat >10 min | critical | Cloud |

## Detectie Locatie

### Lokaal (realtime, urgent)

Deze checks draaien op de Raspberry Pi voor minimale latency:

- **`NO_MOTION`:** Directe check, kan niet wachten op cloud
- **`NIGHT_UNREST`:** Realtime detectie voor directe alert
- **`FRIDGE_SKIP`:** Ochtend check
- **`BATTERY_LOW`:** Bij elke sensor event

### Cloud (batch, trends)

Deze checks draaien in Supabase Edge Functions:

- **`LATE_START`, `EARLY_END`:** Vergelijking met persoonlijke baseline
- **`ROOM_MISSING`, `LOW_ACTIVITY`:** Dagelijkse analyse
- **`GATEWAY_OFFLINE`:** Supabase Edge Function checkt last_seen

## Alert Kanalen

### Lokaal (op Pi)

- Speaker/buzzer voor directe alerts
- Lokale webinterface (op WiFi)
- SMS gateway fallback (optioneel)

### Cloud

- Push notificaties naar app
- Email alerts
- SMS (voor critical alerts)

## Configuratie

Alert thresholds zijn configureerbaar per huishouden:

```json
{
  "no_motion_hours": 4,
  "late_start_threshold_minutes": 120,
  "early_end_threshold_minutes": 120,
  "night_start_hour": 0,
  "night_end_hour": 5,
  "night_motion_threshold": 3,
  "fridge_check_hour": 12,
  "low_activity_percentage": 50,
  "battery_low_threshold": 20,
  "gateway_offline_minutes": 10
}
```
