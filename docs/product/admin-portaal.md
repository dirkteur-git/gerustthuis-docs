# GerustThuis Admin Portaal

## Context

Het projectplan (nu onderdeel van gerustthuis-admin) slaat nu alle data op als een JSONB blob in Supabase. Dit werkt, maar schaalt niet: je kunt niet filteren, rapporteren, of data delen tussen gebruikers. Daarnaast willen we een admin portaal dat breder gaat dan alleen het projectplan.

Dit document beschrijft het ontwerp voor:
1. *Genormaliseerde database tabellen* voor projectplan-data
2. *Admin portaal* als nieuwe repo met uitgebreide functionaliteit

## Admin Portaal — Scope

Het admin portaal (gerustthuis-admin) wordt de centrale plek voor:

| Module | Beschrijving |
|--------|-------------|
| *Projectplan* | Fasen, tickets, go/no-go criteria, budget, tijdlijn |
| *Huishouden beheer* | Overzicht van alle huishoudens, leden, configuraties |
| *Systeem status* | Hue bridge status, edge function logs, data pipeline health |
| *Gebruikers* | User accounts, rollen, uitnodigingen |
| *Rapportages* | Cross-household statistieken, anomalie-trends |

### Technologie

- Vue 3 + Composition API (`<script setup>`)
- Tailwind CSS (consistent met portaal)
- Supabase Auth (bestaande users)
- Supabase Database (genormaliseerde tabellen)
- Repo: gerustthuis-admin

## Database Ontwerp — Projectplan tabellen

### ERD Overzicht

```
projects (1) ──── (N) project_phases (1) ──── (N) phase_criteria
                                     │
                                     ├──── (N) phase_purchases
                                     │
                                     └──── (N) phase_decisions

projects (1) ──── (N) project_tickets (N) ──── (N) ticket_dependencies
```

### Tabel: projects

Project-level instellingen per gebruiker.

| Kolom | Type | Constraint |
|-------|------|-----------|
| id | UUID | PK, default gen_random_uuid() |
| user_id | UUID | FK → auth.users, NOT NULL, UNIQUE |
| name | TEXT | NOT NULL, default 'GerustThuis' |
| description | TEXT | |
| total_budget | NUMERIC | default 0 |
| currency | TEXT | default 'EUR' |
| created_at | TIMESTAMPTZ | default now() |
| updated_at | TIMESTAMPTZ | default now() |

### Tabel: project_phases

10 fasen per project, met status tracking.

| Kolom | Type | Constraint |
|-------|------|-----------|
| id | UUID | PK, default gen_random_uuid() |
| project_id | UUID | FK → projects, NOT NULL |
| phase_number | INTEGER | NOT NULL (0-9) |
| name | TEXT | NOT NULL |
| description | TEXT | |
| status | TEXT | NOT NULL, default 'niet gestart' |
| budget | NUMERIC | nullable |
| no_go_action | TEXT | |
| created_at | TIMESTAMPTZ | default now() |
| updated_at | TIMESTAMPTZ | default now() |

*Constraint:* UNIQUE(project_id, phase_number)

*Status waarden:* niet gestart, actief, go-no-go, afgerond

### Tabel: phase_criteria

Go/no-go criteria per fase.

| Kolom | Type | Constraint |
|-------|------|-----------|
| id | UUID | PK, default gen_random_uuid() |
| phase_id | UUID | FK → project_phases, ON DELETE CASCADE |
| criterion_key | TEXT | NOT NULL (bijv. "0-1") |
| description | TEXT | NOT NULL |
| completed | BOOLEAN | default false |
| completed_at | TIMESTAMPTZ | nullable |
| created_at | TIMESTAMPTZ | default now() |

*Constraint:* UNIQUE(phase_id, criterion_key)

### Tabel: phase_purchases

Uitgaven per fase.

| Kolom | Type | Constraint |
|-------|------|-----------|
| id | UUID | PK, default gen_random_uuid() |
| phase_id | UUID | FK → project_phases, ON DELETE CASCADE |
| description | TEXT | NOT NULL |
| amount | NUMERIC | NOT NULL |
| purchase_date | DATE | default CURRENT_DATE |
| created_at | TIMESTAMPTZ | default now() |

### Tabel: phase_decisions

Go/no-go besluiten (max 1 per fase, maar history bijhouden).

| Kolom | Type | Constraint |
|-------|------|-----------|
| id | UUID | PK, default gen_random_uuid() |
| phase_id | UUID | FK → project_phases, ON DELETE CASCADE |
| decision | TEXT | NOT NULL ('go' of 'no-go') |
| notes | TEXT | nullable |
| decided_at | TIMESTAMPTZ | default now() |

### Tabel: project_tickets

Tickets/taken gekoppeld aan fasen.

