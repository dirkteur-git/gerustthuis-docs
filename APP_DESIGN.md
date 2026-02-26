# GerustThuis App — Design Specificatie v1.0

**Februari 2026 — PWA (React + Vite + Tailwind)**

> Gebaseerd op de visuele mockups in `gerustthuis-app/assets/`. Dit document beschrijft alle schermen, componenten en interacties voor de nieuwe GerustThuis PWA.

---

## 0. Privacy-principe: Geen detailinformatie over de bewoner

De app is gebouwd voor **mantelzorgers**, niet voor surveillance. De bewoner verdient privacy. Daarom gelden de volgende regels voor alle schermen:

| Regel | Toelichting |
|-------|-------------|
| **Geen exacte tijdstippen** | Nooit "om 7:30" of "09:06". Gebruik dagdelen: "vanmorgen", "vanmiddag", "vanavond", "vannacht" |
| **Geen uurlijkse grafieken** | Activiteitsgrafiek toont dagdelen (ochtend/middag/avond/nacht), niet per uur |
| **Geen kamer-timestamps** | Kamers tonen alleen "Recent actief" / "Vandaag" / "Niet recent", geen minuten/uren |
| **Geen activiteitslog met tijden** | Recente activiteit toont globale patronen, geen exacte kloktijden |
| **Geen bewegingsdetails** | Nooit "Beweging gedetecteerd om..." — alleen "Er was activiteit vanmorgen" |
| **Warme taal** | Altijd vanuit zorgperspectief, nooit als bewakingssysteem |

> **Vuistregel:** Als een mantelzorger de informatie zou doorvertellen aan de bewoner, mag het niet voelen als "ik weet precies wat je doet en wanneer".

---

## 1. Data & Bronnen

Alle data in de app komt uit **Supabase** of wordt weergegeven als **placeholder** tijdens ontwikkeling.

| Component | Supabase bron | Placeholder |
|-----------|--------------|-------------|
| Statusbanner | `daily_activity_stats` → Z-score berekening | Hardcoded "Alles goed" |
| AI-samenvatting | `daily_activity_stats` + `room_activity_hourly` → samenvatting genereren | Statische voorbeeldtekst |
| Statistieken | `daily_activity_stats` (active_hours, rooms_active) | Vaste getallen |
| Activiteitsgrafiek | `room_activity_hourly` gegroepeerd op dagdeel | Statische staafjes |
| Kamers | `hue_devices` + `activity_events` (laatste activiteit) | 3 voorbeeldkamers |
| Recente activiteit | `activity_events` (gegroepeerd, geanonimiseerd) | 5 voorbeelditems |
| Weekoverzicht | `daily_activity_stats` (laatste 7 dagen) | 7 gekleurde blokjes |
| Familieleden | `household_members` + `user_profiles` | 3 voorbeeldleden |
| Familiebord | Nieuwe tabel `family_board_messages` (nog aan te maken) | 3 voorbeeldberichten |
| Meldingen | Nieuwe tabel `notifications` (nog aan te maken) | 5 voorbeeldmeldingen |
| Hue Bridge | `hue_config` | Placeholder "Niet verbonden" |
| Sensoren | `hue_devices` + `physical_devices` | Lege lijst |
| Instellingen | `localStorage` + eventueel `user_settings` tabel | Standaardwaarden |

> **Ontwikkelmodus:** Gebruik hardcoded placeholder data zodat de app volledig werkt zonder Supabase-verbinding. Schakel over naar echte queries wanneer de backend klaar is.

---

## 2. Technologie & Architectuur

| Onderdeel | Keuze |
|-----------|-------|
| **Framework** | React 19 + TypeScript |
| **Build** | Vite |
| **Styling** | Tailwind CSS |
| **Routing** | React Router (of TanStack Router) |
| **State** | Zustand |
| **Backend** | Supabase (Auth + Database + Realtime) |
| **Distributie** | PWA (Progressive Web App) |
| **Icons** | Lucide React |
| **Fonts** | DM Serif Display (koppen) + DM Sans (body) |
| **Datum** | date-fns (NL locale) |

