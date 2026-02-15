# GerustThuis User Stories

User stories gegroepeerd per personage voor het GerustThuis ecosysteem.

**Laatst bijgewerkt:** 2026-02-15

---

## Personages

### Bewoner

De oudere die thuis woont en gemonitord wordt. Heeft **geen eigen account**. Wordt als profiel aangemaakt door de mantelzorger.

| Eigenschap | Beschrijving |
|------------|--------------|
| Voornaam | Bijv. "Annie", "Jan" |
| Relatie | mama, papa, opa, oma, partner, broer, zus, vriend, buurman, anders |
| Foto | Optionele profielfoto |
| Geboortedatum | Optioneel, voor leeftijdscontext |
| Notities | Optioneel, vrije tekst |

**Kernprincipe:** De bewoner gebruikt het systeem niet zelf. Sensoren werken onzichtbaar op de achtergrond. De bewoner merkt niets van de monitoring.

---

### Mantelzorger

De persoon die meekijkt via het portaal of de app. Heeft een account, beheert het huishouden, ontvangt meldingen.

| Eigenschap | Beschrijving |
|------------|--------------|
| Account | Email + wachtwoord via Supabase Auth |
| Rol | `admin` (beheerder) of `viewer` (meekijker) |
| Meerdere bewoners | Kan meerdere huishoudens monitoren |
| Meldingen | Push, email, SMS (configureerbaar) |

**Kernprincipe:** "Geen bericht = goed bericht." De mantelzorger wordt alleen gestoord als er iets afwijkt.

---

### Installateur

Iemand uit de kring - een zoon die handig is met techniek, een vriend, een buurman - die helpt met het plaatsen van sensoren en het koppelen van de Philips Hue Bridge. Geen externe professional, maar iemand die de bewoner kent.

| Eigenschap | Beschrijving |
|------------|--------------|
| Account | Email + wachtwoord via Supabase Auth |
| Rol | `installer` |
| Toegang | Kan sensoren, devices en bewonersprofiel zien. Geen activiteitsdata, geen meldingen. |
| Flexibel | Admin kan de rol later wijzigen naar `viewer` (meekijker) of de toegang intrekken |

**Kernprincipe:** De installateur kent de bewoner, maar hoeft geen bewegingsdata te zien. Ze helpen even met de techniek en gaan dan weer hun gang. Als ze later ook willen meekijken, kan de admin hun rol wijzigen naar viewer.

---

## User Stories

### 1. Onboarding - Mantelzorger (nieuw account)

#### US-1.1 Account aanmaken
> Als mantelzorger wil ik een account aanmaken met mijn emailadres, zodat ik het systeem kan gebruiken.

**Acceptatiecriteria:**
- Ik kan registreren met email + wachtwoord
- Er wordt automatisch een huishouden aangemaakt
- Ik word admin van dit huishouden
- Ik kom op de onboarding flow terecht

#### US-1.2 Bewoner profiel instellen
> Als mantelzorger wil ik het profiel van mijn naaste instellen (naam, relatie, foto), zodat het systeem persoonlijk aanvoelt.

**Acceptatiecriteria:**
- Ik kan een voornaam invullen (verplicht)
- Ik kan een relatie kiezen uit een lijst: mama, papa, opa, oma, partner, broer, zus, vriend, buurman, anders
- Ik kan optioneel een foto uploaden
- Na instellen toont het systeem gepersonaliseerde berichten (bijv. "Het gaat goed met mama")
- Het huishouden wordt automatisch hernoemd (bijv. "Bij mama")

#### US-1.3 Meerdere bewoners toevoegen
> Als mantelzorger wil ik meerdere bewoners aan een huishouden toevoegen, zodat ik een ouder echtpaar tegelijk kan monitoren.

**Acceptatiecriteria:**
- Ik kan een tweede bewoner toevoegen aan hetzelfde huishouden
- Berichten gebruiken de namen van beide bewoners indien relevant
- Elke bewoner heeft een eigen profiel (naam, relatie, foto)

#### US-1.4 Philips Hue koppelen
> Als mantelzorger wil ik de Philips Hue Bridge koppelen, zodat het systeem sensordata kan ontvangen.

**Acceptatiecriteria:**
- Ik word doorgestuurd naar de Hue OAuth login
- Na autorisatie worden sensoren automatisch ontdekt
- Ik zie een lijst van gevonden sensoren per kamer
- De Hue Bridge wordt gekoppeld aan mijn huishouden

