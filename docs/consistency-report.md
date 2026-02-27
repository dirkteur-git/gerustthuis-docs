# GerustThuis Project Health Report

_Automatisch gegenereerd op 2026-02-27 09:01_

> Dit rapport is de centrale actielijst voor het project.
> **❌ Problemen** moeten direct opgelost worden.
> **📋 Niet gebouwd** zijn openstaande backlog items.
> **⚠️ Risico** zijn zaken die aandacht verdienen.

---

## ❌ Problemen (2) — moet opgelost worden

- CORS staat op `'*'` in `_shared/cors.ts` — zet op specifieke domeinen (gerustthuis.nl, localhost)
- `hue-token-exchange/index.ts` regel 32: console.log met (deel van) credential — verwijder voor productie

## 📋 Niet gebouwd (8) — backlog items

- US-3: Installer DB-rol bestaat (migration 021) maar er is GEEN installer-specifieke UI/onboarding flow
- US-3b: AcceptInvitation.vue mist rol-bewustzijn voor meekijker vs mantelzorger onboarding
- US-5.5/5.6: Rol upgrade/downgrade (viewer↔admin) nog niet geïmplementeerd in portaal/app UI
- ADR-002: gerustthuis-portaal en gerustthuis-app bestaan nog als aparte repos — samenvoegen naar één Vue 3 PWA staat open
- ADR-003: IKEA Dirigera is prioriteit 1 na Hue — ikea-sync-state Edge Function ontbreekt nog
- `gerustthuis-portaal`: geen tests aanwezig — voeg Vitest toe (unit tests voor z-scores, auth flows, edge cases)
- `gerustthuis-app`: geen tests aanwezig — voeg Vitest toe (unit tests voor z-scores, auth flows, edge cases)
- `gerustthuis-admin`: geen tests aanwezig — voeg Vitest toe (unit tests voor z-scores, auth flows, edge cases)

## ⚠️ Risico (7) — controleer dit

- gerustthuis-portaal heeft geen TypeScript (tsconfig.json ontbreekt) — alle code is .js (verhoogt risico bij refactoring)
- portaal `Analyse.vue`: 945 regels — te groot, splits in subcomponenten
- portaal `Dashboard.vue`: 865 regels — te groot, splits in subcomponenten
- portaal `Instellingen.vue`: 653 regels — te groot, splits in subcomponenten
- portaal `Patronen.vue`: 836 regels — te groot, splits in subcomponenten
- portaal `src/services/supabase.js`: 521 regels — mixt auth, data en domain-logica (god-file). Splits of migreer naar Pinia stores
- gerustthuis-portaal gebruikt geen Pinia — state management via kale `reactive()`. Migreer naar Pinia (consistent met Vue 3 best practices)

---

## 📎 Handmatige audit bevindingen

_Externe code review (feb 2026). Verwijder een item als het is opgelost._

### Security
- **Race condition rate limiting** (`waitlist-signup`): upsert + count check is niet-atomair. Vervang door `UPDATE ... RETURNING` of advisory lock in PostgreSQL.

### Code kwaliteit
- **Input-validatie portaal**: formulieren valideren niet op lengte/formaat/inhoud. Website doet dit wél (Vee-validate + Zod). Voeg validatie toe aan portaal-formulieren.
- **Duplicatie portaal ↔ app**: z-score berekeningen, activiteitsdata-formattering en Hue-logica staan in beide repos. Geen shared packages. Wordt opgelost bij ADR-002 merge.
- **Pinia**: portaal gebruikt `reactive()` voor global state. Migreer naar Pinia voor betere DevTools-ondersteuning en consistency.

### Scorekaart externe review (startpunt)

| Repository | Score | Sterk | Aandacht |
|------------|-------|-------|---------|
| gerustthuis-docs | 8.5/10 | ADR-kwaliteit, volledigheid | Migraties 023-030 niet gedocumenteerd |
| gerustthuis-app | 7.5/10 | TypeScript strict, component-design | Geen tests, veel mock data |
| gerustthuis-website | 8/10 | Productie-klaar, SEO, validatie | Geen tests |
| gerustthuis-supabase | 6.5/10 | Migratie-kwaliteit, RLS | Security-lekken, CORS, race conditions |
| gerustthuis-portaal | 4.5/10 | Data-science logica (z-scores) | Geen TS, fat components, geen tests |
| gerustthuis-admin | 6/10 | Schone architectuur voor intern tool | Hardcoded email-allowlist, beperkt |

---

_Totaal: 2 problemen · 8 backlog · 7 risico · 105 checks OK_