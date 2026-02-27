# GerustThuis App — Content Spec & Schermkaart

> Dit is het "contract": welke schermen zijn er, wat staat erin, welke acties kan een gebruiker doen.
> Gebruik dit als basis voor UI-beslissingen, mockups en data-integratie.
> Laatste update: 2026-02-26

---

## 1. Schermkaart & Navigatie

```
[Login] ──────────────────────────────────────────────────────┐
  │  register / forgot password                               │
  ▼                                                          │
[Setup: Welcome]                                             │
  │ "Aan de slag"                                            │
  ▼                                                          │
[Setup: Wie ben ik] (stap 1/4)                               │
  │ opslaan of sla over                                      │
  ▼                                                          │
[Setup: Voor wie] (stap 2/4)                                 │
  │ opslaan of sla over                                      │
  ▼                                                          │
[Setup: Connect Hue] (stap 3/4)                              │
  │ verbinden of overslaan                                   │
  ▼                                                          │
[Setup: Learning] (stap 4/4)                                 │
  │ "Naar het dashboard" → setup_completed = true            │
  ▼                                                          │
[Dashboard] ← ─────────────────────────────────────────────┘
  │
  ├── Tab 1: [Overzicht]
  ├── Tab 2: [Familie]
  ├── Tab 3: [Meldingen]
  └── Tab 4: [Instellingen]
              │
              └── Uitloggen → [Login]
```

**Terugnavigatie:** Setup-schermen hebben een "← Terug" of "Sla over" link.
**Deep links (toekomst):** Push-notificatie → direct naar Meldingen detail.

---

## 2. Login & Registratie

### Schermen
| Scherm | Route | Beschrijving |
|--------|-------|-------------|
| Login | `/login` | Inloggen + registreren (tabs), wachtwoord vergeten |

### Content
| Element | Waarden / Gedrag |
|---------|-----------------|
| Tab toggle | `Inloggen` / `Registreren` |
| E-mail input | Vrij tekst, type=email |
| Wachtwoord input | Vrij tekst, type=password, min 6 tekens |
| Foutmeldingen | Vertaald NL (zie tabel hieronder) |
| Succes-bericht | "Controleer je e-mail om je account te bevestigen." |
| Wachtwoord vergeten | Aparte view in zelfde scherm, stuurt reset-email |

**Foutmeldingen vertaling:**
| Supabase fout | NL tekst |
|--------------|---------|
| Invalid login credentials | Onjuist e-mailadres of wachtwoord. |
| Email not confirmed | Bevestig je e-mail voor je kunt inloggen. |
| User already registered | Dit e-mailadres is al geregistreerd. |

### Acties
- Inloggen
- Registreren (→ bevestigingsmail)
- Wachtwoord vergeten (→ reset-email)

---

## 3. Setup Flow

### Scherm 3.1 — Welcome (`/setup/welcome`)
**Doel:** Eerste indruk, uitleg wat de app doet.

| Element | Inhoud |
|---------|--------|
| Koptekst | "Welkom bij GerustThuis" |
| Subtitel | "Gerust zijn over je naaste. Zonder camera's, zonder tijdstippen — alleen rust." |
| Feature list | 3 punten: Privacy-first / Meldingen alleen als nodig / Deel met familie |
| Knop | "Aan de slag" |

---

### Scherm 3.2 — Wie ben ik (`/setup/wie-ben-ik`, stap 1/4)
**Doel:** Mantelzorger legt vast hoe de app hem aanspreekt.

| Element | Inhoud |
|---------|--------|
| Vraag | "En jij bent...?" |
| Input | Vrije naam, bijv. "Jan", "Sophie", "Dirkjan" |
| Preview | "Jij bent [naam]" |
| Opslaan naar | `user_profiles.display_name` |
| Skip optie | "Sla over — ik stel dit later in" |

---

### Scherm 3.3 — Voor wie (`/setup/bewoner`, stap 2/4)
**Doel:** Vastleggen voor wie de mantelzorger zorgt.

