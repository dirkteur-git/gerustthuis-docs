# GerustThuis Anomaly Detection

Documentatie over het patroonherkenningssysteem in GerustThuis.

**Laatst bijgewerkt:** 2026-02-10

---

## Overzicht

GerustThuis gebruikt een **Isolation Forest-achtige** benadering om afwijkende activiteitspatronen te detecteren. Het systeem leert wat "normaal" is voor een bewoner en signaleert wanneer het gedrag significant afwijkt.

---

## Dag-Vector: 15 Activiteitsmetingen

Elke dag wordt samengevat in een vector van 15 metingen:

| Index | Meting | Beschrijving | Eenheid |
|-------|--------|--------------|---------|
| 0 | `eerste_activiteit` | Eerste activiteit van de dag | Decimaal uur (bijv. 7.5 = 07:30) |
| 1 | `laatste_activiteit` | Laatste activiteit van de dag | Decimaal uur |
| 2 | `events_ochtend` | Activiteit 05:00-10:00 | Aantal events |
| 3 | `events_middag` | Activiteit 10:00-17:00 | Aantal events |
| 4 | `events_avond` | Activiteit 17:00-22:00 | Aantal events |
| 5 | `events_nacht` | Activiteit 22:00-05:00 | Aantal events |
| 6 | `motion_events` | Bewegingssensor triggers | Aantal events |
| 7 | `light_events` | Lamp aan/uit events | Aantal events |
| 8 | `door_events` | Deur open/dicht events | Aantal events |
| 9 | `woonkamer` | Activiteit in woonkamer | Aantal events |
| 10 | `badkamer` | Activiteit in badkamer | Aantal events |
| 11 | `berging` | Activiteit in berging | Aantal events |
| 12 | `toilet` | Activiteit in toilet | Aantal events |
| 13 | `actieve_kamers` | Aantal kamers met activiteit | Aantal kamers |
| 14 | `minuten_actief` | Totale actieve tijd | Minuten |

---

## Anomaly Score Berekening

### Z-Score Methode

Voor elke meting wordt een z-score berekend:

```
z = (waarde - gemiddelde) / standaarddeviatie
```

De **maximale z-score** over alle metingen bepaalt het zorgniveau:

| Max Z-Score | Zorgniveau | Beschrijving |
|-------------|------------|--------------|
| < 1.0 | `ok` | Alles normaal |
| 1.0 - 2.0 | `let_op` | Kleine afwijking, let op |
| 2.0 - 3.0 | `zorg` | Aandacht nodig |
| > 3.0 | `alert` | Directe actie vereist |

### Dagscore

De dagscore is een intuïtievere weergave (0-100):

```javascript
dagscore = Math.max(0, 100 - (max_z_score * 33))
```

| Dagscore | Betekenis |
|----------|-----------|
| 70-100 | Normaal patroon |
| 40-69 | Let op |
| 0-39 | Aandacht nodig |

---

## Verwachte Ranges (p5-p95)

Voor elke meting worden percentielgrenzen berekend:

- **p5**: 5e percentiel (ondergrens van normaal)
- **p95**: 95e percentiel (bovengrens van normaal)

Waarden binnen p5-p95 worden als normaal beschouwd.

### Berekening

```javascript
const getHistoricalStats = (idx) => {
  const values = dagVectors
    .map(dv => dv.vector[idx])
    .filter(val => val !== -1 && val !== null)
    .sort((a, b) => a - b)

  const p5Idx = Math.floor(values.length * 0.05)
  const p95Idx = Math.min(values.length - 1, Math.floor(values.length * 0.95))

  return { p5: values[p5Idx], p95: values[p95Idx] }
}
```

---

## Normaalverdeling Visualisatie

Het systeem visualiseert de distributie van elke meting:

```
                    ╭──────────╮
                   ╱            ╲
                  ╱              ╲
                 ╱                ╲
               ╱                  ╲
           ───╱────────|────────────╲───
             min      gem          max
                       ●
                    vandaag
```

### SVG Curve Generatie

