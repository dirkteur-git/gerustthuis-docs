# GerustThuis Anomaly Detection

Documentatie over het patroonherkenningssysteem in GerustThuis.

**Laatst bijgewerkt:** 2026-01-31

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

### `dag_vectors`

Opslag van dagelijkse vectoren:

```sql
CREATE TABLE dag_vectors (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id   UUID REFERENCES hue_config(id),
    datum       DATE NOT NULL,
    vector      NUMERIC[15] NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### `uur_verwachtingen`

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

## RPC Functie: `check_nu`

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
| UI | `gerustthuis-cloud/src/views/consumer/Patronen.vue` | Dashboard met anomaly visualisatie |
| API | Supabase RPC `check_nu` | Real-time anomaly check |
| Data | `dag_vectors` tabel | Historische dagvectoren |
| View | `room_activity_hourly` | Input voor vector berekening |
