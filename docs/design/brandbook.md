# GerustThuis Brandbook v3.0

**Deep Sage & Amber — Februari 2026**

> Volledig interactief brandbook: `assets/gerustthuis-brand-v3/gerustthuis-brandbook-v3.html`

## 1. Merkessentie

**Missie:** Mantelzorgers gemoedsrust geven door slimme, onopvallende monitoring van hun dierbaren.

**Belofte:** Wij vertellen je rustig hoe de dag verloopt. Geen alarmen, geen jargon — gewoon duidelijkheid wanneer je het nodig hebt.

**Logo concept: Dun dak, stevig hart**
Een beschermend dak in een dunne lijn (4px), met daaronder een krachtig hart in een dikke lijn (7.5px). Het dak beschermt subtiel op de achtergrond. Het hart is wat je voelt.

### Kernwaarden

| Waarde | Betekenis |
|--------|-----------|
| Geruststelling | Kalmeren, niet alarmeren |
| Menselijkheid | Techniek voelt als zorg |
| Privacy | Geen camera's, geen microfoons |
| Eenvoud | Zo min mogelijk, zo goed mogelijk |

### Tone of voice

- Warm maar niet kinderachtig
- Informatief maar niet technisch
- Kalm maar niet afstandelijk
- Eerlijk maar niet alarmerend

## 2. Logo

Twee elementen in één beeld: beschermend dak (lijndikte 4) + krachtig hart (lijndikte 7.5).

### Varianten

| Variant | Gebruik | Bestand |
|---------|---------|---------|
| Mono sage | Standaard op wit | `logos/logo-primary.svg` |
| Tweekleur | Sage dak + amber hart | `logos/logo-two-color.svg` |
| Op sage | Wit op sage achtergrond | `logos/logo-white.svg` |
| Op donker | Op donkere achtergronden | `logos/logo-on-dark.svg` |

### Regels

- Dak altijd 4px, hart altijd 7.5px (of proportioneel)
- Op kleine formaten (<32px) worden beide lijnen proportioneel dikker
- Gebruik altijd de aangeleverde SVG-bestanden
- Minimale breedte icoon: 32px
- Nooit het dak dikker maken dan het hart
- Nooit vervormen, roteren of effecten toevoegen
- Nooit het hart los van het dak gebruiken

## 3. Varianten: Consumer & Pro

| | Consumer | Pro (Zakelijk) |
|---|---------|----------------|
| **Logo** | Deep sage dak, amber hart | Donker icoon, gedempt amber hart |
| **Toon** | Warm, persoonlijk | Professioneel, zakelijk |
| **Headings** | Serif (DM Serif Display) | Serif |
| **Doelgroep** | Families, mantelzorgers | Thuiszorg, corporaties, gemeenten |

## 4. Kleuren

### Primair palet

| Naam | Hex | Gebruik |
|------|-----|---------|
| Deep Sage | `#3E6652` | Primair accent, CTA's, dak in logo |
| Sage Mid | `#5E9178` | Positieve status, hover states |
| Amber | `#D4944C` | Hart in logo, warmte-accent, let-op status |
| Amber Light | `#F0C88C` | Highlights, hover, zachte accenten |
| Ink | `#2C2C2C` | Koppen, belangrijke tekst |

### Neutrale basis

| Naam | Hex | Gebruik |
|------|-----|---------|
| Cream | `#FDFCF7` | Pagina-achtergrond |
| Sand | `#F5F1EA` | Secties, kaart-achtergronden |
| White | `#FFFFFF` | Cards, content |
| Ink Soft | `#5A5A5A` | Bodytekst |
| Ink Muted | `#8A8A8A` | Captions, secundair |

### Statuskleuren

| Status | Kleur | Hex |
|--------|-------|-----|
| Goed | Sage | `#3E6652` |
| Even opletten | Amber | `#D4944C` |
| Aandacht nodig | Terracotta | `#C4645A` |
| Inactief | Warm grijs | `#B8B3AD` |

### Verdeling

70% neutraal (cream/sand/white) — 20% sage — 10% amber

