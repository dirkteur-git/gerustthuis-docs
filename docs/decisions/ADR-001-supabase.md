# ADR-001: Cloud-first architectuur — Supabase als huidige implementatie

**Status:** Geaccepteerd
**Datum:** 2024
**Auteur:** Dirk Bakker

---

## Ontwerpprincipe: volledig cloud-based

GerustThuis is volledig cloud-based. Er staat **niets lokaal** bij de gebruiker thuis, behalve de bestaande smart home hub (Hue, IKEA, Aqara). Geen eigen gateway, geen lokale server, geen Raspberry Pi.

Dit principe versterkt de kernbelofte:
- Nul installatie — gebruiker koppelt via een app, geen monteur
- Altijd up-to-date — geen firmware-updates bij gebruikers thuis
- Schaalbaar — van 1 naar 100.000 huishoudens zonder hardware-logistiek

> "Dingen weten is met AI bijna gratis. De infrastructuur hoeft er ook niet duur bij te zijn."

**Lokale verwerking is bewust niet het doel.** Privacy wordt gewaarborgd via data-minimalisatie (aggregaties, geen ruwe events zichtbaar voor mantelzorger) en Row Level Security — niet via lokale opslag.

---

## Context: huidige implementatie

Voor de MVP-fase is Supabase gekozen als cloud-platform. Supabase levert:
- PostgreSQL database met Row Level Security
- Authenticatie (email/wachtwoord, uitnodigingsflow)
- Edge Functions (Deno) voor polling en OAuth
- `pg_cron` voor geplande aggregaties
- Gratis tier voor de beginfase

**Supabase is de huidige invulling van het cloud-first principe — niet het principe zelf.** Bij schaling wordt Supabase vervangen of aangevuld. De migraties zijn standaard SQL en kunnen naar elke PostgreSQL.

---

## Overwogen alternatieven (MVP-fase)

| Optie | Pro | Con |
|-------|-----|-----|
| **Supabase** | Auth + DB + Edge Functions in één, gratis tier, PostgreSQL | Vendor lock-in voor auth en realtime |
| Firebase | Bekend, goed SDK | NoSQL, geen relaties, Google-afhankelijkheid |
| Custom (Node.js + PostgreSQL) | Volledige controle | Veel bouwtijd, zelf auth implementeren |
| Neon + Vercel Functions | PostgreSQL, serverless | Geen ingebouwde auth |

---

## Schalingsstrategie

| Grens | Actie |
|-------|-------|
| <1.000 huishoudens | Supabase gratis tier |
| 1.000–10.000 | Supabase Pro ($25/mnd) |
| >10.000 | Evalueer: zelf hosten (Supabase open source op eigen infra) of migreer naar managed PostgreSQL (Neon, RDS) + eigen auth |
| Enterprise / ISP-partner | Dedicated infra per partner — cloud-first principe blijft, Supabase-specifieke code verdwijnt |

Bij elke schalingsstap blijven de SQL-migraties en het data-model intact. Alleen de hosting-laag wijzigt.

---

## Gevolgen

**Positief:**
- Nul lokale afhankelijkheden — support is volledig remote mogelijk
- RLS op database-niveau — data-isolatie onafhankelijk van applicatielaag
- SQL-migraties zijn portable — niet locked in op Supabase-specifieke features
- Snelle MVP — auth, database en functies in één platform

**Negatief / risico:**
- Supabase gratis tier limieten: 500MB database, 2GB bandbreedte, 500K edge function requests/maand
- Edge Function cold starts ~1-2s na inactiviteit (niet kritiek voor 5-min polling)
- Vendor lock-in voor auth en realtime bij Supabase — migreerbaar maar niet gratis
