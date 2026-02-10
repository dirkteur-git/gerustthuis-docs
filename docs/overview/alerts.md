# Alert Systeem

## Status

> **Nog niet geïmplementeerd.** Dit document beschrijft het geplande alert systeem. Momenteel wordt anomaly detection alleen via de Analyse en Patronen views in het Portaal getoond, zonder actieve notificaties.

## Overzicht

GerustThuis plant een twee-laags alert systeem: frontend-detectie (huidige situatie) en backend-notificaties (toekomstig).

## Huidige Implementatie

### Frontend Detectie (live)

Anomaly detection draait in de browser en wordt getoond op drie plekken:

| View | Methode | Wat wordt getoond |
|------|---------|-------------------|
| Dashboard | Ratio-check (events vandaag vs gemiddelde) | Status banner: "Normale dag", "Rustige dag", "Erg rustig", "Actieve dag" |
| Patronen | Vergelijking vandaag vs 14-dagen baseline | 5 metrics met severity badges (low/medium/high) |
| Analyse | Z-score per feature | Anomaly score 0-1, breakdown per feature |

Zie [ANOMALY_DETECTION.md](../../ANOMALY_DETECTION.md) voor details over het algoritme.

### Wat nog ontbreekt

- Geen backend-side anomaly checks (alles draait in de browser)
- Geen email/push/SMS notificaties
- Geen configureerbare drempelwaarden per huishouden
- Geen alert historie/log

## Geplande Anomalie Types

| Code | Naam | Trigger | Severity |
|------|------|---------|----------|
| `NO_MOTION` | Geen beweging | Geen sensor activiteit > X uur (dag) | critical |
| `LATE_START` | Laat opstaan | Eerste activiteit > 2u later dan gemiddeld | warning |
| `EARLY_END` | Vroeg naar bed | Laatste activiteit > 2u eerder dan gemiddeld | info |
| `NIGHT_UNREST` | Nachtelijke onrust | Veel nacht-events vs baseline | warning |
| `LOW_ACTIVITY` | Weinig activiteit | <50% van gemiddeld dagelijks events | warning |
| `BATTERY_LOW` | Batterij laag | Sensor batterij <20% | info |

## Geplande Configuratie

Alert thresholds configureerbaar per huishouden:

```json
{
  "no_motion_hours": 4,
  "late_start_threshold_minutes": 120,
  "early_end_threshold_minutes": 120,
  "night_motion_threshold": 3,
  "low_activity_percentage": 50,
  "battery_low_threshold": 20
}
```

## Geplande Alert Kanalen

- Email notificaties
- Push notificaties (browser)
- In-app alert historie