| Element | Inhoud |
|---------|--------|
| Vraag | "Voor wie zorg jij?" |
| Relatie-picker | Oma / Opa / Mama / Pappa / Partner / Anders... |
| Anders-veld | Vrije tekst, bijv. "Vader", "Tante Riet", "Lieve buurman" |
| Naam-input | Optioneel, bijv. "Marie", "Janssen" |
| Preview | "Je zorgt voor [Oma Janssen]" |
| Opslaan naar | `residents` tabel (household_id, relationship, first_name) |
| Skip optie | "Sla over — ik stel dit later in" |

**Meerdere bewoners:** Ondersteund in de setup flow. Gebruiker kan meerdere bewoners toevoegen via "Toevoegen" → lijst opbouwt zich. Daarna via Instellingen uitbreiden.

---

### Scherm 3.4 — Connect Hue (`/setup/connect`, stap 3/4)
**Doel:** Philips Hue Bridge koppelen.

| Element | Inhoud |
|---------|--------|
| Uitleg | Stappen: druk knop op Bridge → klik Verbinden → autoriseer |
| Status | Verbonden (groen) / Niet verbonden |
| Knop | "Verbinden" (→ OAuth flow, toekomst) |
| Skip optie | "Overslaan (later instellen)" |

**OAuth-flow:** Al geïmplementeerd in het portaal (`HueConnect.vue`, `HueCallback.vue`, Edge Function `hue-token-exchange`). Voor de app: zelfde flow hergebruiken, `redirect_uri` aanpassen naar app URL.

---

### Scherm 3.5 — Learning (`/setup/learning`, stap 4/4)
**Doel:** Uitleggen dat de app eerst 14 dagen leert.

| Element | Inhoud |
|---------|--------|
| Koptekst | "Leerperiode loopt" |
| Uitleg | "GerustThuis leert het normale dagpatroon. Dit duurt 14 dagen — na 30 dagen is de detectie heel betrouwbaar." |
| Progress bar | Dag X van 14 (later: uit `hue_config.created_at` berekend) |
| Checklist | Sensoren actief / X van 14 dagen data / Basispatroon bepaald / Detectie actief |
| Knop | "Naar het dashboard" → `setup_completed = true` |

---

## 4. Tab 1 — Overzicht

**Doel:** In één oogopslag weten hoe het gaat met je naaste.

### 4.1 StatusBanner
| Element | Mogelijke waarden | Databron |
|---------|------------------|---------|
| Status-kleur | Groen (goed) / Amber (aandacht) / Rood (kritiek) | `daily_activity_stats.anomaly_score` |
| Label | "Alles goed" / "Aandacht gevraagd" / "Actie vereist" | Afgeleid van score |
| Bewonernaam | "Oma" / "Oma en Opa" (kort) | `residents` via store |
| Datum | "donderdag 26 februari" | Client-side date-fns |

**Status-algoritme:**
```
anomaly_score < 0.3  → goed     "Alles goed"
anomaly_score < 0.6  → aandacht "Aandacht gevraagd"
anomaly_score >= 0.6 → kritiek  "Actie vereist"
geen data vandaag    → goed     "Geen data vandaag"
```

---

### 4.2 AISummary
| Element | Inhoud | Databron |
|---------|--------|---------|
| Intro | "[Naam] had een [beschrijving] dag." | Template op basis van stats |
| Bullet 1 | Ochtendactiviteit, bijv. "Vanmorgen vroeg actief in de keuken" | `activity_events` 06:00–12:00 |
| Bullet 2 | Middag/avond, bijv. "Vanmiddag bewogen door woonkamer" | `activity_events` 12:00–18:00 |

