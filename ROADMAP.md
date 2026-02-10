# GerustThuis Roadmap

Feature status en geplande verbeteringen.

---

## Afgerond

### Multi-tenant RLS Policies ✓
**Migraties:** 005, 007, 010-017
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
**Migraties:** 015-017
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

---

## Prioriteit: Hoog

### 1. Alert Systeem
- [ ] Inactiviteitsalarm (geen beweging > X uur)
- [ ] Nachtelijke onrust detectie
- [ ] Email/push notificaties
- [ ] Quiet hours configuratie

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

- [ ] PWA support (offline viewing)
- [ ] Export naar CSV/PDF
- [ ] Real-time Supabase subscriptions
- [ ] Push notificaties (browser)
- [ ] Seizoensaanpassing patroonherkenning
- [ ] Weekdag-aware baseline (werkdagen vs weekend)
- [ ] Trend detectie (geleidelijke veranderingen over weken)

---

## Changelog

### v0.3.0 (Huidig - feb 2026)
- Patronen pagina live (dagritme, trends, vergelijking)
- Household-based multi-tenancy
- Data pipeline fixes (migraties 015-017)
- Superadmin verwijderd (migratie 018)
- Auto-refresh op Dashboard (elke 5 minuten)

### v0.2.0 (jan 2026)
- Analyse pagina (Z-score anomaly detection)
- Daily activity stats aggregatie
- Hue OAuth integratie verbeterd

### v0.1.0 (dec 2025)
- Basis dashboard met heatmap
- Hue OAuth integratie
- Sensor health monitoring