### PWA Vereisten

- `manifest.json` met app-naam, iconen, kleuren
- Service Worker voor offline caching
- "Add to Home Screen" prompt op iOS/Android
- Standalone display mode (geen browser chrome)
- Portrait-only orientatie
- Push notifications via Web Push API

---

## 3. Navigatie

Bottom tab bar met 4 tabs, altijd zichtbaar:

| Tab | Label | Icoon | Route |
|-----|-------|-------|-------|
| 1 | **Overzicht** | `Home` (huis) | `/` |
| 2 | **Familie** | `Users` (personen) | `/familie` |
| 3 | **Meldingen** | `Bell` (bel) | `/meldingen` |
| 4 | **Instellingen** | `Settings` (tandwiel) | `/instellingen` |

### Tab bar styling

- Achtergrond: `#FDFCF7` (Cream) met top border `#E8E4DD`
- Actieve tab: tekst en icoon in Deep Sage `#3E6652`, bold label
- Inactieve tab: tekst en icoon in `#8A8A8A` (Ink Muted)
- Badge op Meldingen: ronde badge met count, achtergrond Amber `#D4944C`, witte tekst
- Hoogte: 64px, icoon 24px, label 11px

---

## 4. Scherm 1 — Overzicht (Home)

De hoofdpagina. Toont in één oogopslag hoe het gaat met de bewoner. Scrollbaar, mobile-first.

### 4.1 Header

- Titel: **"GerustThuis"** — gecentreerd, DM Serif Display, 20px
- Geen navigatie-elementen in header

### 4.2 Statusbanner

Bovenaan, volledige breedte card met afgeronde hoeken.

| Element | Detail |
|---------|--------|
| Achtergrond | Licht sage `#EBF5EF` (normaal), licht amber (waarschuwing), licht rood (aandacht) |
| Icoon links | Hart-icoon (Lucide `Heart`), Deep Sage |
| Titel | **"Alles goed"** / "Even opletten" / "Aandacht nodig" — DM Sans Semibold 18px |
| Subtitel | Naam bewoner, bijv. "Oma" — DM Sans Regular 14px, `#5A5A5A` |
| Rechts | Datum, bijv. "woensdag 25 februari" — DM Sans 13px, `#8A8A8A` |

**Statusvarianten:**

| Status | Achtergrond | Icoon kleur | Tekst |
|--------|-------------|-------------|-------|
| Normaal | `#EBF5EF` | `#3E6652` | "Alles goed" |
| Waarschuwing | `#FEF6EC` | `#D4944C` | "Even opletten" |
| Aandacht | `#FDECEB` | `#C4645A` | "Aandacht nodig" |

### 4.3 AI-samenvatting card

Witte card met subtiele border, direct onder statusbanner. **Geen exacte tijdstippen — alleen dagdelen en globale patronen.**

- **Intro tekst**: Natuurlijke, warme zin, bijv. *"Alles ziet er goed uit vandaag! Oma was actief in de woonkamer en keuken zoals gewoonlijk."*
- **Bulletpoints** (3-4 items): Elk met een sage-kleurig bullet-punt
  - *"Vanmorgen activiteit in de keuken"* (NIET: "om 7:30")
  - *"Actief in de woonkamer de hele ochtend"*
  - *"Meer beweging in de gang vandaag — misschien een wandeling?"*
- Tekst: DM Sans 15px, kleur `#2C2C2C`
- Tone of voice: warm, persoonlijk, niet-technisch (zie Brandbook)

> **Privacy:** Bulletpoints vermelden nooit exacte tijdstippen. Gebruik "vanmorgen", "vanmiddag", "vanavond", "de hele dag", "net als gisteren".

### 4.4 Statistieken — drie kaarten op een rij

Drie gelijke witte cards naast elkaar, horizontaal verdeeld:

| Kaart | Icoon | Waarde | Label |
|-------|-------|--------|-------|
| 1 | `Clock` | **9** | "Actieve uren" |
| 2 | `Activity` | **3** | "Kamers actief" |
| 3 | `TrendingUp` | **8.5u** | "Week gem." |