#### US-1.5 Leerfase doorlopen
> Als mantelzorger wil ik zien dat het systeem het dagritme van mijn naaste leert, zodat ik weet wanneer de monitoring betrouwbaar is.

**Acceptatiecriteria:**
- Ik zie een voortgangsindicator (dag X van 7)
- Ik kan de app al gebruiken tijdens de leerfase
- Na 7 dagen is de baseline compleet
- Het systeem toont "We leren het dagritme van [naam]" tijdens de leerfase

---

### 2. Onboarding - Mantelzorger (uitgenodigd)

#### US-2.1 Uitnodiging ontvangen
> Als mantelzorger wil ik via een link uitgenodigd worden voor een huishouden, zodat ik kan meekijken met een naaste.

**Acceptatiecriteria:**
- Ik ontvang een link via email
- Als ik al een account heb, word ik direct lid
- Als ik geen account heb, maak ik eerst een account aan en word dan lid
- Ik zie direct het bewonersprofiel (naam, foto) van de naaste

#### US-2.2 Rol begrijpen
> Als uitgenodigde mantelzorger wil ik begrijpen wat mijn rol is (admin of viewer), zodat ik weet wat ik kan doen.

**Acceptatiecriteria:**
- Bij het accepteren zie ik welke rol ik krijg
- Als viewer kan ik meekijken maar niet beheren
- Als admin kan ik ook instellingen wijzigen en mensen uitnodigen

---

### 3. Onboarding - Installateur

#### US-3.1 Uitgenodigd worden als installateur
> Als zoon/vriend/buurman wil ik uitgenodigd worden voor het huishouden van mijn ouder/kennis, zodat ik kan helpen met de sensoren.

**Acceptatiecriteria:**
- Ik ontvang een uitnodigingslink van de mantelzorger
- Mijn rol is `installer`
- Ik zie het sensoroverzicht en het bewonersprofiel (ik ken de bewoner)
- Ik zie geen activiteitsdata (bewegingen, patronen)

#### US-3.2 Sensoren configureren
> Als installateur wil ik de Hue Bridge koppelen en sensoren controleren, zodat het systeem correct werkt.

**Acceptatiecriteria:**
- Ik kan de Hue Bridge koppelen als dat nog niet is gebeurd
- Ik zie alle gevonden sensoren met kamer-toewijzing
- Ik kan controleren of sensoren online zijn
- Ik kan sensoren hernoemen of aan kamers toewijzen

#### US-3.3 Later ook meekijken
> Als installateur wil ik later eventueel ook kunnen meekijken met de status, als de mantelzorger dat goedkeurt.

**Acceptatiecriteria:**
- De admin kan mijn rol wijzigen van `installer` naar `viewer`
- Na rolwijziging zie ik ook de activiteitsdata en kan ik meldingen ontvangen
- De admin kan mijn toegang ook volledig intrekken

---

### 4. Dagelijks gebruik - Mantelzorger

#### US-4.1 Status bekijken
> Als mantelzorger wil ik in een oogopslag zien hoe het gaat met mijn naaste, zodat ik gerust ben.

**Acceptatiecriteria:**
- Ik zie een persoonlijk statusbericht: "Het gaat goed met [naam]" (groen), "Iets anders dan normaal bij [naam]" (amber)
- Bij meerdere bewoners zie ik de status per bewoner
- De status wordt elke 5 minuten ververst

#### US-4.2 Patronen bekijken
> Als mantelzorger wil ik het dagritme van mijn naaste bekijken, zodat ik trends kan herkennen.

**Acceptatiecriteria:**
- Ik zie het dagritme met naam: "[naam]'s dagritme"
- Vergelijking vandaag vs normaal is beschikbaar
- Weekpatroon en trends tonen de naam van de bewoner

#### US-4.3 Melding ontvangen
> Als mantelzorger wil ik een melding krijgen als er iets afwijkt, zodat ik actie kan ondernemen.

**Acceptatiecriteria:**
- Meldingen gebruiken de naam van de bewoner
- "Rustige ochtend bij [naam]" in plaats van "Geen activiteit gedetecteerd"
- Ik kan meldingsvoorkeuren instellen (push, email, SMS)
- Ik kan gevoeligheid instellen (gevoelig, normaal, alleen urgent)

