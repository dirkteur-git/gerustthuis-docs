# ADR-004: Privacy-first ontwerp

**Status:** Geaccepteerd
**Datum:** 2024
**Auteur:** Dirk Bakker

---

## Context

GerustThuis monitort het gedrag van ouderen in hun eigen huis. Dit is gevoelige persoonsdata. Verkeerd omgaan met deze data:
- Schaadt het vertrouwen van gebruikers en bewoners
- Creëert juridische risico's onder AVG/GDPR
- Kan leiden tot ongewenste surveillance van kwetsbare mensen

De bewoner (de oudere) is bewust niet de primaire gebruiker van de app — de mantelzorger is dat. De bewoner heeft geen account en ziet geen data. Dat is een bewuste keuze.

---

## Kernbeslissingen

### 1. Geen camera's of microfoons

GerustThuis gebruikt uitsluitend bewegings- en contactsensoren. Geen beeldmateriaal, geen geluid.

**Reden:** Camera's zijn voor bewoners onaanvaardbaar invasief, juridisch complex (AVG Art. 9), en niet nodig voor het doel (activiteitspatroon detecteren).

### 2. Patronen ipv exacte tijdstippen

De app toont **dagdelen** (ochtend / middag / avond / nacht), nooit exacte tijdstippen.

**Voorbeeld:**
- ✓ "Ochtend: actief"
- ✗ "Opgestaan om 07:23"

**Reden:** Exacte tijdstippen zijn niet nodig voor het doel (gerustgesteld worden). Ze voelen als surveillance. Het beperkt ook het nut van eventuele datalekken.

**Technische implementatie:** `daily_activity_stats` en `room_activity_hourly` slaan aggregaties op, geen ruwe events. De app query't alleen deze tabellen.

### 3. Data-isolatie per huishouden via RLS

Alle data is gekoppeld aan een `household_config_id`. Row Level Security op PostgreSQL-niveau zorgt dat gebruiker A nooit data van gebruiker B kan zien — ook al maakt een bug de applicatielaag kwetsbaar.

**Implementatie:** `get_accessible_config_ids()` (SECURITY DEFINER) als centrale RLS-functie. Alle tabellen in `activity.*` en `integrations.*` gebruiken deze functie in hun policies.

### 4. Bewoner heeft geen account

De bewoner is bewust buiten het digitale systeem gehouden. Zijn/haar naam en relatie staan in `public.residents`, maar er is geen auth-account, geen login, geen notificaties.

**Reden:** De bewoner heeft toestemming gegeven voor monitoring, maar wordt niet actief betrokken in de digitale flow. Dit vermindert cognitieve belasting en voorkomt dat de bewoner zich bewaakt voelt.

### 5. Minimale data-retentie

| Data | Bewaartermijn | Locatie |
|------|---------------|---------|
| Ruwe sensor events (`activity_events`) | 90 dagen | Supabase cloud |
| 5-min aggregaties (`room_activity`) | 30 dagen | Supabase cloud |
| Uurlijkse aggregaties (`room_activity_hourly`) | 1 jaar | Supabase cloud |
| Dagelijkse stats (`daily_activity_stats`) | Onbepaald (klein formaat) | Supabase cloud |

> **Toekomstig (lokale gateway):** Ruwe events blijven op de Raspberry Pi (14 dagen), alleen aggregaties gaan naar de cloud. Zie [ADR-003](ADR-003-hue-first-extensible.md).

---

## Juridisch kader (AVG)

| Verplichting | Hoe voldaan |
|-------------|-------------|
| Rechtmatige grondslag | Toestemming van bewoner (mondeling + via mantelzorger) |
| Dataminimalisatie | Alleen aggregaties in cloud, geen camera/audio |
| Transparantie | Privacyverklaring op website, uitleg in app |
| Beveiliging | RLS, Supabase Auth, HTTPS, geen plain-text credentials |
| Verwerkersovereenkomst | Supabase DPA ondertekenen (Fase 0 actie) |

---

## Gevolgen

**Positief:**
- Vertrouwen van gebruikers — "geen camera's" is de sterkste marketingboodschap
- Juridisch veilig — AVG-compliant door ontwerp
- Eenvoudigere UX — mantelzorger hoeft niet door exacte logs te scrollen

**Negatief / risico:**
- Minder granulariteit voor alerts: "geen activiteit in ochtend" ipv "geen beweging tussen 07:00-07:30"
  - Acceptabel: het doel is geruststelling, niet surveillance
- Edge case: bewoner slaapt ongewoon lang → alert is vertraagd door aggregatie
  - Mitigatie: realtime alert op langdurige inactiviteit (toekomstige feature) — zonder exacte tijdstip te tonen

**Principe:** Bij twijfel kiezen we voor meer privacy, niet meer data.
