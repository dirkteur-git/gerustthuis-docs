# GerustThuis User Stories

User stories gegroepeerd per personage voor het GerustThuis ecosysteem.

**Laatst bijgewerkt:** 2026-02-27

---

## Personages

### Bewoner

De oudere die thuis woont en gemonitord wordt. Heeft **geen eigen account**. Wordt als profiel aangemaakt door de mantelzorger of installateur.

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
| Rol | `admin` (beheerder) |
| Meerdere bewoners | Kan meerdere huishoudens monitoren |
| Meldingen | Push, email, SMS (configureerbaar) |
| Installatie | Kan zelf installeren via onboarding flow op eigen telefoon |

**Kernprincipe:** "Geen bericht = goed bericht." De mantelzorger wordt alleen gestoord als er iets afwijkt. De mantelzorger kan het systeem ook zelf installeren zonder professionele hulp — de onboarding flow begeleidt stap voor stap.

---

### Meekijker

Een tweede mantelzorger die uitgenodigd is om mee te kijken. Kan de status en patronen zien, maar beheert niets. Denk aan een broer of zus die ook betrokken is.

| Eigenschap | Beschrijving |
|------------|--------------|
| Account | Email + wachtwoord via Supabase Auth |
| Rol | `viewer` |
| Toegang | Status, patronen, meldingen. Geen beheer, geen uitnodigen, geen instellingen |
| Meldingen | Configureerbaar (push, email, SMS) — onafhankelijk van admin |
| Upgrade | Admin kan meekijker upgraden naar admin. Admin kan door andere admin worden gedowngraded naar meekijker. |

**Kernprincipe:** De meekijker is betrokken maar niet verantwoordelijk. Ze zien hetzelfde beeld als de admin, maar kunnen niets wijzigen. "Ik wil weten hoe het met mama gaat, maar mijn zus regelt de rest."

---

### Installateur (professioneel)

Iemand van GerustThuis die bij de bewoner thuis het systeem installeert. Maakt het huishouden aan, koppelt de Hue Bridge, configureert sensoren en draagt het huishouden over aan de mantelzorger. Na overdracht heeft de installateur **geen toegang meer**.

| Eigenschap | Beschrijving |
|------------|--------------|
| Account | GerustThuis medewerker-account (niet gekoppeld aan huishouden) |
| Rol | `installer` (tijdelijk, tijdens setup) |
| Toegang | Tijdens installatie: sensoren, devices, bridge koppeling. Na overdracht: geen |
| Overdracht | Nodigt mantelzorger uit als `admin`, daarna verdwijnt installateur uit huishouden |

**Kernprincipe:** De installateur is een tijdelijke rol. Na overdracht aan de mantelzorger heeft de installateur geen enkele toegang meer tot het huishouden of de data. Geen lid, geen viewer, helemaal weg.

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
- Ik zie een voortgangsindicator (dag X van 14)
- Ik kan de app al gebruiken tijdens de leerfase
- Na 14 dagen is de baseline compleet
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

### 3. Onboarding - Professionele installatie

#### US-3.1 Huishouden aanmaken (installateur)
> Als installateur wil ik een nieuw huishouden aanmaken voor de bewoner, zodat ik het systeem kan klaarzetten.

**Acceptatiecriteria:**
- Ik maak een huishouden aan via mijn installateur-account
- Ik vul het bewonersprofiel in (naam, optioneel foto)
- Het huishouden is nog niet zichtbaar voor mantelzorgers

#### US-3.2 Hue Bridge koppelen en sensoren configureren (installateur)
> Als installateur wil ik de Hue Bridge koppelen en sensoren controleren, zodat het systeem correct werkt.

**Acceptatiecriteria:**
- Ik kan de Hue Bridge koppelen via OAuth
- Ik zie alle gevonden sensoren met kamer-toewijzing
- Ik kan sensoren hernoemen of aan kamers toewijzen
- Ik kan controleren of sensoren online zijn en data sturen

#### US-3.3 Huishouden overdragen aan mantelzorger
> Als installateur wil ik het huishouden overdragen aan de mantelzorger, zodat zij het beheer overnemen.

**Acceptatiecriteria:**
- Ik vul het emailadres van de mantelzorger in
- De mantelzorger ontvangt een uitnodiging als `admin`
- Na acceptatie door de mantelzorger verdwijnt mijn toegang volledig
- Ik kan het huishouden niet meer zien of benaderen

