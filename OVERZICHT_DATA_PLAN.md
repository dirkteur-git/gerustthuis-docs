# Overzicht Scherm — Data Plan

> Status: **Placeholders actief** — echte data-integratie nog te doen.
> Bewoner naam, Hue Bridge en auth zijn al live.

---

## Componenten & benodigde data

### 1. `StatusBanner` — "Alles goed / Aandacht / Kritiek"

| Veld | Type | Bron | Status |
|------|------|------|--------|
| `status` | `'goed' \| 'aandacht' \| 'kritiek'` | `daily_activity_stats.anomaly_score` | ❌ Hardcoded `'goed'` |
| `label` | string | Afgeleid van status | ❌ Hardcoded `'Alles goed'` |
| `residentName` | string | `residents` via store | ✅ Live |
| `datum` | string | `date-fns` client-side | ✅ Live |

**Algoritme nodig:**
```
anomaly_score < 0.3  → status = 'goed',     label = 'Alles goed'
anomaly_score < 0.6  → status = 'aandacht', label = 'Aandacht gevraagd'
anomaly_score >= 0.6 → status = 'kritiek',  label = 'Actie vereist'
```

**Query:**
```sql
SELECT anomaly_score
FROM daily_activity_stats
WHERE config_id = :configId AND stat_date = CURRENT_DATE
LIMIT 1
```

---

### 2. `AISummary` — Dagelijkse samenvatting

| Veld | Type | Bron | Status |
|------|------|------|--------|
| `intro` | string | Template op basis van `daily_activity_stats` | ⚠️ Naam live, tekst placeholder |
| `bullets[0]` | string | Ochtend-activiteit uit `activity_events` | ❌ Placeholder |
| `bullets[1]` | string | Middag/avond-activiteit uit `activity_events` | ❌ Placeholder |

**Template intro (geen LLM nodig):**
```typescript
// Varianten op basis van anomaly_score + active_hours
'[Naam] had een rustige maar actieve dag.'       // normaal
'[Naam] was vandaag minder actief dan normaal.'  // lage activiteit
'[Naam] had een drukke dag met veel beweging.'   // hoge activiteit
'Het is een rustige dag voor [Naam].'            // nacht / vroege ochtend
```

**Bullet template:**
```typescript
// bullet 0 — ochtendactiviteit
`Vanmorgen ${verb} in de ${kamer}.`
// → verb: "actief geweest", "opgestaan en rondgelopen"
// → kamer: meest actieve zone 06:00–12:00 uit activity_events

// bullet 1 — middag/avond
`Vanmiddag ${beweging} door ${kamers}.`
// → kamers: top 2 zones 12:00–18:00 uit activity_events
```

**Queries:**
```sql
-- Ochtendactiviteit (top zone 06:00–12:00)
SELECT zone_id, COUNT(*) as events
FROM activity_events
WHERE config_id = :configId
  AND created_at::date = CURRENT_DATE
  AND EXTRACT(hour FROM created_at) BETWEEN 6 AND 11
GROUP BY zone_id ORDER BY events DESC LIMIT 1

-- Middag (top 2 zones 12:00–18:00)
SELECT zone_id, COUNT(*) as events
FROM activity_events
WHERE config_id = :configId
  AND created_at::date = CURRENT_DATE
  AND EXTRACT(hour FROM created_at) BETWEEN 12 AND 17
GROUP BY zone_id ORDER BY events DESC LIMIT 2
```

---

### 3. `StatsRow` — Actieve uren / Kamers actief / Weekgemiddelde

| Veld | Type | Bron | Status |
|------|------|------|--------|
| `activeHours` | number | `daily_activity_stats.active_hours` | ❌ Mock (9) |
| `activeRooms` | number | `daily_activity_stats.rooms_active` | ❌ Mock (4) |
| `weekAvgHours` | number | avg(`active_hours`) afgelopen 7 dagen | ❌ Mock (8) |

