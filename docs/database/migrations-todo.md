# Migrations TODO — Alles in één keer uitvoeren

> **Aanpak:** Alle migrations schrijven, dan in één sessie uitvoeren via Supabase SQL Editor.
> Volgorde is belangrijk — sommige tabellen hebben foreign keys naar eerder gemaakte tabellen.

---

## Status overzicht

| # | Migration | Status | Kritiek? |
|---|-----------|--------|----------|
| 031 | `setup_completed` op `user_profiles` | ✅ Gedraaid | JA — login flow werkt niet zonder dit |
| 032 | `family_board_messages` tabel | ✅ Gedraaid | Nee — voor Familie tab |
| 033 | `notifications` tabel | ✅ Gedraaid | Nee — voor Meldingen tab |
| 034 | `user_settings` tabel | ✅ Gedraaid | Nee — voor Instellingen toggles |
| 035 | `residents.first_name` → `naam` (rename) | ✅ Gedraaid + app-code bijgewerkt | Nee — puur naamgeving |

---

## App code fix (GEEN migration, wel nodig)

### ⚠️ Schema bug in `Instellingen.tsx`

Migration 028 heeft `hue_config` en `hue_devices` verhuisd naar het `integrations` schema.
De app vraagt ze nog via de `public` schema → **dit werkt niet!**

**Fix in `Instellingen.tsx`:**
```typescript
// ❌ Fout — public schema
supabase.from('hue_config').select(...)
supabase.from('hue_devices').select(...)

// ✅ Goed — integrations schema
supabase.schema('integrations').from('hue_config').select(...)
supabase.schema('integrations').from('hue_devices').select(...)
```

**Fix voor Overzicht queries (nog te bouwen):**
```typescript
// daily_activity_stats, activity_events, room_activity_hourly
supabase.schema('activity').from('daily_activity_stats').select(...)
```

Zie portaal: `src/services/supabase.js` — `activityDb()` en `integrationsDb()` helpers.

---

## Hue OAuth — NIET opnieuw bouwen

De OAuth flow is **al volledig geïmplementeerd** in het portaal:

| Bestand portaal | Wat het doet |
|----------------|-------------|
| `src/views/HueConnect.vue` | OAuth URL bouwen + redirect naar `api.meethue.com` |
| `src/views/HueCallback.vue` | Code ontvangen + Edge Function aanroepen |
| Edge Function `hue-token-exchange` | Token uitwisselen + opslaan in `integrations.hue_config` |

Voor de **app** (setup stap 3 — Connect Hue):
- Dezelfde Edge Function hergebruiken
- `redirect_uri` aanpassen naar de app URL (`/setup/connect/callback`)
- Env var `VITE_HUE_CLIENT_ID` ook in de app `.env` zetten

---

## Migration 031 — Uitvoeren

**Bestand:** `gerustthuis-supabase/supabase/migrations/031_setup_completed.sql`

```sql
ALTER TABLE user_profiles
  ADD COLUMN IF NOT EXISTS setup_completed BOOLEAN NOT NULL DEFAULT false;

UPDATE user_profiles
SET setup_completed = true
WHERE id IN (
  SELECT DISTINCT hm.user_id
  FROM household_members hm
  JOIN households h ON h.id = hm.household_id
  JOIN residents r ON r.household_id = h.id
);
```

**Resultaat:** Bestaande users met bewoners krijgen `setup_completed = true` → zij worden niet meer naar setup gestuurd.

---

## Migration 032 — `family_board_messages`

```sql
-- Migration 032: Familiebord berichten
CREATE TABLE IF NOT EXISTS family_board_messages (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  household_id UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
  user_id      UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  message      TEXT NOT NULL CHECK (char_length(message) <= 500),
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_family_board_household
  ON family_board_messages(household_id, created_at DESC);

ALTER TABLE family_board_messages ENABLE ROW LEVEL SECURITY;

-- Huishoudleden mogen berichten lezen
CREATE POLICY "Members view family messages" ON family_board_messages
  FOR SELECT TO authenticated
  USING (
    household_id IN (
      SELECT household_id FROM household_members
      WHERE user_id = auth.uid()
    )
  );

-- Huishoudleden mogen eigen berichten plaatsen
CREATE POLICY "Members post family messages" ON family_board_messages
  FOR INSERT TO authenticated
  WITH CHECK (
    user_id = auth.uid()
    AND household_id IN (
      SELECT household_id FROM household_members
      WHERE user_id = auth.uid()
    )
  );

-- Alleen eigen berichten verwijderen
CREATE POLICY "Members delete own messages" ON family_board_messages
  FOR DELETE TO authenticated
  USING (user_id = auth.uid());

-- Realtime inschakelen
ALTER PUBLICATION supabase_realtime ADD TABLE family_board_messages;
```