#### US-3.4 Zelf installeren (mantelzorger)
> Als mantelzorger wil ik het systeem zelf kunnen installeren op mijn telefoon, zodat ik geen externe hulp nodig heb.

**Acceptatiecriteria:**
- De onboarding flow begeleidt mij stap voor stap
- Ik maak zelf een account aan en word automatisch admin
- Ik koppel zelf de Hue Bridge via OAuth
- Ik wijs sensoren toe aan kamers
- Ik hoef niemand uit te nodigen om te starten

---

### 3b. Onboarding - Meekijker

#### US-3b.1 Uitgenodigd worden als meekijker
> Als broer/zus/familielid wil ik uitgenodigd worden om mee te kijken, zodat ik ook weet hoe het met onze ouder gaat.

**Acceptatiecriteria:**
- Ik ontvang een uitnodigingslink van de admin
- Ik zie direct wie de bewoner is (naam, foto)
- Ik snap dat ik kan meekijken maar niet beheren
- Ik kan mijn eigen meldingsvoorkeuren instellen

#### US-3b.2 Status bekijken als meekijker
> Als meekijker wil ik dezelfde status zien als de admin, zodat ik gerust ben.

**Acceptatiecriteria:**
- Ik zie hetzelfde statusbericht ("Het gaat goed met mama")
- Ik zie patronen en dagritme
- Ik kan NIET: instellingen wijzigen, mensen uitnodigen, bewonersprofiel bewerken
- Ik kan WEL: mijn eigen meldingen aan/uit zetten

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

#### US-5.5 Meekijker upgraden naar admin
> Als admin wil ik een meekijker kunnen upgraden naar admin, zodat zij ook het huishouden kunnen beheren.

**Acceptatiecriteria:**
- Ik kan de rol van een viewer wijzigen naar admin
- De meekijker krijgt direct alle admin-rechten (instellingen, uitnodigen, beheer)
- De meekijker ontvangt een melding dat hun rol is gewijzigd
- Er kunnen meerdere admins per huishouden zijn

#### US-5.6 Admin downgraden naar meekijker
> Als admin wil ik een andere admin kunnen downgraden naar meekijker, zodat ik het beheer kan beperken.

**Acceptatiecriteria:**
- Ik kan de rol van een andere admin wijzigen naar viewer
- Ik kan mezelf niet downgraden als ik de enige admin ben
- De gedowngrade persoon verliest direct beheerrechten
- De gedowngrade persoon ontvangt een melding dat hun rol is gewijzigd
- De gedowngrade persoon behoudt toegang tot status en patronen

#### US-5.7 Lid verwijderen uit huishouden
> Als admin wil ik een lid kunnen verwijderen uit het huishouden, zodat ik de toegang kan beheren.

**Acceptatiecriteria:**
- Ik kan viewers verwijderen
- Ik kan andere admins verwijderen, mits er minimaal 1 admin overblijft
- Ik kan mezelf niet verwijderen als ik de enige admin ben
- Het verwijderde lid verliest direct alle toegang
- Het verwijderde lid ontvangt een melding dat hun toegang is ingetrokken

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

### 7. Storingen & foutafhandeling

#### US-7.1 Hue Bridge offline
> Als mantelzorger wil ik een duidelijke melding krijgen als de Hue Bridge offline is, zodat ik weet dat er geen data binnenkomt en ik niet onterecht gerust ben.

**Acceptatiecriteria:**
- Ik zie een waarschuwing in de app: "We ontvangen geen data van de sensoren bij [naam]"
- De statusmelding verandert van groen naar grijs (onbekend), niet naar rood (alarm)
- Ik ontvang een push/email na 30 minuten offline (configureerbaar)
- Als de bridge weer online komt, verdwijnt de waarschuwing automatisch
- De app toont wanneer de laatste data is ontvangen: "Laatst gezien: vandaag 14:32"

#### US-7.2 Supabase / database storing
> Als mantelzorger wil ik weten als het systeem tijdelijk niet beschikbaar is, zodat ik begrijp waarom ik geen data zie.

**Acceptatiecriteria:**
- Bij een databasestoring zie ik een vriendelijke foutmelding: "We hebben tijdelijk een storing. Je data is veilig, we werken aan een oplossing."
- De app crasht niet maar toont een fallback-scherm
- Na herstel laadt de app automatisch de laatste data
- Storingen worden gelogd voor het GerustThuis team (monitoring)