**Intro-varianten (template, geen LLM):**
```
normaal:          "[Naam] had een rustige maar actieve dag."
weinig actief:    "[Naam] was vandaag wat minder actief dan normaal."
heel actief:      "[Naam] had een drukke dag met veel beweging."
vroege ochtend:   "Het is nog vroeg — [Naam] is net opgestaan."
nacht:            "[Naam] slaapt — alles rustig."
geen data:        "Nog niet genoeg data voor een samenvatting."
```

---

### 4.3 StatsRow
| Stat | Label | Eenheid | Databron |
|------|-------|---------|---------|
| Actieve uren | "Actieve uren" | uur (u) | `daily_activity_stats.active_hours` |
| Kamers actief | "Kamers actief" | getal | `daily_activity_stats.rooms_active` |
| Weekgemiddelde | "Weekgemiddelde" | uur (u) | avg `active_hours` laatste 7 dagen |

---

### 4.4 WeekOverview
7 gekleurde blokjes, één per dag (Ma t/m Zo).

| Element | Waarden |
|---------|---------|
| Kleur per dag | Groen / Amber / Rood / Grijs (geen data) |
| Vandaag | Ring om het blokje |
| Label | "Ma", "Di", ... "Zo" |
| Databron | `daily_activity_stats` laatste 7 rijen |

---

## 5. Tab 2 — Familie

**Doel:** Wie zorgen er mee, en een gedeeld berichtenbord.

### 5.1 ResidentBanner
| Element | Inhoud | Databron |
|---------|--------|---------|
| Label | "Zorg voor" | Statisch |
| Naam | "Oma Janssen" / "Oma en Opa" (volledig) | `residents` via store |

### 5.2 Familieleden
| Element | Inhoud | Databron |
|---------|--------|---------|
| Naam | Weergavenaam | `user_profiles.display_name` |
| Rol | "Beheerder" / "Kijker" | `household_members.role` |
| Laatste actief | "Gisteren", "2 uur geleden" | `auth.users.last_sign_in_at` (toekomst) |
| Jij-indicator | "(jij)" achter eigen naam | `authStore.user.id === member.id` |
| Uitnodigen | Knop → stuurt invite email (toekomst) | `household_members` INSERT |

**Rollen:**
| Rol | Rechten |
|-----|---------|
| `admin` | Alles: instellingen, bewoners, leden beheren |
| `viewer` | Alleen lezen: overzicht, meldingen, familiebord |

### 5.3 Familiebord
| Element | Inhoud | Databron |
|---------|--------|---------|
| Berichten | Tekst + auteur + timestamp | `family_board_messages` (tabel nog aan te maken) |
| Eigen berichten | Rechts uitgelijnd, groen | `user_id = currentUser.id` |
| Andermans berichten | Links, grijs + naam erboven | — |
| Input | Vrije tekst, max ~500 tekens | — |
| Realtime | Berichten verschijnen direct | Supabase Realtime |

---

## 6. Tab 3 — Meldingen

**Doel:** Overzicht van alle automatische meldingen over de bewoner.

### Meldingstypes
| Type | Kleur/icoon | Wanneer | Voorbeeld tekst |
|------|------------|---------|----------------|
| `goed` | Groen / Heart | Positieve afwijking | "Oma was vandaag extra actief" |
| `info` | Blauw / Info | Neutraal bericht | "Leerperiode bijna compleet" |
| `goedemorgen` | Sage / Sun | Ochtendactiviteit gedetecteerd | "Oma is opgestaan om 7:23" |
| `nacht` | Donkerblauw / Moon | Nachtelijke onrust | "Ongewone activiteit om 3:15" |
| `dagrapport` | Amber / BarChart | Dagelijkse samenvatting | "Dagrapport voor maandag" |
| `kritiek` | Rood / AlertCircle | Geen activiteit gedetecteerd | "Geen beweging in 6 uur" |

### Melding-structuur
| Veld | Type | Inhoud |
|------|------|--------|
| `type` | enum | Zie types hierboven |
| `title` | string | Korte koptekst |
| `description` | string? | Optionele toelichting |
| `is_read` | boolean | Gelezen of niet |
| `created_at` | timestamp | Tijdstip van de melding |