- Icoon: Deep Sage `#3E6652`, 20px
- Waarde: DM Sans Bold 28px, `#2C2C2C`
- Label: DM Sans 12px, `#8A8A8A`
- Card: wit, border-radius 12px, subtle shadow

### 4.5 Activiteitsgrafiek — "Activiteit vandaag"

Toont activiteitsniveau per **dagdeel**, niet per uur. Dit beschermt de privacy van de bewoner.

- **Titel**: "Activiteit vandaag" — DM Sans Semibold 17px
- **Type**: Staafdiagram (bar chart), 4 dagdelen
- **Staven**: Per dagdeel, hoogte op basis van activiteitsintensiteit
- **Dagdelen**:
  - Nacht (0:00–6:00)
  - Ochtend (6:00–12:00)
  - Middag (12:00–18:00)
  - Avond (18:00–24:00)
- **Kleurschaal**: 4 tinten sage van licht naar donker (weinig → veel)
  - Weinig: `#D4E8DC`
  - Normaal: `#A3D1B4`
  - Veel: `#5E9178`
  - Zeer veel: `#3E6652`
- **Baseline**: Stippellijn die het gemiddelde patroon toont (per dagdeel)
- **X-as labels**: Nacht, Ochtend, Middag, Avond
- **Legenda**: "Weinig" tot "Veel" met kleurblokjes
- Achtergrond: witte card met licht sage tint `#F5FAF7`

> **Privacy:** Geen uur-voor-uur detail. De mantelzorger ziet alleen of ochtend/middag/avond normaal verliep.

### 4.6 Kamers — horizontale scrollbare kaarten

- **Titel**: "Kamers" — DM Sans Semibold 17px
- **Layout**: Horizontaal scrollbaar (overflow-x), geen scrollbar zichtbaar
- **Per kamer-kaart**:
  - Afmeting: ~110px breed, ~130px hoog
  - Achtergrond: licht sage `#E8F3EC` (actief) of licht grijs `#F0EDEA` (inactief)
  - **Icoon**: Groot kamer-icoon (sofa voor woonkamer, pan voor keuken, bed voor slaapkamer), 40px, in sage/grijs
  - **Status dot**: Rechtsboven op het icoon — groen (recent actief) of grijs (niet recent)
  - **Kamernaam**: DM Sans Semibold 14px
  - **Status label**: Vaag tijdsindicator — DM Sans 12px, `#8A8A8A`

**Status labels (geen exacte tijden):**

| Situatie | Label | Dot kleur |
|----------|-------|-----------|
| Activiteit < 1 uur geleden | "Recent actief" | Groen |
| Activiteit vandaag | "Vandaag actief" | Licht groen |
| Geen activiteit vandaag | "Niet recent" | Grijs |

> **Privacy:** Nooit "12 min geleden" of "6 uur geleden". Alleen globale indicatoren.

**Kamer-iconen mapping:**

| Kamer | Icoon (Lucide) |
|-------|----------------|
| Woonkamer | `Sofa` |
| Keuken | `CookingPot` |
| Slaapkamer | `Bed` |
| Badkamer | `Bath` |
| Gang | `DoorOpen` |
| Toilet | `DoorClosed` |

### 4.7 Recente activiteit — dagdeel-overzicht

Geen exacte tijdlijn, maar een **samenvatting per dagdeel** van waar activiteit was.

- **Titel**: "Recente activiteit" — DM Sans Semibold 17px
- **Layout**: Verticale lijst, gegroepeerd per dagdeel
- **Per item**:
  - Links: timeline dot (sage `#3E6652`, 8px cirkel) met verticale lijn
  - **Dagdeel**: "Vanmorgen" / "Vanmiddag" / "Vanavond" — DM Sans Semibold 15px
  - **Beschrijving**: Welke kamers actief waren, bijv. "Woonkamer en keuken" — DM Sans 13px, `#5A5A5A`
  - **Geen kloktijden**: Rechts eventueel alleen dagdeel-icoon (zon/maan)

**Voorbeelden:**

