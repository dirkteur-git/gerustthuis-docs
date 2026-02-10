# GerustThuis Roadmap

Feature status en geplande verbeteringen.

---

## Afgerond

### Multi-tenant RLS Policies ✓
**Migraties:** 005, 007, 010-017
- Household-based multi-tenancy via `get_accessible_config_ids()`
- Elke user ziet alleen data van eigen huishouden
- Superadmin (dirk@boostix.nl) kan alle huishoudens bekijken

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

### Superadmin ✓
**Migratie:** 014
- dirk@boostix.nl als global admin
- Gebruikers tab in Instellingen (alle users/households)
- Household switcher

### Data Pipeline ✓
**Migraties:** 015-017
- Auto-link hue_config aan household via trigger
- room_activity_hourly en daily_activity_stats aggregatie
- Correcte RLS policies op alle tabellen

---

## Prioriteit: Hoog

### 1. Auto-Refresh Dashboard
Dashboard laadt data één keer bij mount. Toevoegen:
- [ ] Polling interval (5 min)
- [ ] Handmatige refresh knop
- [ ] "Laatste update: X min geleden" indicator

### 2. Alert Systeem
- [ ] Inactiviteitsalarm (geen beweging > X uur)
- [ ] Nachtelijke onrust detectie
- [ ] Email/push notificaties
- [ ] Quiet hours configuratie

---

## Prioriteit: Medium

### 3. Low Battery Notificaties
- [ ] Alert bij batterij < 20%
- [ ] UI indicator voor low battery devices
- [ ] Email notificatie (optioneel)

### 4. Woning.vue Uitbreiden
- [ ] Kamers beheren (namen, verdiepingen)
- [ ] Sensoren toewijzen aan kamers
- [ ] Device hernoemen
- [ ] Inactieve devices verbergen

---

## Backlog

- [ ] PWA support (offline viewing)
- [ ] Dark mode
- [ ] Export naar CSV/PDF
- [ ] Real-time Supabase subscriptions
- [ ] Push notificaties (browser)
- [ ] Seizoensaanpassing patroonherkenning

---

## Changelog

### v0.3.0 (Huidig - feb 2026)
- Patronen pagina live (dagritme, trends, vergelijking)
- Household-based multi-tenancy
- Superadmin functionaliteit
- Data pipeline fixes (migraties 015-017)

### v0.2.0 (jan 2026)
- Analyse pagina (Z-score anomaly detection)
- Daily activity stats aggregatie
- Hue OAuth integratie verbeterd

### v0.1.0 (dec 2025)
- Basis dashboard met heatmap
- Hue OAuth integratie
- Sensor health monitoring