**Query:**
```sql
-- Vandaag
SELECT active_hours, rooms_active
FROM daily_activity_stats
WHERE config_id = :configId AND stat_date = CURRENT_DATE

-- Weekgemiddelde
SELECT ROUND(AVG(active_hours), 1) as week_avg
FROM daily_activity_stats
WHERE config_id = :configId
  AND stat_date >= CURRENT_DATE - INTERVAL '7 days'
```

---

### 4. `WeekOverview` — 7-daags statusoverzicht

| Veld | Type | Bron | Status |
|------|------|------|--------|
| `days[].label` | string | `Ma/Di/Wo/Do/Vr/Za/Zo` client-side | ✅ Live (statisch) |
| `days[].status` | `'goed' \| 'aandacht' \| 'kritiek' \| 'geen-data'` | `daily_activity_stats.anomaly_score` per dag | ❌ Mock |
| `days[].isToday` | boolean | Client-side datum check | ✅ Live (statisch) |

**Query:**
```sql
SELECT stat_date, anomaly_score
FROM daily_activity_stats
WHERE config_id = :configId
  AND stat_date >= CURRENT_DATE - INTERVAL '6 days'
ORDER BY stat_date ASC
```

**Algoritme:** zelfde als StatusBanner (anomaly_score → goed/aandacht/kritiek).
Ontbrekende dagen → `'geen-data'`.

---

## Implementatie volgorde

1. **Stap 1** — `StatsRow` vullen
   - Eenvoudigste query, minste logica
   - Bouw `getStatsToday(configId)` in `queries.ts`

2. **Stap 2** — `WeekOverview` vullen
   - 7 rijen uit `daily_activity_stats`
   - Bouw `getWeekOverview(configId)` in `queries.ts`

3. **Stap 3** — `StatusBanner` vullen
   - Hergebruik data van stap 1 (zelfde rij)
   - Voeg `anomaly_score` toe aan stap 1 query

4. **Stap 4** — `AISummary` vullen
   - Meeste logica, template-based
   - Bouw `getDayActivitySummary(configId)` in `queries.ts`
   - Vertaal zones naar leesbare kamernamen via `hue_devices.name`

---

## Nieuwe bestanden nodig

| Bestand | Inhoud |
|---------|--------|
| `src/services/queries.ts` | Alle Supabase queries gegroepeerd |
| `src/stores/appStore.ts` | Zustand store voor schermdata (vervangt mock) |
| `src/hooks/useRefreshInterval.ts` | 5-min auto-refresh voor status |

---

## Zones → kamernamen

De `activity_events` en `room_activity_hourly` tabellen gebruiken `zone_id` (UUID).
Voor leesbare namen in bullets: join met `hue_devices`:

```sql
SELECT hd.name as zone_name, COUNT(ae.id) as events
FROM activity_events ae
JOIN hue_devices hd ON hd.id = ae.zone_id
WHERE ae.config_id = :configId
  AND ae.created_at::date = CURRENT_DATE
GROUP BY hd.name
ORDER BY events DESC
```

---

## Placeholder teksten (huidig)

De volgende teksten zijn **tijdelijk hardcoded** en moeten vervangen worden:

| Component | Huidige placeholder | Vervangen door |
|-----------|--------------------|-|
| `StatusBanner.status` | `'goed'` | `anomaly_score` berekening |
| `StatusBanner.label` | `'Alles goed'` | Dynamisch label |
| `AISummary.intro` | `[Naam] had een rustige maar actieve dag.` | Template op basis van stats |
| `AISummary.bullets[0]` | `Vanmorgen vroeg opgestaan en actief in de keuken` | Echte zone-activiteit ochtend |
| `AISummary.bullets[1]` | `Vanmiddag bewogen door woonkamer en slaapkamer` | Echte zone-activiteit middag |
| `StatsRow.activeHours` | `9` | `daily_activity_stats.active_hours` |
| `StatsRow.activeRooms` | `4` | `daily_activity_stats.rooms_active` |
| `StatsRow.weekAvgHours` | `8` | Gemiddelde afgelopen 7 dagen |
| `WeekOverview.days[*].status` | Mock statusreeks | `daily_activity_stats` per dag |