| Dagdeel | Beschrijving |
|---------|-------------|
| Vanmorgen | "Keuken en woonkamer" |
| Vanmiddag | "Woonkamer" |
| Gisteren avond | "Woonkamer en slaapkamer" |
| Gisteren middag | "Alle kamers actief" |

> **Privacy:** Nooit "Beweging gedetecteerd om 09:06". Alleen welke kamers actief waren in welk dagdeel.

### 4.8 Weekoverzicht card — "Deze week"

Onderaan het scherm, witte card:

- **Titel**: **"Deze week"** — DM Sans Semibold 17px
- **Subtitel**: "Stabiel patroon deze week" — DM Sans 14px, `#5A5A5A`
- **7-daagse bar**: Horizontale rij van 7 gekleurde segmenten (ma-zo)
  - Groen `#3E6652` = goed
  - Amber `#D4944C` = aandacht
  - Rood `#C4645A` = sterk afwijkend
  - Grijs `#B8B3AD` = geen data
- **Legenda**: Gekleurde dots met labels, bijv. "6 goed · 1 aandacht"

---

## 5. Scherm 2 — Familie

Toont het huishouden: wie de bewoner is, welke familieleden meekijken, en een gedeeld familiebord.

### 5.1 Header

- Titel: **"Familie"** — gecentreerd, DM Serif Display, 20px

### 5.2 Bewoner banner

- Achtergrond: Licht sage `#EBF5EF`
- **Label**: "Zorg voor" — DM Sans 13px, `#3E6652`
- **Naam**: "Oma Janssen" — DM Sans Bold 22px, `#2C2C2C`
- Border-radius: 12px, padding 16px

### 5.3 Familieleden

- **Sectie header**: "Familieleden" (links) + **"Uitnodigen"** button (rechts)
  - Uitnodigen button: Outline style, icoon `UserPlus`, tekst Deep Sage
- **Per lid** (witte card, gestapeld):
  - **Avatar**: Cirkel 48px met initialen, kleur per persoon:
    - Beheerder: Deep Sage `#3E6652`
    - Kijkers: Amber `#D4944C`, Paars `#8B7EC8`, etc.
  - **Naam**: DM Sans Semibold 16px
  - **Status**: "Nu online" / "2 uur geleden" / "Gisteren" — DM Sans 13px, `#8A8A8A`
  - **Rol badge** (rechts):
    - Beheerder: icoon `Crown` + "Beheerder" in `#D4944C`
    - Kijker: icoon `Eye` + "Kijker" in `#8A8A8A`

**Rollen:**

| Rol | Rechten |
|-----|---------|
| Beheerder | Alles: instellingen, uitnodigen, Hue koppelen |
| Kijker | Alleen meekijken: status, meldingen |

### 5.4 Familiebord

Een gedeeld notitie-/berichtenbord waar familieleden korte updates kunnen plaatsen.

- **Sectie header**: Icoon `MessageCircle` + "Familiebord"
- **Per bericht** (witte card):
  - **Avatar**: Kleine cirkel (32px) met initiaal, zelfde kleur als familielid
  - **Naam**: DM Sans Semibold 14px
  - **Tijd**: Rechts, "3u geleden" / "Gisteren" / "2d geleden" — DM Sans 12px, `#8A8A8A`
  - **Bericht tekst**: DM Sans 15px, `#2C2C2C`
  - Voorbeelden:
    - *"Vandaag gebeld met Oma, ze klonk goed! Ze heeft een nieuwe puzzel gekocht."*
    - *"Morgen even langs om de tuin te doen."*
    - *"Boodschappen gebracht, koelkast is weer vol!"*
- **Input veld** (onderaan, sticky):
  - Placeholder: "Schrijf een notitie..."
  - Achtergrond: `#F5F1EA` (Sand), border-radius 24px
  - Verzend-icoon: `Send` in cirkel, rechts

---

## 6. Scherm 3 — Meldingen

Chronologische feed van alle meldingen en dagsamenvattingen.

### 6.1 Header

- Titel: **"Meldingen"** — gecentreerd, DM Serif Display, 20px