#### US-7.3 Anomaly detection / berekening faalt
> Als mantelzorger wil ik dat het systeem eerlijk is als een berekening niet lukt, zodat ik geen verkeerde conclusies trek.

**Acceptatiecriteria:**
- Als de patroonherkenning faalt, toont de app: "We hebben niet genoeg data om het dagritme te analyseren"
- De basisfuncties (ruwe activiteitsstatus) blijven werken, ook als de slimme analyse faalt
- Er wordt geen "Het gaat goed met [naam]" getoond als het systeem het niet weet — dan wordt het "We hebben nu geen beeld van [naam]"
- Het systeem valt terug op simpele regels (wel/geen beweging) als de complexe analyse niet beschikbaar is

#### US-7.4 Sensor batterij bijna leeg
> Als mantelzorger wil ik een melding krijgen als een sensorbatterij bijna leeg is, zodat ik op tijd kan vervangen.

**Acceptatiecriteria:**
- Ik ontvang een melding bij <20% batterij
- De melding noemt welke sensor in welke kamer het betreft
- In het sensoroverzicht zie ik de batterijstatus per sensor
- Bij een lege batterij (0% / geen data) wordt dit duidelijk onderscheiden van een bridge-storing

#### US-7.5 Internet uitval bij bewoner
> Als mantelzorger wil ik weten als het internet bij mijn naaste uitvalt, zodat ik het verschil begrijp tussen "geen activiteit" en "geen verbinding".

**Acceptatiecriteria:**
- Het systeem maakt onderscheid tussen "geen data door internetuitval" en "geen beweging gedetecteerd"
- Bij internetuitval: grijze status ("Geen verbinding bij [naam]")
- Bij geen beweging met werkende verbinding: amber status ("Rustige dag bij [naam]")
- Na herstel van internet worden eventueel gebufferde data alsnog verwerkt

---

## Gepersonaliseerde berichten

Het toevoegen van bewoners maakt het hele systeem persoonlijker. Voorbeelden:

| Generiek (nu) | Gepersonaliseerd (nieuw) |
|----------------|--------------------------|
| "Normale dag" | "Het gaat goed met mama" |
| "Rustige ochtend" | "Rustige ochtend bij mama" |
| "Minder beweging dan normaal" | "Mama is vandaag rustiger dan normaal" |
| "Ochtend: actief" | "Mama is vanochtend actief" |
| "We leren nog" | "We leren het dagritme van mama" |
| "Huishouden" | "Bij mama" |

---

## Data-flow diagram

### Scenario A: Professionele installatie

```
Installateur (GerustThuis)
    │
    ├── Maakt huishouden aan
    ├── Vult bewonersprofiel in ──► residents tabel
    ├── Koppelt Hue Bridge ──► hue_config tabel
    ├── Configureert sensoren ──► hue_devices
    │
    └── Draagt over aan mantelzorger ──► household_invitations (role: admin)
          │
          ├── Mantelzorger accepteert → wordt admin
          └── Installateur verliest alle toegang
```

### Scenario B: Zelf installeren

```
Mantelzorger
    │
    ├── Maakt account aan → wordt admin
    ├── Maakt bewonersprofiel aan ──► residents tabel
    ├── Koppelt Hue Bridge ──► hue_config tabel
    ├── Configureert sensoren ──► hue_devices
    │
    └── Nodigt meekijker(s) uit ──► household_invitations (role: viewer)
          │
          └── Meekijker ziet status + patronen
                (inclusief bewonersprofiel en gepersonaliseerde berichten)
```

### Dagelijks gebruik

```
Admin / Meekijker
    │
    └── Bekijkt status
          "Het gaat goed met mama" ◄── daily_activity_stats + residents
```

---

## Privacy overwegingen

| Aspect | Bewoner | Admin | Meekijker | Installateur (tijdens setup) |
|--------|---------|-------|-----------|------------------------------|
| Bewoner naam + foto | N.v.t. | Ja | Ja | Ja (vult in) |
| Sensor overzicht | N.v.t. | Ja | Nee | Ja |
| Activiteitsdata | N.v.t. | Ja | Ja | Nee |
| Patronen & analyse | N.v.t. | Ja | Ja | Nee |
| Instellingen | N.v.t. | Ja | Nee | Nee |
| Leden beheer | N.v.t. | Ja | Nee | Nee |
| Toegang na overdracht | N.v.t. | Permanent | Permanent | Geen |