```javascript
const getNormalDistributionPath = (mean, std, min, max) => {
  const points = []
  for (let i = 0; i <= 50; i++) {
    const x = rangeMin + (i / 50) * range
    const z = (x - mean) / std
    const y = Math.exp(-0.5 * z * z) / (std * Math.sqrt(2 * Math.PI))
    points.push({ x, y })
  }
  return points
}
```

---

## Database Tabellen

### `daily_activity_stats` (primaire bron)

De belangrijkste tabel voor anomaly detection. Bevat alle benodigde data per dag:

```sql
CREATE TABLE daily_activity_stats (
    id                    UUID PRIMARY KEY,
    config_id             UUID REFERENCES hue_config(id),
    date                  DATE NOT NULL,
    first_activity        TIME,              -- Eerste activiteit
    last_activity         TIME,              -- Laatste activiteit
    total_events          INTEGER,           -- Totaal events
    events_per_hour       INTEGER[24],       -- Events per uur (index 0 = 00:00-01:00)
    active_hours          INTEGER,           -- Uren met ≥1 event
    rooms_active          INTEGER,           -- Unieke kamers met activiteit
    rooms_available       INTEGER,           -- Totaal beschikbare kamers
    longest_gap_minutes   INTEGER,           -- Langste periode zonder events
    night_events          INTEGER,           -- Events 23:00-06:00
    night_active_hours    INTEGER,           -- Actieve uren 23:00-06:00
    UNIQUE(config_id, date)
);
```

**Anomaly-relevante velden:**
| Veld | Anomaly Use Case |
|------|------------------|
| `first_activity` | "Laat opgestaan" detectie |
| `last_activity` | "Vroeg naar bed" detectie |
| `events_per_hour` | Uur-voor-uur patroonanalyse |
| `longest_gap_minutes` | Inactiviteitsalarm (bijv. > 3 uur) |
| `night_events` | Nachtelijke onrust detectie |
| `rooms_active` | "Niet alle kamers bezocht" detectie |

### Vector Berekening uit `daily_activity_stats`

De 15-dimensionale dag-vector kan direct uit `daily_activity_stats` berekend worden:

```javascript
const buildDayVector = (stats) => {
  const h = stats.events_per_hour  // INTEGER[24]

  return [
    timeToDecimal(stats.first_activity),   // 0: eerste_activiteit
    timeToDecimal(stats.last_activity),    // 1: laatste_activiteit
    sum(h.slice(5, 10)),                   // 2: events_ochtend (05:00-10:00)
    sum(h.slice(10, 17)),                  // 3: events_middag (10:00-17:00)
    sum(h.slice(17, 22)),                  // 4: events_avond (17:00-22:00)
    sum(h.slice(22, 24)) + sum(h.slice(0, 5)), // 5: events_nacht
    null,                                  // 6: motion_events (apart query)
    null,                                  // 7: light_events (apart query)
    null,                                  // 8: door_events (apart query)
    null,                                  // 9-12: per kamer (apart query)
    null,
    null,
    null,
    stats.rooms_active,                    // 13: actieve_kamers
    stats.active_hours * 60 / 12,          // 14: minuten_actief (geschat)
  ]
}
```

### `dag_vectors` (niet geïmplementeerd - toekomstig)

Pre-computed vectoren voor snellere queries:

```sql
CREATE TABLE dag_vectors (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id   UUID REFERENCES hue_config(id),
    datum       DATE NOT NULL,
    vector      NUMERIC[15] NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### `uur_verwachtingen` (niet geïmplementeerd - toekomstig)

Verwachte waarden per uur van de dag:

```sql
CREATE TABLE uur_verwachtingen (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id    UUID REFERENCES hue_config(id),
    uur          INTEGER NOT NULL,  -- 0-23
    motion_mean  NUMERIC,
    motion_std   NUMERIC,
    -- ... meer metingen
    UNIQUE(config_id, uur)
);
```

---

## RPC Functie: `check_nu` (niet geïmplementeerd - toekomstig)

Real-time anomaly check:

```sql
CREATE OR REPLACE FUNCTION check_nu()
RETURNS JSON AS $$
DECLARE
    result JSON;
    current_vector NUMERIC[15];
    max_z NUMERIC := 0;
    afwijkingen JSON[];