### 6.2 Toolbar

- Links: Bel-icoon + **"X ongelezen"** — DM Sans 15px
- Rechts: Dubbel vinkje icoon + **"Alles gelezen"** link — DM Sans 14px, Deep Sage

### 6.3 Meldingskaarten

Elke melding is een witte card met gekleurde linker accent-border:

| Type | Icoon | Icoon achtergrond | Border kleur | Voorbeeld |
|------|-------|-------------------|-------------|-----------|
| Alles goed | `Heart` | `#EBF5EF` | `#3E6652` | "Alles goed vandaag" |
| Informatie | `Info` | `#FEF6EC` | `#D4944C` | "Meer activiteit dan normaal" |
| Goedemorgen | `Heart` | `#EBF5EF` | `#3E6652` | "Goedemorgen! Er is activiteit vanmorgen." |
| Nachtactiviteit | `AlertTriangle` | `#FEF3E0` | `#D4944C` | "Onrustige nacht" |
| Dagrapport | `Heart` (rood) | `#FDECEB` | `#3E6652` | "Alles goed gisteren" |

**Per kaart:**

- **Icoon**: 40px cirkel met gekleurde achtergrond + wit/gekleurd icoon
- **Titel**: DM Sans Semibold 16px, bijv. "Alles goed vandaag"
- **Tijd**: Rechts, "1 uur geleden" / "5 uur geleden" / "Gisteren" — DM Sans 13px, `#8A8A8A`
- **Ongelezen dot**: Kleine sage cirkel (8px) rechtsboven bij ongelezen meldingen
- **Beschrijving**: DM Sans 14px, `#5A5A5A`, max 2 regels
  - Persoonlijk en warm, bijv. *"Oma was actief zoals gewoonlijk. Niets om je zorgen over te maken."*

### 6.4 Meldingstypen (volledig)

Alle meldingen volgen het privacy-principe: **geen exacte tijdstippen, geen kamerdetails**.

| Type | Trigger | Titel | Beschrijving voorbeeld | Toon |
|------|---------|-------|----------------------|------|
| Dagelijkse samenvatting | Elke avond | "Alles goed vandaag" | "Oma was actief zoals gewoonlijk. Niets om je zorgen over te maken." | Warm, samenvattend |
| Ochtendmelding | Eerste activiteit van de dag | "Goedemorgen!" | "Er is activiteit vanmorgen. Alles normaal." | Positief, bevestigend |
| Meer activiteit | 20%+ boven normaal | "Meer activiteit dan normaal" | "Er was meer beweging dan gewoonlijk vandaag. Misschien bezoek of een wandeling!" | Positief, nieuwsgierig |
| Minder activiteit | 20%+ onder normaal | "Rustige dag tot nu toe" | "Het is wat rustiger dan normaal vandaag." | Neutraal, niet alarmerend |
| Nachtactiviteit | Ongewoon nachtpatroon | "Onrustige nacht" | "Er was meer activiteit vannacht dan gebruikelijk. Dit kan normaal zijn." | Informatief, kalm |
| Geen activiteit | Langdurige stilte | "Nog geen activiteit vandaag" | "Er is vandaag nog geen activiteit opgemerkt." | Alleen bij kritieke meldingen AAN |
| Sensor offline | Sensor niet bereikbaar | "We missen even het zicht" | "Een sensor is tijdelijk niet bereikbaar." | Technisch, alleen voor beheerder |

> **Privacy:** Meldingen vermelden nooit "om 3:15 in de badkamer". Alleen globale patronen: "vannacht", "vanmorgen", "meer dan normaal".

---

## 7. Scherm 4 — Instellingen

Gegroepeerde instellingen met secties.

### 7.1 Header

- Titel: **"Instellingen"** — gecentreerd, DM Serif Display, 20px

### 7.2 Hue Bridge status card

Prominente card bovenaan:

- **Achtergrond**: Deep Sage `#3E6652` (verbonden) of `#B8B3AD` (niet verbonden)
- **Status dot**: Groen cirkel + "Verbonden" in wit
- **Titel**: "Philips Hue Bridge" — wit, DM Sans Bold 20px
- **Details**: "192.168.1.42 · Bridge Pro · 12 apparaten" — wit, DM Sans 14px, opacity 80%
- Border-radius: 16px

