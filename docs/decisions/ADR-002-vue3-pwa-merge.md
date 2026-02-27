# ADR-002: Één Vue 3 PWA — merge portaal en app

**Status:** In uitvoering (feb 2026)
**Datum:** 2025
**Auteur:** Dirk Bakker

---

## Context

GerustThuis heeft twee aparte frontend-applicaties gebouwd:

| Repo | Tech | Doel | Status |
|------|------|------|--------|
| `gerustthuis-portaal` | Vue 3, Vite, Tailwind v3 | Desktop dashboard voor mantelzorgers | Verder uitgewerkt (heatmaps, anomaly detection, Hue koppeling) |
| `gerustthuis-app` | React 19, Vite, Tailwind v3 | Mobiele PWA voor mantelzorgers | Goede UX-patronen (tabs, dagdelen, privacy), minder functionaliteit |

**Probleem:** Twee codebases voor dezelfde gebruiker (mantelzorger) op verschillende devices. Ze raken snel uit sync — een bugfix of nieuwe feature moet twee keer gebouwd worden. De React app en Vue portaal delen dezelfde Supabase backend, maar hebben aparte state management, componenten en routering.

**Beide apps dienen dezelfde gebruiker:** De mantelzorger. Er is geen reden voor twee aparte applicaties.

---

## Overwogen alternatieven

| Optie | Pro | Con |
|-------|-----|-----|
| **Één Vue 3 PWA** (portaal uitbreiden) | Portaal is verder, Vue 3 al bekend | React app weggooien, mobiele UX opnieuw bouwen |
| Één React PWA (app uitbreiden) | React app heeft betere mobiele UX | Portaal functionaliteit (heatmap, anomaly) opnieuw bouwen in React |
| Twee aparte apps houden | Geen migratie nodig | Blijft uit sync, dubbel onderhoud |
| React Native | Native apps | Ver van huidige stack, te complex voor MVP |

---

## Beslissing

**Merge naar één Vue 3 PWA — portaal als basis, UX-patronen van app overnemen.**

Redenen:
- Portaal heeft meer werkende functionaliteit (heatmap, z-score, Hue OAuth)
- Vue 3 is al gekozen voor portaal én admin portal — consistent
- PWA in Vue 3 is volledig haalbaar (Vite PWA plugin)
- Responsive design + Vue Router = geen aparte app nodig
- UX-patronen van de React app (tab navigatie, dagdelen, privacyfocus) zijn CSS/UX — niet React-specifiek

**Wat van de app wordt overgenomen:**
- Tab navigatie voor mobiel (Overzicht / Familie / Meldingen / Instellingen)
- Weergave per dagdeel (ochtend/middag/avond/nacht) — nooit exacte tijdstippen
- Privacy-taal in UI ("geen exacte tijden zichtbaar")
- Kompakte weergave voor kleine schermen
- DeviceShell concept (375px centered op desktop voor preview)

---

## Implementatieplan

### Fase 1: Responsive maken van portaal
- Mobile-first breakpoints toevoegen aan bestaande views
- Tab navigatie toevoegen voor mobiel (`<768px`)
- Dagdeel-weergave implementeren in Overzicht-tab

### Fase 2: PWA configuratie
- `vite-plugin-pwa` installeren en configureren
- Service worker voor offline basisfunctionaliteit
- App-manifest (icoon, naam, kleuren uit brandbook)
- `apple-touch-icon` en iOS meta-tags

### Fase 3: Migratie afronden
- Meldingen-tab implementeren (was in app, niet in portaal)
- Familie-board implementeren (was in app, niet in portaal)
- Instellingen samenvoegen (portaal heeft meer, app heeft betere UX)

### Fase 4: App deprecaten
- `gerustthuis-app` archiveren op GitHub
- Vercel deployment van app verwijderen

---

## Gevolgen

**Positief:**
- Één codebase — feature pariteit automatisch
- Één deployment — minder Vercel projecten
- Één auth-flow — geen gesplitste gebruikerservaring meer
- Vue 3 consistent door alle frontends (portaal, admin, pwa)

**Negatief / risico:**
- Mobiele UX kost meer CSS-aandacht dan native tabbladen — testen op echte devices vereist
- PWA installatie op iOS Safari is beperkter dan Android (geen push notificaties via web)
  - Workaround: email/WhatsApp notificaties als alternatief
- `gerustthuis-app` React codebase gaat verloren — documenteer UX-beslissingen vóór archivering

**Beslissing over repo:** `gerustthuis-portaal` wordt hernoemd naar `gerustthuis-frontend` of behoudt de naam. Naam verandering is optioneel — GitHub behoudt redirects.

---

## Voortgang (feb 2026)

### Gedaan
- `Analyse.vue` verplaatst naar `gerustthuis-admin_portal` (developer tool hoort niet bij mantelzorger-UI)
- Sidebar vervangen door bottom `TabBar.vue` (4 tabs: Overzicht / Familie / Meldingen / Instellingen)
- `Familie.vue` aangemaakt: bewoner banner + familieleden + familiegroep berichten (realtime via Supabase)
- `Meldingen.vue` aangemaakt: notificaties per huishouden, gegroepeerd op datum, mark-as-read, realtime
- `supabase.js` uitgebreid met: `getResident()`, `getFamilyBoardMessages()`, `postFamilyBoardMessage()`, `getNotifications()`, `markNotificationRead()`, `markAllNotificationsRead()`
- Router bijgewerkt: `/familie` en `/meldingen` routes toegevoegd
- Link "Sensoren & Kamers →" toegevoegd in Instellingen.vue

### Nog te doen
- PWA configuratie (`vite-plugin-pwa`, service worker, manifest)
- `gerustthuis-app` archiveren op GitHub