### Acties
- Tik op melding → mark as read (+ detail tonen, toekomst)
- "Alles gelezen" knop → bulk mark as read
- Realtime: nieuwe meldingen verschijnen boven aan de lijst

---

## 7. Tab 4 — Instellingen

**Doel:** Account, Bridge en notificatie-voorkeuren beheren.

### 7.1 Account
| Element | Inhoud | Databron |
|---------|--------|---------|
| E-mailadres | Weergave (niet wijzigbaar hier) | `auth.users.email` |
| Naam wijzigen | (toekomst) Aparte flow | `user_profiles.display_name` |

### 7.2 Bewoners beheren *(toekomst)*
| Actie | Beschrijving |
|-------|-------------|
| Bewoner toevoegen | Tweede bewoner, zelfde flow als setup stap 2 |
| Bewoner bewerken | Naam of relatie aanpassen |
| Bewoner verwijderen | Met bevestigingsdialoog |

### 7.3 Hue Bridge
| Element | Inhoud | Databron |
|---------|--------|---------|
| Status | "Verbonden" (groen) / niet verbonden | `hue_config.status = 'active'` |
| Bridge naam | "Hue Bridge BSB002" | `hue_config.bridge_id` |
| Apparaten | "14 apparaten actief" | COUNT `hue_devices` |
| Verbinding beheren | → nieuwe OAuth-flow (toekomst) | — |
| Zones & kamers | → sensoren toewijzen (toekomst) | `hue_devices` |
| MotionAware | → bewegingsgevoeligheid (toekomst) | `hue_config` settings |

### 7.4 Meldingen (toggles)
| Toggle | Label | Default | Databron |
|--------|-------|---------|---------|
| `dagelijksSamenvatting` | "Dagelijkse samenvatting" | Aan | `user_settings` tabel (nog te maken) |
| `kritiekeAlerts` | "Kritieke meldingen" | Aan | idem |
| `nachtelijkeActiviteit` | "Nachtelijke activiteit" | Uit | idem |

### 7.5 Abonnement *(toekomst)*
| Plan | Prijs | Features |
|------|-------|---------|
| Basis | Gratis | Standaard meldingen, 1 gebruiker |
| Plus | €60/jaar | Push-notificaties, patronen, meerdere familieleden |

### 7.6 Over
| Item | Actie |
|------|-------|
| Hulp & support | → externe link of in-app FAQ |
| Privacybeleid | → externe link |
| Uitloggen | → `supabase.auth.signOut()` → login scherm |

---

## 8. Ontbrekende schermen (toekomst)

| Scherm | Beschrijving | Prioriteit |
|--------|-------------|-----------|
| Melding detail | Uitgebreide weergave van één melding | Medium |
| Bewoner beheren | Bewoner toevoegen/bewerken vanuit Instellingen | Hoog |
| Familielid uitnodigen | E-mail uitnodigen voor huishouden | Medium |
| Profiel bewerken | Naam en avatar wijzigen | Laag |
| Hue OAuth flow | Bridge koppelen via Hue API | Hoog |
| Wachtwoord resetten | `/auth/reset-password` pagina | Hoog |
| Email bevestigen | `/auth/confirm` pagina | Hoog |

---

## 9. Globale UX-regels

| Regel | Detail |
|-------|--------|
| Geen scroll op tabs 1–3 | Content past op één scherm, Instellingen mag scrollen |
| Interne scroll toegestaan | Meldingen-lijst, Familiebord berichten |
| Geen lege schermen | Altijd een zinvolle lege staat (bijv. "Nog geen meldingen") |
| Foutmeldingen | Altijd in NL, nooit technisch jargon |
| Loading states | Spinner bij DB-laden, nooit lege witte vlakken |
| Datum/tijd | Altijd in NL locale via date-fns |
| Bewonernamen | Kort (Oma) in header/banner, Volledig (Oma Jenny) in tekst |