**Niet-verbonden variant:**
- Grijze achtergrond
- Rode dot + "Niet verbonden"
- Button: "Verbinden" in wit

### 7.3 Sectie: HUE VERBINDING

Section header: "HUE VERBINDING" — uppercase, DM Sans 12px, `#8A8A8A`, letter-spacing 1px

Witte card met 3 rijen (list items met chevron):

| Item | Icoon | Label | Sublabel |
|------|-------|-------|----------|
| Hue Bridge | `Wifi` | "Hue Bridge" | "Verbonden · BSB002" |
| Bewaakte zones | `Home` | "Bewaakte zones" | "3 van 5 kamers" |
| MotionAware | `Radio` | "MotionAware" | "Beschikbaar met Bridge Pro" |

- Icoon: 40px cirkel, sage achtergrond `#EBF5EF`, icoon `#3E6652`
- Chevron: `ChevronRight`, `#B8B3AD`

### 7.4 Sectie: MELDINGEN

Section header: "MELDINGEN"

Witte card met 3 toggles:

| Item | Icoon | Label | Sublabel | Default |
|------|-------|-------|----------|---------|
| Dagelijkse samenvatting | `Bell` (sage) | "Dagelijkse samenvatting" | "Ontvang elke avond een melding" | AAN |
| Kritieke meldingen | `Shield` (rood) | "Kritieke meldingen" | "Geen activiteit >12 uur" | AAN |
| Nachtelijke activiteit | `Clock` (amber) | "Nachtelijke activiteit" | "Melding bij ongewone nachtpatronen" | UIT |

- Toggle: Custom toggle component
  - AAN: achtergrond Deep Sage `#3E6652`, knop wit
  - UIT: achtergrond `#D4D1CC`, knop wit

### 7.5 Sectie: ABONNEMENT

Section header: "ABONNEMENT"

**Upgrade card** (prominent):
- Border: 2px `#D4944C` (amber)
- Achtergrond: `#FEF6EC` (licht amber)
- Icoon: `Star` in amber
- Titel: **"Upgrade naar Plus"** — DM Sans Semibold 16px
- Subtitel: "Onbeperkte zones, rapporten & meer" — DM Sans 14px, `#5A5A5A`
- Prijs: **"€5/maand"** — DM Sans Bold 18px, `#D4944C`, rechts uitgelijnd

**Huidig plan card** (subtiel):
- Achtergrond: `#F5F1EA` (Sand)
- Tekst: "Huidige plan: **Basis (gratis)**"
- Sublabel: "Max 3 bewaakte zones · Basis samenvatting · 1 gebruiker"

### 7.6 Sectie: OVER

Section header: "OVER"

Witte card met 3 navigatie-items:

| Item | Icoon | Label |
|------|-------|-------|
| Hulp | `HelpCircle` | "Hulp & veelgestelde vragen" |
| Privacy | `Shield` | "Privacy & gegevensbescherming" |
| Uitloggen | `LogOut` | "Uitloggen" |

- Elke rij met chevron rechts
- Uitloggen icoon/tekst in amber `#D4944C` (niet rood — geen alarm)

### 7.7 Footer

- **"GerustThuis v1.0.0"** — gecentreerd, DM Sans 12px, `#B8B3AD`
- Padding-bottom: 32px

---

## 8. Aanvullende schermen

### 8.1 Login / Registratie

Eén scherm met toggle tussen inloggen en registreren:

- GerustThuis logo bovenaan (groot, gecentreerd)
- Tagline: *"Gerust over je dierbare"*
- E-mail invoerveld
- Wachtwoord invoerveld
- (Registratie) Wachtwoord bevestiging
- Primary button: "Inloggen" / "Account aanmaken"
- Toggle link: "Nog geen account? Registreer" / "Al een account? Log in"
- Achtergrond: Cream `#FDFCF7`

### 8.2 Onboarding / Setup