BEGIN
    -- Bereken huidige vector tot nu
    -- Vergelijk met historische gemiddelden
    -- Bepaal zorgniveau

    RETURN json_build_object(
        'zorgniveau', zorgniveau,
        'max_z_score', max_z,
        'vector', current_vector,
        'afwijkingen', afwijkingen
    );
END;
$$ LANGUAGE plpgsql;
```

---

## Waarom Geen Echte Isolation Forest?

Een volledige Isolation Forest implementatie zou vereisen:
- Random forest training op historische data
- Tree-based anomaly scoring
- Periodieke hertraining

De huidige **z-score benadering** is:
- Eenvoudiger te implementeren in SQL/JavaScript
- Real-time berekenbaar (geen model training)
- Transparant en uitlegbaar voor zorgverleners
- Voldoende voor de use case (dagpatronen vergelijken)

---

## Toekomstige Verbeteringen

1. **Weekdag-aware**: Aparte verwachtingen voor werkdagen vs weekend
2. **Seizoensaanpassing**: Zomer/winter patronen (licht/donker)
3. **Trend detectie**: Geleidelijke veranderingen over weken
4. **Machine Learning**: Echte Isolation Forest voor complexere patronen

---

## Implementatie Locaties

| Component | Locatie | Beschrijving |
|-----------|---------|--------------|
| Data | `daily_activity_stats` tabel | Primaire bron voor anomaly detection |
| Data | `activity_events` tabel | Ruwe events voor device-type analyse |
| Functie | `calculate_daily_activity_stats()` | Berekent dagelijkse stats |
| View | `room_activity_hourly` | Uurlijkse aggregatie per kamer |

### Huidige Frontend Implementatie

| Component | Locatie | Beschrijving |
|-----------|---------|--------------|
| Analyse | `gerustthuis-portaal/src/views/Analyse.vue` | Z-score anomaly detection per dag, score breakdown |
| Patronen | `gerustthuis-portaal/src/views/Patronen.vue` | Dagritme, vandaag vs normaal, weekpatroon, trends |
| Utilities | `gerustthuis-portaal/src/composables/useDataQuality.js` | Gedeelde berekeningen (dayStart, dayEvents, avg, stddev) |

---

## Anomaly Queries

### Inactiviteitsalarm (> 3 uur gap)

```sql
SELECT date, longest_gap_minutes
FROM daily_activity_stats
WHERE config_id = 'xxx'
  AND longest_gap_minutes > 180
ORDER BY date DESC;
```

### Afwijkende opstaan/slapen tijden

```sql
WITH stats AS (
  SELECT
    AVG(EXTRACT(HOUR FROM first_activity) + EXTRACT(MINUTE FROM first_activity)/60) as avg_wake,
    STDDEV(EXTRACT(HOUR FROM first_activity) + EXTRACT(MINUTE FROM first_activity)/60) as std_wake
  FROM daily_activity_stats
  WHERE config_id = 'xxx'
    AND date > CURRENT_DATE - 30
)
SELECT
  das.date,
  das.first_activity,
  (EXTRACT(HOUR FROM das.first_activity) + EXTRACT(MINUTE FROM das.first_activity)/60 - stats.avg_wake) / NULLIF(stats.std_wake, 0) as z_score
FROM daily_activity_stats das, stats
WHERE das.config_id = 'xxx'
  AND das.date = CURRENT_DATE;
```

### Nachtelijke onrust detectie

```sql
SELECT date, night_events, night_active_hours
FROM daily_activity_stats
WHERE config_id = 'xxx'
  AND night_events > (
    SELECT AVG(night_events) + 2 * STDDEV(night_events)
    FROM daily_activity_stats
    WHERE config_id = 'xxx'
      AND date > CURRENT_DATE - 30
  )
ORDER BY date DESC;
```

### Dashboard Status Query

```sql
SELECT
  date,
  total_events,
  active_hours,
  longest_gap_minutes,
  CASE
    WHEN longest_gap_minutes > 180 THEN 'alert'
    WHEN total_events < 10 THEN 'warning'
    WHEN active_hours < 8 THEN 'warning'
    ELSE 'ok'
  END as status
FROM daily_activity_stats
WHERE config_id = 'xxx'
ORDER BY date DESC
LIMIT 7;
```