| Kolom | Type | Constraint |
|-------|------|-----------|
| id | UUID | PK, default gen_random_uuid() |
| project_id | UUID | FK → projects, NOT NULL |
| phase_id | UUID | FK → project_phases, ON DELETE SET NULL |
| ticket_number | TEXT | NOT NULL, UNIQUE per project |
| title | TEXT | NOT NULL |
| description | TEXT | |
| status | TEXT | NOT NULL, default 'todo' |
| priority | TEXT | NOT NULL, default 'should' |
| estimated_hours | NUMERIC | nullable |
| planned_week | INTEGER | nullable (1-52) |
| created_at | TIMESTAMPTZ | default now() |
| updated_at | TIMESTAMPTZ | default now() |

*Status waarden:* todo, in-progress, done

*Priority waarden:* must, should, nice

*Ticket nummering:* Database sequence project_ticket_seq per project, format GT-001

### Tabel: ticket_dependencies

Relaties tussen tickets (many-to-many).

| Kolom | Type | Constraint |
|-------|------|-----------|
| id | UUID | PK, default gen_random_uuid() |
| ticket_id | UUID | FK → project_tickets, ON DELETE CASCADE |
| depends_on_id | UUID | FK → project_tickets, ON DELETE CASCADE |
| created_at | TIMESTAMPTZ | default now() |

*Constraint:* UNIQUE(ticket_id, depends_on_id), CHECK(ticket_id != depends_on_id)

## RLS Beleid

Alle tabellen gebruiken RLS. Toegang via de projects.user_id:

```sql
-- Voorbeeld voor project_phases:
CREATE POLICY "Users can manage own phases" ON project_phases
  FOR ALL USING (
    project_id IN (SELECT id FROM projects WHERE user_id = auth.uid())
  );
```

Hetzelfde patroon voor alle child-tabellen: join naar projects om user_id te checken.

## Migratie van JSONB naar genormaliseerde tabellen

### Strategie

1. Nieuwe tabellen aanmaken (migratie 022)
2. Data migratiescript: lees projectplan_state.state JSONB, schrijf naar genormaliseerde tabellen
3. gerustthuis-admin herschrijven naar directe Supabase queries
4. projectplan_state tabel behouden als backup, later verwijderen

### Migratiescript (SQL)

```sql
-- Stap 1: Insert project
INSERT INTO projects (user_id, name, description, total_budget, currency)
SELECT user_id,
  state->'project'->>'name',
  state->'project'->>'description',
  (state->'project'->>'totalBudget')::numeric,
  state->'project'->>'currency'
FROM projectplan_state
WHERE state->'project' IS NOT NULL;

-- Stap 2: Insert phases
INSERT INTO project_phases (project_id, phase_number, name, description, status, budget, no_go_action)
SELECT p.id, (phase->>'id')::int, phase->>'name', phase->>'description',
  phase->>'status', (phase->>'budget')::numeric, phase->>'noGoAction'
FROM projectplan_state ps
JOIN projects p ON p.user_id = ps.user_id,
LATERAL jsonb_array_elements(ps.state->'phases') AS phase;

-- Stap 3: Insert criteria (per fase)
-- Stap 4: Insert purchases (per fase)
-- Stap 5: Insert tickets
-- Stap 6: Insert dependencies
```

## Admin Portaal — Pagina's

### Projectplan module

| Route | Pagina | Functionaliteit |
|-------|--------|----------------|
| / | Dashboard | Overzicht actieve fase, budget, ticket stats |
| /fasen | Fasen overzicht | Alle fasen met voortgang |
| /fasen/:id | Fase detail | Criteria, purchases, go/no-go, tickets |
| /tickets | Kanban board | Drag-drop tickets, filters, zoeken |
| /planning | Tijdlijn | Weekplanning, dependencies |

### Beheer module (nieuw)

| Route | Pagina | Functionaliteit |
|-------|--------|----------------|
| /beheer/huishoudens | Huishoudens | Lijst, status, config per huishouden |
| /beheer/gebruikers | Gebruikers | Accounts, rollen, uitnodigingen |
| /beheer/systeem | Systeem status | Hue bridges, edge functions, cron jobs |
| /beheer/rapportages | Rapportages | Data kwaliteit, anomalie-trends |

## Fasering

### Fase 1: Database tabellen (migratie 022)
- Alle 7 tabellen aanmaken met RLS
- Data migratie vanuit JSONB blob
- Verificatie: data klopt na migratie

### Fase 2: Admin portaal repo opzetten
- Vue 3 + Tailwind + Supabase
- Auth (login, guard)
- Basis layout (sidebar navigatie)

### Fase 3: Projectplan module migreren
- Dashboard, Fasen, FaseDetail, Tickets, Planning
- Directe Supabase queries ipv reactive store
- Herschreven CRUD functies

### Fase 4: Beheer module
- Huishouden overzicht (leest bestaande tabellen)
- Gebruikersbeheer
- Systeem status

### Fase 5: Rapportages
- Data kwaliteit per huishouden
- Anomalie-trends over tijd
- Sensor uptime