## 5. Typografie

**Fonts:** DM Serif Display (koppen) + DM Sans (body)

| Element | Font | Grootte | Gewicht |
|---------|------|---------|---------|
| H1 — Display | DM Serif Display | 32px | Regular |
| H2 — Sectie | DM Serif Display | 24px | Regular |
| H3 — Card | DM Sans | 17px | Semibold (600) |
| Body | DM Sans | 15px | Regular (400) |
| Caption | DM Sans | 12px | Medium (500) |

## 6. Taal & Communicatie

### Statusmeldingen

| Nooit zo | Altijd zo |
|----------|-----------|
| "ALERT: Geen beweging gedetecteerd!" | "Rustige ochtend tot nu toe" |
| "Anomalie score: 0.73" | "Een beetje anders dan gewoonlijk" |
| "Sensor offline — systeem fout" | "We missen even het zicht" |
| "Gebruiker inactief sinds 09:00" | "Nog geen activiteit vandaag" |

### Verboden woorden

- "Alert" of "Alarm"
- "Probleem gedetecteerd"
- "Afwijking" of "Anomalie"
- "Geen beweging" — klinkt als het ergste
- "Monitoring" in consumer context — gebruik "meekijken"
- Technisch jargon: "sensor", "systeem", "offline"

## 7. Componenten

### Buttons

| Type | Achtergrond | Tekst |
|------|-------------|-------|
| Primary | Sage `#3E6652` | Wit |
| Secondary | Wit | Ink |
| Warm | Amber `#D4944C` | Wit |
| Ghost | Transparant | Sage |

### Border radius

- 12px voor cards
- 10px voor buttons
- 8px voor kleine elementen
- Nooit scherpe hoeken

### Icoon stijl

Afgeronde lijn-iconen (stroke: 2px, linecap: round). Geen gevulde iconen, geen scherpe hoeken.

## 8. Toegankelijkheid

| Meting | Waarde | Toelichting |
|--------|--------|-------------|
| Contrast | 6.1:1 | Wit op sage — WCAG AA+ ruim gehaald |
| Touch target | 44px | Minimale tapgrootte mobiel |
| Minimale body | 15px | Consumer app bodytekst |
| Line-height | 1.6 | Ruime regelafstand |

### Regels

- Status altijd met tekst + kleur, nooit alleen kleur
- Alle interactieve elementen focusbaar met toetsenbord
- Test regelmatig met echte gebruikers uit de doelgroep
- Geen donkere mode (doelgroep heeft hier moeite mee)
- Geen kleine tekst (<14px) buiten dashboards
- Geen autoplay video of audio

## 9. Don'ts

- Donkere mode
- Kleine tekst (<14px voor body)
- Complexe grafieken met veel lijnen
- Alarmerende rode kleur als default
- Animaties die afleiden
- Technische termen in UI
- Emoji's (behalve in onboarding)
- Stockfoto's van lachende ouderen
- Medische claims of terminologie
- "Smart home" of "IoT" language

## Bestanden

Alle brand assets staan in `assets/gerustthuis-brand-v3/`:

```
gerustthuis-brand-v3/
├── gerustthuis-brandbook-v3.html    # Interactief brandbook
├── GerustThuis-Brand-Package.zip    # Compleet pakket
├── logos/
│   ├── logo-primary.svg/png         # Mono sage
│   ├── logo-two-color.svg/png       # Sage + amber
│   ├── logo-white.svg/png           # Op donker
│   ├── logo-on-dark.svg             # Op donkere achtergrond
│   ├── wordmark-*.svg/png           # Woordmerken (cream/dark/sage/two-color)
│   ├── app-icon-*.svg/png           # App iconen (gradient/pro/sage/sage-amber)
│   └── favicon.*                    # Favicons (16/32/SVG)
└── social/
    ├── facebook-cover*.svg/png      # Facebook covers
    ├── instagram-*.svg/png          # Instagram posts & stories
    ├── linkedin-banner*.svg/png     # LinkedIn banners
    └── profile-picture-round.*      # Profielfoto's
```
