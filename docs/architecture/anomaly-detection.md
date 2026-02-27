# GerustThuis Anomaly Detection

Documentatie over het patroonherkenningssysteem in GerustThuis.

**Laatst bijgewerkt:** 2026-02-14

---

## Overzicht

GerustThuis gebruikt **z-score anomaly detection** om afwijkende activiteitspatronen te detecteren. Het systeem leert wat "normaal" is voor een bewoner door een baseline te berekenen over de afgelopen 14 dagen, en signaleert wanneer het gedrag significant afwijkt.

De aanpak is bewust eenvoudig gehouden: transparant, uitlegbaar voor zorgverleners, en real-time berekenbaar zonder model training.

---

## Features: 18 Activiteitsmetingen in 6 Groepen

Elke dag wordt geanalyseerd op basis van 18 features, georganiseerd in 6 groepen:

### Groep 1: Tijdstip

| # | Feature | Beschrijving | Bron | Weight |
|---|---------|--------------|------|--------|
| 1 | `first_activity` | Eerste activiteit van de dag | daily_activity_stats | 1.0 |
| 2 | `last_activity` | Laatste activiteit van de dag | daily_activity_stats | 1.0 |
| 3 | `awake_duration` | Wakkere duur (last - first) in minuten | Berekend client-side | 0.8 |

### Groep 2: Volume

| # | Feature | Beschrijving | Bron | Weight |
|---|---------|--------------|------|--------|
| 4 | `total_events` | Totaal aantal sensor events | daily_activity_stats | 1.0 |
| 5 | `active_hours` | Uren met minimaal 1 event | daily_activity_stats | 1.0 |
| 6 | `morning_events` | Events 06:00-12:00 | Berekend uit events_per_hour[] | 0.8 |
| 7 | `afternoon_events` | Events 12:00-18:00 | Berekend uit events_per_hour[] | 0.8 |
| 8 | `evening_events` | Events 18:00-23:00 | Berekend uit events_per_hour[] | 0.8 |

### Groep 3: Rust & nacht

| # | Feature | Beschrijving | Bron | Weight |
|---|---------|--------------|------|--------|
| 9 | `longest_gap_minutes` | Langste periode zonder events | daily_activity_stats | 1.2 |
| 10 | `night_events` | Events 23:00-06:00 | daily_activity_stats | 1.0 |
| 11 | `night_active_hours` | Actieve uren 23:00-06:00 | daily_activity_stats | 0.8 |

### Groep 4: Ruimte

| # | Feature | Beschrijving | Bron | Weight |
|---|---------|--------------|------|--------|
| 12 | `rooms_active` | Unieke kamers met activiteit | daily_activity_stats | 0.8 |
| 13 | `room_ratio` | rooms_active / rooms_available | Berekend client-side | 0.6 |
| 14 | `main_room_pct` | % events in meest actieve kamer | room_activity_hourly | 0.6 |

**Voorwaarde:** Kamer-features #13, #14 worden overgeslagen als `rooms_available <= 1`.

### Groep 5: Sensor type

| # | Feature | Beschrijving | Bron | Weight |
|---|---------|--------------|------|--------|
| 15 | `motion_events` | Bewegingssensor events | daily_activity_stats | 0.8 |
| 16 | `door_events` | Deur/contact sensor events | daily_activity_stats | 0.8 |

### Groep 6: Patroon

| # | Feature | Beschrijving | Bron | Weight |
|---|---------|--------------|------|--------|
| 17 | `transition_count` | Kamerwisselingen per uur | room_activity_hourly | 0.6 |
| 18 | `activity_regularity` | Cosine similarity met baseline uurpatroon | Berekend client-side | 0.6 |

**Voorwaarde:** `transition_count` wordt overgeslagen als `rooms_available <= 1`.

---

## Anomaly Score Berekening

### Z-Score Methode

Per feature wordt een z-score berekend ten opzichte van de baseline:

```javascript
function calculateZScore(value, mean, stddev) {
  if (stddev === 0 || stddev === null || value === null || mean === null) return 0
  return (value - mean) / stddev
}
```

### Anomaly Score (gewogen combinatie)

De anomaly score combineert de **maximale absolute z-score** (gevoelig voor enkele grote afwijkingen) met het **gewogen gemiddelde** (gevoelig voor meerdere matige afwijkingen):

