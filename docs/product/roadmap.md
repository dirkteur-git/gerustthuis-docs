# GerustThuis Roadmap

Feature status en geplande verbeteringen.

---

## Afgerond

### Multi-tenant RLS Policies ✓
**Migraties:** 005, 007, 010-018
- Household-based multi-tenancy via `get_accessible_config_ids()`
- Elke user ziet alleen data van eigen huishouden

### Patronen.vue ✓
**Status:** Live in productie
- Dagritme analyse (gemiddeld uurpatroon, opstaan/bedtijd)
- Vandaag vs normaal vergelijking (5 metrics met severity badges)
- Weekpatroon analyse (activiteit per weekdag)
- Trends (sparklines voor events, actieve uren, nachtactiviteit)

### Households & Multi-tenancy ✓
**Migraties:** 009-013
- User profiles met active_household_id
- Household members met roles (admin/viewer)
- Automatische household aanmaak bij signup
- Uitnodigingssysteem (AcceptInvitation.vue)

### Data Pipeline ✓
**Migraties:** 015-020
- Auto-link hue_config aan household via trigger
- room_activity_hourly en daily_activity_stats aggregatie
- Correcte RLS policies op alle tabellen

### Auto-Refresh Dashboard ✓
- Dashboard herlaadt alle data elke 5 minuten via `setInterval`
- Automatische cleanup bij unmount

### Superadmin verwijderd ✓
**Migratie:** 018
- Hardcoded dirk@boostix.nl logica verwijderd uit alle functies en policies
- `is_superadmin` kolom verwijderd van user_profiles
- Alle users gaan nu via standaard household-based access control

### Aggregatie Automatisering ✓
**Migratie:** 019
- pg_cron jobs voor automatische uurlijkse aggregatie
- `aggregate-hourly-activity` (room_activity → room_activity_hourly)
- `refresh-daily-stats` (herberekent daily_activity_stats)

### Sensor Type Tracking ✓
**Migratie:** 020
- motion_events en door_events kolommen op daily_activity_stats
- Onderscheid tussen bewegings- en deursensor events

### 18-Feature Anomaly Detection ✓
- Uitgebreid van 6 naar 18 features in 6 groepen
- Rolling vergelijking (vandaag tot huidig uur vs baseline)
- Z-score gebaseerde status banner op Dashboard

### PWA App ✓
- React + Vite + Tailwind PWA voor mantelzorgers (vervangt React Native)
- 4 tabs: Overzicht / Familie / Meldingen / Instellingen
- Privacy-first: geen exacte tijdstippen, alleen dagdelen
- Zie [APP_DESIGN.md](../design/app-design.md) voor volledig design

### Alert Systeem ✓ (in PWA)
- Meldingenfeed met dagsamenvattingen, ochtend- en nachtmeldingen
- Kritieke meldingen (geen activiteit), nachtelijke onrust
- Dagelijkse samenvatting (elke avond)
- Quiet hours configuratie via Instellingen tab
- Zie [APP_DESIGN.md §6](../design/app-design.md) voor meldingstypen en [docs/overview/alerts.md](../architecture/alerts.md)

---

## Prioriteit: Hoog

---

## Prioriteit: Medium

### 2. Low Battery Notificaties
- [ ] Alert bij batterij < 20%
- [ ] UI indicator voor low battery devices
- [ ] Email notificatie (optioneel)

### 3. Woning.vue Uitbreiden
- [ ] Kamers beheren (namen, verdiepingen)
- [ ] Sensoren toewijzen aan kamers
- [ ] Device hernoemen
- [ ] Inactieve devices verbergen

---

## Backlog

- [ ] Export naar CSV/PDF
- [ ] Real-time Supabase subscriptions
- [ ] Push notificaties (browser)
- [ ] Seizoensaanpassing patroonherkenning
- [ ] Weekdag-aware baseline (werkdagen vs weekend)
- [ ] Trend detectie (geleidelijke veranderingen over weken)

---

## Changelog

### Website Nuxt (feb 2026)
- Nieuwe marketing website live: Nuxt 3 SSG (`gerustthuis-website-nuxt`)
- Prijsmodel: Gratis (max 3 sensoren) / Plus (€5/mnd) / Compleet Pakket (€125 netto na terugkoop)
  - Compleet Pakket: GerustThuis hardware (€160) + installatie (€45) + jaar 1 Plus = €205 bruto, terugkoopgarantie 50% hardware (€80) → €125 netto
  - Installatie ALLEEN via Compleet Pakket (wij sourcen hardware) — géén standalone installatie op eigen hardware
- Founding deal: eerste 500 gebruikers betalen altijd de helft van de actuele Plus prijs (nu €2,50/mnd, lifelong)
- Friendship deal: 1 maand gratis per doorverwezen aanmelding
- Privacy/beveiliging pagina toegevoegd (AVG-compliant)
- Homepage vereenvoudigd: focus op emotionele story, hardware-secties verplaatst
- Stappenplan: Koppel sensoren → Systeem leert → Jij voelt je gerust
- Navigatie uitgebreid: Voor wie, Prijzen, beveiliging-link in footer

### v0.3.0 (Huidig - feb 2026)
- Patronen pagina live (dagritme, trends, vergelijking)
- Household-based multi-tenancy
- Data pipeline fixes (migraties 015-017)
- Superadmin verwijderd (migratie 018)
- Auto-refresh op Dashboard (elke 5 minuten)
- Aggregatie automatisering via pg_cron (migratie 019)
- Motion/door events tracking (migratie 020)
- 18-feature anomaly detection met rolling vergelijking
- PWA app (React + Vite + Tailwind, vervangt React Native)

### v0.2.0 (jan 2026)
- Analyse pagina (Z-score anomaly detection)
- Daily activity stats aggregatie
- Hue OAuth integratie verbeterd

### v0.1.0 (dec 2025)
- Basis dashboard met heatmap
- Hue OAuth integratie
- Sensor health monitoring