---

### 5. Huishouden beheer - Admin

#### US-5.1 Mantelzorger uitnodigen
> Als admin wil ik een andere mantelzorger uitnodigen voor mijn huishouden, zodat meerdere mensen kunnen meekijken.

**Acceptatiecriteria:**
- Ik kan een emailadres invullen en een rol kiezen (admin of viewer)
- De uitgenodigde ontvangt een link per email
- De uitnodiging verloopt na 7 dagen
- Ik zie een lijst van openstaande uitnodigingen

#### US-5.2 Installateur uitnodigen
> Als admin wil ik een installateur uitnodigen, zodat iemand de sensoren kan plaatsen.

**Acceptatiecriteria:**
- Ik kan een installateur uitnodigen met de `installer` rol
- De installateur krijgt beperkte toegang (alleen devices, geen activiteitsdata)
- Ik kan de installateurstoegang intrekken na de installatie

#### US-5.3 Bewoner profiel bewerken
> Als admin wil ik het bewonersprofiel kunnen bewerken, zodat de informatie actueel blijft.

**Acceptatiecriteria:**
- Ik kan naam, relatie en foto wijzigen
- Ik kan een bewoner verwijderen
- Wijzigingen zijn direct zichtbaar voor alle leden van het huishouden

#### US-5.4 Lid verwijderen
> Als admin wil ik een lid kunnen verwijderen uit het huishouden, zodat ik de toegang kan beheren.

**Acceptatiecriteria:**
- Ik kan viewers en installateurs verwijderen
- Ik kan geen andere admins verwijderen (tenzij ik de enige admin ben)
- Het verwijderde lid verliest direct toegang tot alle data

---

### 6. Meerdere huishoudens - Mantelzorger

#### US-6.1 Meerdere huishoudens monitoren
> Als mantelzorger wil ik meerdere huishoudens monitoren (bijv. moeder en schoonmoeder), zodat ik voor meerdere naasten kan zorgen.

**Acceptatiecriteria:**
- Ik kan lid zijn van meerdere huishoudens
- Ik kan wisselen tussen huishoudens
- Elk huishouden heeft eigen bewonersprofiel(en) en instellingen
- De app toont duidelijk welk huishouden actief is

---

## Gepersonaliseerde berichten

Het toevoegen van bewoners maakt het hele systeem persoonlijker. Voorbeelden:

| Generiek (nu) | Gepersonaliseerd (nieuw) |
|----------------|--------------------------|
| "Normale dag" | "Het gaat goed met mama" |
| "Rustige ochtend" | "Rustige ochtend bij mama" |
| "Minder beweging dan normaal" | "Mama is vandaag rustiger dan normaal" |
| "Eerste activiteit: 08:15" | "Mama is rond 08:15 opgestaan" |
| "We leren nog" | "We leren het dagritme van mama" |
| "Huishouden" | "Bij mama" |

---

## Data-flow diagram

```
Mantelzorger (admin)
    │
    ├── Maakt account aan
    │
    ├── Maakt bewonersprofiel aan ──► residents tabel
    │     (naam, relatie, foto)
    │
    ├── Koppelt Hue Bridge ──► hue_config tabel
    │
    ├── Nodigt installateur uit ──► household_invitations (role: installer)
    │     │
    │     └── Installateur configureert sensoren ──► hue_devices
    │           (beperkte toegang: geen activiteitsdata)
    │
    ├── Nodigt mantelzorger uit ──► household_invitations (role: viewer/admin)
    │     │
    │     └── Meekijker ziet status + patronen
    │           (inclusief bewonersprofiel en gepersonaliseerde berichten)
    │
    └── Dagelijks: bekijkt status
          "Het gaat goed met mama" ◄── daily_activity_stats + residents
```

---

## Privacy overwegingen

| Aspect | Bewoner | Mantelzorger | Installateur |
|--------|---------|--------------|-------------|
| Bewoner naam + foto | N.v.t. | Ja | Nee |
| Sensor overzicht | N.v.t. | Ja | Ja |
| Activiteitsdata | N.v.t. | Ja | Nee |
| Patronen & analyse | N.v.t. | Ja | Nee |
| Instellingen | N.v.t. | Admin: ja, Viewer: nee | Nee |
| Leden beheer | N.v.t. | Admin: ja, Viewer: nee | Nee |