```javascript
const maxAbsZ = Math.max(...features.map(f => Math.abs(f.zScore)))

const totalWeight = validScores.reduce((sum, s) => sum + s.weight, 0)
const weightedAvgZ = validScores.reduce((sum, s) =>
  sum + Math.abs(s.zScore) * s.weight, 0
) / totalWeight

// 60% max + 40% gewogen gemiddelde
const combined = 0.6 * maxAbsZ + 0.4 * weightedAvgZ
const anomalyScore = Math.min(1, combined / 3)
```

**Waarom deze formule?**
- Een enkel extreem signaal (z=3) geeft nog steeds een hoge score (~0.60+)
- Maar 5 features die allemaal z=2 afwijken geven een hogere score dan 1 feature met z=2
- Feature weights zorgen dat klinisch belangrijke features (langste gap, eerste activiteit) zwaarder wegen

### Niveaus

| Anomaly Score | Label | Beschrijving |
|---------------|-------|--------------|
| 0 - 0.33 | `Normaal` | Alles binnen verwachting |
| 0.33 - 0.66 | `Afwijkend` | Let op, iets anders dan normaal |
| 0.66 - 1.0 | `Sterk afwijkend` | Duidelijke afwijking, bekijk even |

### Feature Weights

| Weight | Betekenis | Features |
|--------|-----------|----------|
| 1.2 | Kritiek | longest_gap_minutes |
| 1.0 | Hoog | first_activity, last_activity, total_events, active_hours, night_events |
| 0.8 | Normaal | awake_duration, morning/afternoon/evening_events, night_active_hours, rooms_active, motion_events, door_events |
| 0.6 | Informatief | room_ratio, main_room_pct, transition_count, activity_regularity |

### Severity per Feature

| |z-score| | Severity | Kleur |
|-----------|----------|-------|
| < 1.0 | `low` | Groen |
| 1.0 - 2.0 | `medium` | Amber |
| > 2.0 | `high` | Rood |

---

## Baseline Berekening

### Periode

De baseline wordt berekend over de **laatste 14 dagen**, exclusief de geselecteerde dag.

### Statistieken

Per feature worden berekend:
- **Gemiddelde (mu)**: `avg = sum(values) / count`
- **Standaarddeviatie (sigma)**: populatie-standaarddeviatie (minimum 1 om deling door 0 te voorkomen)
- **Min** en **Max**: voor de baseline tabel

### Minimum Data Vereiste

Er zijn minimaal **7 dagen** met data nodig voordat het systeem betrouwbare analyses kan maken (`MINIMUM_DAYS_REQUIRED`).

### Data Bronnen voor Baseline

De baseline combineert data uit twee tabellen:

| Bron | Features | Rijen per 14d |
|------|----------|---------------|
| `daily_activity_stats` | #1-12, #15-16 | ~14 rijen |
| `room_activity_hourly` | #14, #17 | ~300-700 rijen |

Features #3, #6-8, #13, #18 worden client-side berekend uit bovenstaande data.

---

## Feature Berekeningen

### Dagdeel events (features #6-8)

Berekend uit de `events_per_hour` array:

```javascript
function sumEventsInRange(eventsPerHour, startHour, endHour) {
  let sum = 0
  for (let h = startHour; h <= endHour; h++) {
    sum += eventsPerHour[h] || 0
  }
  return sum
}

morning_events   = sumEventsInRange(events_per_hour, 6, 11)   // 06:00-12:00
afternoon_events = sumEventsInRange(events_per_hour, 12, 17)  // 12:00-18:00
evening_events   = sumEventsInRange(events_per_hour, 18, 22)  // 18:00-23:00
```

### Wakkere duur (feature #3)

```javascript
awake_duration = timeToMinutes(last_activity) - timeToMinutes(first_activity)
```

### Kamer ratio (feature #13)

```javascript
room_ratio = rooms_active / rooms_available  // 0-1 range
```

### Hoofdkamer percentage (feature #14)

Berekend uit `room_activity_hourly` per dag:

```javascript
function computeMainRoomPct(roomHourlyData) {
  // Sommeer total_events per room_name voor de dag
  // Return: max(room_total) / sum(all_totals) * 100
}
```