Drie stappen na eerste login:

**Stap 1 — Welkom**
- Illustratie/icoon
- Titel: "Welkom bij GerustThuis"
- Beschrijving: Korte uitleg over het systeem
- Button: "Aan de slag"

**Stap 2 — Hue Bridge verbinden**
- Instructies voor het koppelen
- OAuth flow redirect naar Philips Hue
- Status feedback: "Verbinden..." → "Verbonden!"

**Stap 3 — Leerperiode**
- Progress indicator (dag X van 7)
- Uitleg dat het systeem leert
- Na 7 dagen: automatisch naar Overzicht

### 8.3 Kamer detail (vanuit Kamers)

Bij tap op een kamer-kaart:

- Kamernaam als titel
- Status: "Recent actief" / "Vandaag actief" / "Niet recent" (geen exacte tijd)
- Aantal sensoren in de kamer
- Per sensor: naam, type (beweging/deur), batterijniveau, status (actief/offline)
- **Geen activiteitsgeschiedenis met tijdstippen** — alleen globale status

> **Privacy:** Dit scherm toont alleen of sensoren werken en batterijniveaus. Geen gedetailleerde activiteitslog.

---

## 9. Design tokens & Styling

### 9.1 Kleuren (Tailwind config)

```
colors: {
  sage: {
    50:  '#EBF5EF',
    100: '#D4E8DC',
    200: '#A3D1B4',
    300: '#5E9178',
    400: '#4A7D64',
    500: '#3E6652',  // Primary
    600: '#335544',
    700: '#2A4437',
  },
  amber: {
    50:  '#FEF6EC',
    100: '#F0C88C',
    500: '#D4944C',  // Primary
  },
  terracotta: {
    50:  '#FDECEB',
    500: '#C4645A',
  },
  cream:    '#FDFCF7',
  sand:     '#F5F1EA',
  ink:      '#2C2C2C',
  'ink-soft':  '#5A5A5A',
  'ink-muted': '#8A8A8A',
  'warm-grey': '#B8B3AD',
}
```

### 9.2 Typografie

```
fontFamily: {
  serif: ['DM Serif Display', 'serif'],
  sans:  ['DM Sans', 'sans-serif'],
}
```

### 9.3 Spacing & Sizing

| Token | Waarde | Gebruik |
|-------|--------|---------|
| card-radius | 12px | Cards, buttons |
| card-radius-lg | 16px | Prominente cards (Hue Bridge) |
| card-padding | 16px | Standaard card padding |
| section-gap | 24px | Ruimte tussen secties |
| tab-bar-height | 64px | Bottom navigation |
| touch-target | 44px | Minimum tappable area |
| avatar-sm | 32px | Familiebord berichten |
| avatar-md | 48px | Familieleden lijst |

### 9.4 Shadows

```
shadow-card: '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)'
shadow-none: 'none'  // Meeste cards gebruiken border ipv shadow
```

### 9.5 Borders

- Card border: `1px solid #E8E4DD`
- Divider in lijsten: `1px solid #F0EDEA`
- Actieve/selected: `2px solid #3E6652`

---

## 10. Interacties & Animaties

| Interactie | Animatie |
|------------|----------|
| Tab switch | Fade-in content, 200ms ease |
| Pull-to-refresh | Native pull-down spinner (Overzicht) |
| Card tap | Subtle scale 0.98 + opacity 0.8, 100ms |
| Toggle | Slide knop 200ms ease, kleurovergang |
| Melding markeren | Fade-out ongelezen dot, 300ms |
| Statusbanner | Kleur-crossfade bij statuswijziging, 400ms |
| Familiebord bericht | Slide-in van onder, 250ms ease-out |

---

## 11. Responsiviteit

De app is **mobile-first** als PWA, maar moet ook werken op tablets en desktop:

| Viewport | Layout |
|----------|--------|
| < 640px (mobile) | Standaard, 1 kolom, bottom tabs |
| 640px – 1024px (tablet) | Iets meer padding, kamers 4 op rij |
| > 1024px (desktop) | Max-width 480px, gecentreerd ("phone frame") |

