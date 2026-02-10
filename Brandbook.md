GerustThuis Brandbook
1. Merkessentie
Missie: Mantelzorgers gemoedsrust geven door slimme, onopvallende monitoring van hun dierbaren.
Kernwaarden:

Geruststelling - niet alarmeren, maar kalmeren
Eenvoud - complexe data, simpele communicatie
Respect - voor privacy en autonomie van de oudere
Betrouwbaar - altijd beschikbaar, nooit overdreven

Tone of voice:

Warm maar niet kinderachtig
Informatief maar niet technisch
Kalm maar niet afstandelijk
Eerlijk maar niet alarmerend

Voorbeelden:
✗ Niet✓ Wel"ALERT: Geen beweging gedetecteerd!""Rustige ochtend tot nu toe""Anomalie score: 0.73""Iets anders dan normaal""Sensor offline""We missen even het zicht op de badkamer""Gebruiker inactief""Nog geen activiteit vandaag"

2. Logo
Primair logo:

"GerustThuis" in één woord
"Gerust" in accent kleur, "Thuis" in donkergrijs
Geen icoon nodig, het woord is het merk

Gebruiksregels:

Minimale breedte: 120px
Witruimte rondom: minimaal hoogte van de 'G'
Nooit vervormen, roteren of effecten toevoegen

Varianten:

Full color (voor witte achtergrond)
Wit (voor donkere achtergrond)
Monochroom grijs (voor print)


3. Kleuren
Primair palet:
NaamHexGebruikGerust Groen#10b981Accent, positieve status, CTA'sAntraciet#111827Koppen, belangrijke tekstWarm Grijs#6b7280Bodytekst, secundaire infoLicht Grijs#f3f4f6Achtergronden, cardsWit#ffffffHoofdachtergrond
Statuskleur:
StatusKleurHexNormaal / goedGroen#10b981Let opAmber#f59e0bAandacht nodigRood#ef4444Inactief / onbekendGrijs#9ca3af
Kleurgebruik regels:

Rood alleen voor echte problemen, nooit voor decoratie
Groen is de standaard, niet rood
Achtergronden altijd licht, nooit donkere mode (doelgroep)


4. Typografie
Font: Inter (of system-ui als fallback)
ElementGrootteGewichtKleurH124px600AntracietH218px600AntracietH3 / Card titel16px600AntracietBody14px400Warm GrijsSmall / caption12px400#9ca3afButton14px500Wit of Antraciet
Regels:

Nooit volledig hoofdletters (behalve "OK" of "ID")
Geen cursief, nooit
Line-height: 1.5 voor bodytekst


5. Iconografie
Stijl: Outline icons, 1.5px stroke, rounded corners
Bron: Lucide Icons of Heroicons (outline variant)
Sensortype iconen:
TypeIcoonOmschrijvingLamp○ of lightbulbSimpele cirkel of gloeilampBewegingactivity of radioGolvenDeur/contactdoor-openDeurKnopsquareVierkant
Status iconen:
StatusIcoonNormaal✓ checkmarkLet op! in cirkelProbleem✕ of ! in driehoek
Regels:

Iconen altijd vergezeld van tekst (toegankelijkheid)
Kleur volgt de statuskleur
Grootte: 16px inline, 20px standalone


6. Componenten
Cards:
cssbackground: #ffffff;
border: 1px solid #e5e7eb;
border-radius: 8px;
padding: 20px;
box-shadow: none;
hover: box-shadow: 0 2px 8px rgba(0,0,0,0.08);
Buttons:
TypeAchtergrondTekstBorderPrimaryGerust GroenWitGeenSecondaryWitAntraciet1px grijsGhostTransparantGerust GroenGeen
cssborder-radius: 6px;
padding: 10px 16px;
font-weight: 500;
Inputs:
cssborder: 1px solid #d1d5db;
border-radius: 6px;
padding: 10px 12px;
focus: border-color: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,0.1);
```

**Grafieken:**
- Sparklines: alleen lijn, geen fill, geen assen
- Grotere charts: minimale gridlines, geen 3D effecten
- Kleur: Gerust Groen voor actueel, lichtgrijs voor gemiddelde/vergelijking

---

## 7. Communicatierichtlijnen

**Statusmeldingen:**

| Niveau | Titel | Toon |
|--------|-------|------|
| Goed | "Normale dag" | Kort, bevestigend |
| Let op | "Iets anders dan normaal" | Neutraal, niet alarmerend |
| Aandacht | "Bekijk even" | Direct, maar kalm |

**Nooit zeggen:**
- "Alert" of "Alarm"
- "Probleem gedetecteerd"
- "Afwijking" of "Anomalie"
- "Geen beweging" (klinkt als dood)
- Technisch jargon

**Wel zeggen:**
- "Rustige ochtend"
- "Later actief dan normaal"
- "Minder beweging dan gebruikelijk"
- "We kijken even mee"

**Notificaties:**
```
✗ "ALERT: Bewegingssensor Toilet geen activiteit 4 uur"

✓ "Rustige middag - geen activiteit in huis sinds 12:00. 
   Waarschijnlijk even weg, maar check gerust."

8. Ruimte en layout
Spacing schaal: 4px basis

xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
2xl: 48px

Grid:

Max content width: 1200px
Kolommen: 12
Gutter: 24px
Mobiel: 16px margins

Witruimte:

Liever te veel dan te weinig
Cards hebben altijd ademruimte
Geen content tegen de randen


9. Toegankelijkheid
Verplicht:

Contrast ratio minimaal 4.5:1 voor tekst
Focus states op alle interactieve elementen
Tekst altijd bij iconen
Klikbare gebieden minimaal 44x44px
Geen informatie alleen via kleur

Doelgroep-specifiek:

Grotere klikgebieden (mantelzorgers zijn soms ook ouder)
Geen autoplay animaties
Duidelijke error states
Simpele navigatie


10. Don'ts

✗ Donkere mode (doelgroep heeft vaak moeite met)
✗ Kleine tekst (<14px voor body)
✗ Complexe grafieken met veel lijnen
✗ Alarmerende rode kleur als default
✗ Animaties die afleiden
✗ Technische termen in UI
✗ Emoji's (behalve 👋 in onboarding)
✗ Stockfoto's van lachende ouderen
✗ Medische claims of terminologie
✗ "Smart home" of "IoT" language