---

## Migration 033 — `notifications`

```sql
-- Migration 033: Meldingen tabel
CREATE TABLE IF NOT EXISTS notifications (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  household_id UUID NOT NULL REFERENCES households(id) ON DELETE CASCADE,
  type         TEXT NOT NULL CHECK (type IN ('goed', 'info', 'goedemorgen', 'nacht', 'dagrapport', 'kritiek')),
  title        TEXT NOT NULL,
  description  TEXT,
  is_read      BOOLEAN NOT NULL DEFAULT false,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_household
  ON notifications(household_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_unread
  ON notifications(household_id, is_read) WHERE is_read = false;

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Huishoudleden mogen meldingen lezen
CREATE POLICY "Members view notifications" ON notifications
  FOR SELECT TO authenticated
  USING (
    household_id IN (
      SELECT household_id FROM household_members
      WHERE user_id = auth.uid()
    )
  );

-- Admins mogen meldingen aanmaken (of service_role via backend)
CREATE POLICY "Admins create notifications" ON notifications
  FOR INSERT TO authenticated
  WITH CHECK (
    household_id IN (
      SELECT household_id FROM household_members
      WHERE user_id = auth.uid() AND role = 'admin'
    )
  );

-- Huishoudleden mogen is_read updaten
CREATE POLICY "Members mark notifications read" ON notifications
  FOR UPDATE TO authenticated
  USING (
    household_id IN (
      SELECT household_id FROM household_members
      WHERE user_id = auth.uid()
    )
  )
  WITH CHECK (true);

-- Service role volledige toegang (voor Edge Functions)
CREATE POLICY "Service role full access notifications" ON notifications
  FOR ALL TO service_role
  USING (true) WITH CHECK (true);

-- Realtime inschakelen
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;
```

---

## Migration 034 — `user_settings`

```sql
-- Migration 034: Gebruikersinstellingen (notificatie voorkeuren)
CREATE TABLE IF NOT EXISTS user_settings (
  user_id                   UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  dagelijks_samenvatting    BOOLEAN NOT NULL DEFAULT true,
  kritieke_alerts           BOOLEAN NOT NULL DEFAULT true,
  nachtelijke_activiteit    BOOLEAN NOT NULL DEFAULT false,
  updated_at                TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- updated_at trigger
DROP TRIGGER IF EXISTS trigger_user_settings_updated_at ON user_settings;
CREATE TRIGGER trigger_user_settings_updated_at
  BEFORE UPDATE ON user_settings
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- Alleen eigen rij lezen
CREATE POLICY "Users view own settings" ON user_settings
  FOR SELECT TO authenticated
  USING (user_id = auth.uid());

-- Eigen instellingen aanmaken/bijwerken
CREATE POLICY "Users manage own settings" ON user_settings
  FOR ALL TO authenticated
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());
```

---

## Migration 035 — `residents.first_name` → `naam` (optioneel)

```sql
-- Migration 035: Hernoem residents.first_name naar naam
-- first_name is misleidend — het is een vrije naam-aanduiding
-- (kan "Jenny", "Janssen", "de Boer" zijn)
ALTER TABLE residents
  RENAME COLUMN first_name TO naam;
```

**Let op:** Dit vereist ook updates in:
- `src/types/index.ts` — `Resident.first_name` → `Resident.naam`
- `src/utils/formatting.ts` — `resident.first_name` → `resident.naam`
- `src/stores/authStore.ts` — profile query select
- `src/pages/setup/VoorWie.tsx` — form veld naam

---

## Uitvoervolgorde

1. **031** — setup_completed (kritiek, nu doen)
2. **032** — family_board_messages
3. **033** — notifications
4. **034** — user_settings
5. **035** — residents rename (optioneel, afstemmen met Dirk)

**Daarna in app code:**
- Fix `Instellingen.tsx` schema naar `integrations`
- Fix Overzicht queries naar `activity` schema
- Als 035 gedraaid: types + formatting + authStore updaten