---

## 12. Data flow & Refresh

| Actie | Interval | Methode |
|-------|----------|---------|
| Status ophalen | 5 minuten | Auto-refresh via `setInterval` |
| Sensoren ophalen | 5 minuten | Mee met status refresh |
| Meldingen | Realtime | Supabase Realtime subscriptions |
| Familiebord | Realtime | Supabase Realtime subscriptions |
| Handmatig | Pull-to-refresh | Overzicht scherm |

---

## 13. Abonnementen

| Plan | Prijs | Features |
|------|-------|----------|
| **Basis** (gratis) | €0 | Max 3 zones, basis samenvatting, 1 gebruiker |
| **Plus** | €5/maand | Onbeperkte zones, rapporten, meerdere gebruikers |

---

## 14. Mapstructuur (voorstel)

```
gerustthuis-app/
├── public/
│   ├── manifest.json
│   ├── sw.js
│   └── icons/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── router.tsx
│   ├── components/
│   │   ├── layout/
│   │   │   ├── TabBar.tsx
│   │   │   └── PageHeader.tsx
│   │   ├── overzicht/
│   │   │   ├── StatusBanner.tsx
│   │   │   ├── AISummary.tsx
│   │   │   ├── StatsRow.tsx
│   │   │   ├── ActivityChart.tsx
│   │   │   ├── RoomCards.tsx
│   │   │   ├── RecentActivity.tsx
│   │   │   └── WeekOverview.tsx
│   │   ├── familie/
│   │   │   ├── ResidentBanner.tsx
│   │   │   ├── FamilyMembers.tsx
│   │   │   └── FamilyBoard.tsx
│   │   ├── meldingen/
│   │   │   ├── NotificationCard.tsx
│   │   │   └── NotificationList.tsx
│   │   ├── instellingen/
│   │   │   ├── HueBridgeCard.tsx
│   │   │   ├── HueConnectionSection.tsx
│   │   │   ├── NotificationSettings.tsx
│   │   │   ├── SubscriptionSection.tsx
│   │   │   └── AboutSection.tsx
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Card.tsx
│   │       ├── Toggle.tsx
│   │       ├── Avatar.tsx
│   │       ├── Badge.tsx
│   │       └── ListItem.tsx
│   ├── pages/
│   │   ├── Overzicht.tsx
│   │   ├── Familie.tsx
│   │   ├── Meldingen.tsx
│   │   ├── Instellingen.tsx
│   │   ├── Login.tsx
│   │   └── setup/
│   │       ├── Welcome.tsx
│   │       ├── Connect.tsx
│   │       └── Learning.tsx
│   ├── stores/
│   │   ├── authStore.ts
│   │   └── appStore.ts
│   ├── services/
│   │   ├── supabase.ts
│   │   └── queries.ts
│   ├── hooks/
│   │   ├── useNotifications.ts
│   │   └── useRefreshInterval.ts
│   ├── types/
│   │   └── index.ts
│   ├── constants/
│   │   ├── theme.ts
│   │   └── config.ts
│   └── utils/
│       └── formatting.ts
├── index.html
├── tailwind.config.ts
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 15. Referentie screenshots

De visuele mockups zijn beschikbaar in `gerustthuis-app/assets/`:

| Bestand | Scherm |
|---------|--------|
| `WhatsApp Image...13.03.26 (1).jpeg` | Overzicht — bovenste helft (status + samenvatting + stats + grafiek) |
| `WhatsApp Image...13.03.26.jpeg` | Overzicht — onderste helft (kamers + recente activiteit + weekoverzicht) |
| `WhatsApp Image...13.03.25 (3).jpeg` | Familie — bovenste helft (bewoner + leden) |
| `WhatsApp Image...13.03.25 (4).jpeg` | Familie — onderste helft (familiebord) |
| `WhatsApp Image...13.03.25 (2).jpeg` | Meldingen |
| `WhatsApp Image...13.03.25 (1).jpeg` | Instellingen — bovenste helft |
| `WhatsApp Image...13.03.25.jpeg` | Instellingen — onderste helft |