### Kamerwisselingen (feature #17)

Telt hoeveel keer per uur de "dominante kamer" wisselt:

```javascript
function computeTransitionCount(roomHourlyData) {
  // 1. Groepeer per uur
  // 2. Per uur: bepaal dominante kamer (meeste events)
  // 3. Tel wisselingen tussen opeenvolgende uren
}
```

### Regelmaat score (feature #18)

Cosine similarity tussen vandaag's `events_per_hour` patroon en het gemiddelde baseline patroon:

```javascript
function cosineSimilarity(a, b) {
  // dot(a, b) / (|a| * |b|)
  // Returns 0-1, waar 1 = identiek patroon
}
```

---

## Dagstart Detectie

De "opstaantijd" wordt niet simpelweg bepaald door het eerste event, maar door een **cluster-detectie** algoritme:

```javascript
function calculateDayStart(eventsPerHour) {
  // Zoek eerste uur na 05:00 met >= 2 events
  // en vervolgactiviteit binnen 2 uur
  // Fallback: eerste uur met activiteit na 05:00
}
```

**Waarom cluster-detectie?** Een enkel nacht-event (bijv. toiletbezoek om 04:00) moet niet als "opgestaan" geteld worden.

---

## Database Tabellen

### `daily_activity_stats` (primaire bron)

```sql
CREATE TABLE daily_activity_stats (
    config_id             UUID REFERENCES hue_config(id),
    date                  DATE NOT NULL,
    first_activity        TIME,
    last_activity         TIME,
    total_events          INTEGER,
    events_per_hour       INTEGER[24],
    active_hours          INTEGER,
    rooms_active          INTEGER,
    rooms_available       INTEGER,
    longest_gap_minutes   INTEGER,
    night_events          INTEGER,
    night_active_hours    INTEGER,
    motion_events         INTEGER,          -- Migratie 020
    door_events           INTEGER,          -- Migratie 020
    UNIQUE(config_id, date)
);
```

### `room_activity_hourly` (ruimte-features)

```sql
CREATE TABLE room_activity_hourly (
    config_id       UUID REFERENCES hue_config(id),
    room_name       TEXT,
    hour            TIMESTAMPTZ,
    motion_events   INTEGER,
    door_events     INTEGER,
    total_events    INTEGER,
    UNIQUE(config_id, room_name, hour)
);
```

---

## Implementatie Locaties

### Frontend (gerustthuis-portaal)

| Component | Locatie | Beschrijving |
|-----------|---------|--------------|
| **Analyse.vue** | `src/views/Analyse.vue` | Z-score anomaly detection met 18 features in 6 groepen. Developer view met gegroepeerde score breakdown, baseline statistieken, data quality check, events per uur bar chart, en raw data JSON view. |
| **Patronen.vue** | `src/views/Patronen.vue` | Gebruikersvriendelijke patroonanalyse: dagritme, vandaag vs normaal (5 metrics met severity badges), weekpatroon, trends (sparklines). |
| **Dashboard.vue** | `src/views/Dashboard.vue` | Status banner met z-score-gebaseerde status detectie en rolling vergelijking tot huidig uur. |
| **useDataQuality.js** | `src/composables/useDataQuality.js` | Gedeelde utilities: `calculateDayStart()`, `getDayEvents()`, `getDayEventsUntilHour()`, `getActiveDayHours()`, `getActiveDayHoursUntilHour()`, `isNightHour()`, `formatMinutesToTime()`, `timeToMinutes()`, `toLocalDateKey()`, `avg()`, `stddev()`, `sumEventsInRange()`, `cosineSimilarity()`, `awakeDuration()`. Constanten: `MINIMUM_DAYS_REQUIRED`, `DAY_START_HOUR`, `NIGHT_START_HOUR`, `NIGHT_END_HOUR`. |

---

## Toekomstige Verbeteringen

1. **Weekdag-aware baseline**: Aparte verwachtingen voor werkdagen vs weekend
2. **Seizoensaanpassing**: Zomer/winter patronen (licht/donker)
3. **Trend detectie**: Geleidelijke veranderingen over weken signaleren
4. **Alert systeem**: Email/push notificaties bij afwijkingen
5. **Percentiel ranges**: p5-p95 berekening als alternatief voor z-scores
