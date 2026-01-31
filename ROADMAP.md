# GerustThuis Roadmap

Geplande features en verbeteringen.

---

## Prioriteit: Hoog

### 1. Auto-Refresh Dashboard

**Status:** Nog niet geïmplementeerd
**Impact:** Gebruikers zien verouderde data

**Probleem:**
Dashboard laadt data één keer bij mount en ververst nooit.

**Oplossing:**
```javascript
// Dashboard.vue
let refreshInterval = null

onMounted(async () => {
  await refreshAllData()
  refreshInterval = setInterval(refreshAllData, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
```

**Onderdelen:**
- [ ] Polling interval (5 min) toevoegen
- [ ] Handmatige refresh knop
- [ ] "Laatste update: X min geleden" indicator
- [ ] Loading state tijdens refresh

**Alternatief:** Supabase Realtime subscriptions (vereist Realtime inschakelen)

---

### 2. Multi-tenant RLS Policies

**Status:** Security issue - alle users zien alle data
**Impact:** Privacy risico bij meerdere gebruikers

**Huidige situatie:**
```sql
-- Alle authenticated users kunnen alles zien
USING (true)
```

**Gewenste situatie:**
```sql
-- Users zien alleen eigen data
USING (config_id IN (
  SELECT hc.id FROM hue_config hc
  WHERE hc.user_email = auth.jwt()->>'email'
))
```

**Onderdelen:**
- [ ] RLS policies updaten voor hue_devices
- [ ] RLS policies updaten voor physical_devices
- [ ] RLS policies updaten voor raw_events
- [ ] RLS policies updaten voor room_activity_hourly
- [ ] Testen met meerdere accounts

---

## Prioriteit: Medium

### 3. Placeholder Views Invullen

**Status.vue - Real-time Status**
- [ ] Laatste activiteit per kamer
- [ ] Huidige sensor states (motion, deuren)
- [ ] Lampen die aan staan
- [ ] Batterij waarschuwingen

**Woning.vue - Configuratie**
- [ ] Kamers beheren (namen, verdiepingen)
- [ ] Sensoren toewijzen aan kamers
- [ ] Device hernoemen
- [ ] Inactieve devices verbergen

**Patronen.vue - Afwijkingsdetectie**
- [ ] Dagpatroon visualisatie (normaal vs vandaag)
- [ ] Z-score berekening voor afwijkingen
- [ ] Alert configuratie (geen beweging > X uur)
- [ ] Historische vergelijking (week/maand)

---

### 4. Low Battery Notificaties

**Status:** Battery wordt gepolled, maar geen alerting
**Impact:** Gebruikers merken lege batterijen te laat

**Onderdelen:**
- [ ] Alert tabel toevoegen voor batterij waarschuwingen
- [ ] Threshold configureerbaar (default: 20%)
- [ ] UI indicator voor low battery devices
- [ ] Email notificatie (optioneel)

---

### 5. Event Retentie Verduidelijken

**Status:** Cleanup is 90 dagen, maar draait wekelijks
**Impact:** Events kunnen 90-97 dagen oud zijn

**Opties:**
1. Dagelijkse cleanup (consistent 90 dagen)
2. Documentatie updaten (90-97 dagen)
3. Configureerbare retentie periode

---

## Prioriteit: Laag

### 6. Real-time Subscriptions

**Status:** Niet geïmplementeerd
**Impact:** Zou polling kunnen vervangen

**Voordelen:**
- Instant updates bij state changes
- Minder database load dan polling
- Betere UX

**Nadelen:**
- Vereist Supabase Realtime (extra kosten)
- Complexere error handling
- Fallback naar polling nodig

**Implementatie:**
```javascript
const channel = supabase
  .channel('room-activity')
  .on('postgres_changes',
    { event: 'INSERT', schema: 'public', table: 'room_activity_hourly' },
    () => loadHeatmapData()
  )
  .subscribe()
```

---

### 7. gerustthuis-cloud Migratie

**Status:** Code in cloud die niet in portaal zit
**Impact:** Waardevolle features niet beschikbaar

**Te migreren:**
- [ ] Patronen.vue (15-dimensionale anomalie detectie)
- [ ] Alert systeem (4 types + quiet hours)
- [ ] Pro Dashboard (zorginstellingen)
- [ ] Bewoners beheer
- [ ] Contact sensoren v2 API support

**Aanpak:**
1. Feature-by-feature migreren
2. Database schema uitbreiden waar nodig
3. Testen met bestaande data

---

## Backlog

- [ ] PWA support (offline viewing)
- [ ] Dark mode
- [ ] Multi-language (EN/DE)
- [ ] Export naar CSV/PDF
- [ ] Historische trends (maand/jaar view)
- [ ] Vergelijking met vorige week
- [ ] Push notificaties (browser)
- [ ] 2FA voor login
- [ ] Audit log voor data access

---

## Changelog

### v0.1.0 (Huidig)
- Basis dashboard met heatmap
- Hue OAuth integratie
- Sensor health monitoring
- 7-dagen activiteit overzicht
