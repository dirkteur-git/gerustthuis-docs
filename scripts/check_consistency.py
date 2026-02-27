#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
"""
GerustThuis Project Health Dashboard
Drie categorieen:
  ❌ PROBLEMEN      — docs/code is stuk of inconsistent (must fix)
  📋 NIET GEBOUWD   — gedocumenteerd maar code ontbreekt (backlog)
  ⚠️  RISICO         — code aanwezig maar niet gedocumenteerd of verouderd
"""

import re
from pathlib import Path
from datetime import datetime

REPO_ROOT    = Path(__file__).parent.parent
PROJECT_ROOT = REPO_ROOT.parent

SUPABASE_ROOT = PROJECT_ROOT / "gerustthuis-supabase"
PORTAAL_ROOT  = PROJECT_ROOT / "gerustthuis-portaal"
APP_ROOT      = PROJECT_ROOT / "gerustthuis-app"

problems  = []   # ❌ Echte fouten — docs/code is kapot of inconsistent
backlog   = []   # 📋 Gedocumenteerd maar nog niet gebouwd
risks     = []   # ⚠️  In code, niet in docs — of code wijkt af van docs
ok_count  = 0


def problem(msg):
    problems.append(msg)
    print(f"  ❌ {msg}")

def todo(msg):
    backlog.append(msg)
    print(f"  📋 {msg}")

def risk(msg):
    risks.append(msg)
    print(f"  ⚠️  {msg}")

def ok(msg=""):
    global ok_count
    ok_count += 1


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORIE 1: PROBLEMEN — dingen die nu kapot of inconsistent zijn
# ══════════════════════════════════════════════════════════════════════════════

def check_internal_links():
    """Check 1a: Gebroken interne markdown links"""
    print("\n--- 1a. Interne links ---")
    SKIP = {"consistency-report.md"}
    broken = 0
    checked = 0

    for md_file in REPO_ROOT.rglob("*.md"):
        if ".git" in str(md_file) or md_file.name in SKIP:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for text, path in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content):
            if path.startswith(("http", "#", "mailto")):
                continue
            path_clean = path.split("#")[0]
            if not path_clean:
                continue
            target = (md_file.parent / path_clean).resolve()
            checked += 1
            if target.exists():
                ok()
            else:
                broken += 1
                problem(f"`{md_file.relative_to(REPO_ROOT)}` → gebroken link: [{text}]({path})")

    print(f"     {checked} links, {broken} gebroken")


def check_forbidden_columns():
    """Check 1b: Verouderde / niet-bestaande kolomnamen in docs"""
    print("\n--- 1b. Verouderde kolomnamen ---")
    SKIP = {"consistency-report.md"}
    FORBIDDEN = [
        ("current_state", "kolom bestaat niet"),
        ("stat_date",     "heet `date` in daily_activity_stats"),
        ("zone_id",       "gebruik `room_name`"),
    ]
    ALLOWED_CTX = [r'hernoemd naar', r'Migratie\s+\d+', r'-- Migration']
    found = 0

    for md_file in (REPO_ROOT / "docs").rglob("*.md"):
        if md_file.name in SKIP:
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for col, reason in FORBIDDEN:
            for match in re.finditer(rf'`{re.escape(col)}`|(?<!\w){re.escape(col)}(?!\w)', content):
                ctx = content[max(0, match.start()-80):match.end()+80]
                if any(re.search(p, ctx, re.IGNORECASE) for p in ALLOWED_CTX):
                    continue
                found += 1
                problem(f"`{md_file.relative_to(REPO_ROOT)}` vermeldt `{col}` — {reason}")

    if found == 0:
        ok()
        print("     Geen verouderde kolomnamen gevonden")


def check_tables_in_migrations():
    """Check 1c: Tabelnamen in docs bestaan in migraties"""
    print("\n--- 1c. Tabelnamen vs migraties ---")
    KEY_TABLES = [
        "hue_config", "hue_devices", "physical_devices",
        "activity_events", "room_activity", "room_activity_hourly",
        "daily_activity_stats", "households", "household_members",
        "user_profiles", "residents", "notifications",
        "family_board_messages", "user_settings",
        "waitlist",   # gebruikt door waitlist-signup Edge Function
    ]
    migrations_dir = SUPABASE_ROOT / "supabase" / "migrations"
    if not migrations_dir.exists():
        risk(f"Migratiemap niet gevonden: {migrations_dir}")
        return

    all_sql = ""
    for f in sorted(migrations_dir.glob("*.sql")):
        try:
            all_sql += f.read_text(encoding="utf-8", errors="ignore") + "\n"
        except Exception:
            pass

    referenced = set()
    for pattern in [
        r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(?:"?\w+"?\s*\.\s*)?"?(\w+)"?',
        r'ALTER TABLE\s+(?:"?\w+"?\s*\.\s*)?"?(\w+)"?',
        r'CREATE (?:UNIQUE )?INDEX\s+\w+\s+ON\s+(?:"?\w+"?\s*\.\s*)?"?(\w+)"?',
        r'CREATE POLICY\s+"[^"]+"\s+ON\s+(?:"?\w+"?\s*\.\s*)?"?(\w+)"?',
    ]:
        for m in re.finditer(pattern, all_sql, re.IGNORECASE):
            referenced.add(m.group(1).lower())

    missing = [t for t in KEY_TABLES if t.lower() not in referenced]
    for t in missing:
        problem(f"Tabel `{t}` staat in docs maar NIET gevonden in migraties")
    if not missing:
        ok()
        print(f"     Alle {len(KEY_TABLES)} tabellen gevonden in migraties")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORIE 2: NIET GEBOUWD — docs beschrijven het, code ontbreekt
# ══════════════════════════════════════════════════════════════════════════════

def check_portaal_views():
    """Check 2a: Views in portaal.md bestaan als .vue bestanden"""
    print("\n--- 2a. Portaal views (docs → code) ---")
    views_dir = PORTAAL_ROOT / "src" / "views"
    if not views_dir.exists():
        risk(f"Views map niet gevonden: {views_dir}")
        return

    existing = {f.stem.lower() for f in views_dir.glob("*.vue")}

    # Views die gedocumenteerd zijn in portaal.md
    # Analyse.vue is verplaatst naar gerustthuis-admin_portal
    DOCUMENTED_VIEWS = {
        "Dashboard":        "dashboard",
        "Familie":          "familie",
        "Meldingen":        "meldingen",
        "Patronen":         "patronen",
        "Woning":           "woning",
        "Instellingen":     "instellingen",
        "HueConnect":       "hueconnect",
        "HueCallback":      "huecallback",
        "AcceptInvitation": "acceptinvitation",
        "Login":            "login",
        "Trends":           "trends",
    }

    for doc_name, file_stem in DOCUMENTED_VIEWS.items():
        if file_stem in existing:
            ok()
        else:
            todo(f"View `{doc_name}` staat in portaal.md maar `{doc_name}.vue` ontbreekt")

    # Views die wél bestaan maar mogelijk niet gedocumenteerd
    documented_lower = set(DOCUMENTED_VIEWS.values())
    for f in views_dir.glob("*.vue"):
        if f.stem.lower() not in documented_lower:
            risk(f"View `{f.name}` bestaat in portaal maar staat niet in portaal.md")


def check_edge_functions():
    """Check 2b: Edge Functions in docs bestaan als directories"""
    print("\n--- 2b. Edge Functions (docs → code) ---")
    functions_dir = SUPABASE_ROOT / "supabase" / "functions"
    if not functions_dir.exists():
        risk(f"Functions map niet gevonden: {functions_dir}")
        return

    existing = {d.name for d in functions_dir.iterdir() if d.is_dir() and not d.name.startswith("_")}

    DOCUMENTED = ["hue-sync-state", "hue-token-exchange", "waitlist-signup", "ga4-analytics"]

    for fn in DOCUMENTED:
        if fn in existing:
            ok()
        else:
            todo(f"Edge Function `{fn}` staat in docs maar map ontbreekt in supabase/functions/")

    for fn in existing:
        if fn not in DOCUMENTED:
            risk(f"Edge Function `{fn}` bestaat maar staat niet in docs")


def check_app_pages():
    """Check 2c: App schermen in app-design.md bestaan als .tsx bestanden"""
    print("\n--- 2c. App schermen (docs → code) ---")
    pages_dir = APP_ROOT / "src" / "pages"
    if not pages_dir.exists():
        risk(f"App pages map niet gevonden: {pages_dir}")
        return

    existing = {f.stem.lower() for f in pages_dir.rglob("*.tsx")}

    # 4 tabs gedocumenteerd in app-design.md
    DOCUMENTED_TABS = {
        "Overzicht":    "overzicht",
        "Familie":      "familie",
        "Meldingen":    "meldingen",
        "Instellingen": "instellingen",
    }

    for doc_name, stem in DOCUMENTED_TABS.items():
        if stem in existing:
            ok()
        else:
            todo(f"App tab `{doc_name}` staat in app-design.md maar `{doc_name}.tsx` ontbreekt")


def check_user_story_features():
    """Check 2d: Specifieke user story features — zijn ze in code aanwezig?"""
    print("\n--- 2d. User story features (docs → code) ---")

    checks = []

    # US-1.4: Hue OAuth flow — hue-token-exchange function aanwezig
    hue_fn = SUPABASE_ROOT / "supabase" / "functions" / "hue-token-exchange"
    checks.append((
        hue_fn.exists(),
        "US-1.4 Hue OAuth",
        "hue-token-exchange/ Edge Function aanwezig",
        "US-1.4: Hue koppeling (hue-token-exchange function) ontbreekt"
    ))

    # US-1.5: Leerfase / setup_completed kolom in migraties
    migrations_dir = SUPABASE_ROOT / "supabase" / "migrations"
    setup_completed_found = False
    if migrations_dir.exists():
        for f in migrations_dir.glob("*.sql"):
            try:
                if "setup_completed" in f.read_text(encoding="utf-8", errors="ignore"):
                    setup_completed_found = True
                    break
            except Exception:
                pass
    checks.append((
        setup_completed_found,
        "US-1.5 Leerfase tracking",
        "setup_completed kolom gevonden in migraties",
        "US-1.5: setup_completed kolom ontbreekt in migraties (nodig voor leerfase-indicator)"
    ))

    # US-3 Installer rol — DB bestaat (021), maar ontbreekt er een installer-specifieke UI flow?
    installer_db_found = False
    if migrations_dir.exists():
        for f in migrations_dir.glob("*.sql"):
            try:
                if "installer" in f.read_text(encoding="utf-8", errors="ignore").lower():
                    installer_db_found = True
                    break
            except Exception:
                pass
    # Check installer-specifieke views (onboarding flow, setup flow)
    installer_views = ["Installer.vue", "InstallerSetup.vue", "InstallSetup.vue"]
    installer_ui_found = any(
        (PORTAAL_ROOT / "src" / "views" / v).exists() or
        (APP_ROOT / "src" / "pages" / v).exists()
        for v in installer_views
    ) if (PORTAAL_ROOT.exists() or APP_ROOT.exists()) else False

    checks.append((
        installer_ui_found,
        "US-3 Installer onboarding UI",
        "installer-specifieke UI flow gevonden",
        "US-3: Installer DB-rol bestaat (migration 021) maar er is GEEN installer-specifieke UI/onboarding flow"
    ))

    # US-4.3: Notifications tabel
    notif_found = False
    if migrations_dir.exists():
        for f in migrations_dir.glob("*.sql"):
            try:
                if "notifications" in f.read_text(encoding="utf-8", errors="ignore").lower():
                    notif_found = True
                    break
            except Exception:
                pass
    checks.append((
        notif_found,
        "US-4.3 Meldingen",
        "notifications tabel gevonden in migraties",
        "US-4.3: notifications tabel ontbreekt in migraties"
    ))

    # US-3b Meekijker onboarding — is er een viewer-specifieke onboarding flow?
    viewer_onboarding_found = False
    viewer_keywords = ["meekijker", "viewer_onboarding", "AcceptInvitation", "acceptinvitation"]
    invite_view = PORTAAL_ROOT / "src" / "views" / "AcceptInvitation.vue"
    if invite_view.exists():
        try:
            invite_content = invite_view.read_text(encoding="utf-8", errors="ignore").lower()
            # Controleer of het onderscheid maakt tussen viewer/admin bij accepteren
            viewer_onboarding_found = "viewer" in invite_content or "rol" in invite_content or "role" in invite_content
        except Exception:
            pass
    checks.append((
        viewer_onboarding_found,
        "US-3b Meekijker onboarding",
        "viewer rol verwerkt in uitnodigingsflow",
        "US-3b: AcceptInvitation.vue mist rol-bewustzijn voor meekijker vs mantelzorger onboarding"
    ))

    # US-5.5/5.6: Rolbeheer — check op ACTIEVE rolwijziging UI (niet alleen DB-queries)
    role_change_found = False
    role_ui_patterns = ["changeRole", "updateRole", "update_role", "setRole", "rolChange", "rolBeheer"]
    for root in [PORTAAL_ROOT, APP_ROOT]:
        if not root.exists():
            continue
        for ext in ["*.vue", "*.js", "*.ts", "*.tsx"]:
            for f in root.rglob(ext):
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    if any(p in content for p in role_ui_patterns):
                        role_change_found = True
                        break
                except Exception:
                    pass
            if role_change_found:
                break
        if role_change_found:
            break
    checks.append((
        role_change_found,
        "US-5.5/5.6 Rolbeheer UI",
        "rolwijziging UI gevonden in portaal/app",
        "US-5.5/5.6: Rol upgrade/downgrade (viewer↔admin) nog niet geïmplementeerd in portaal/app UI"
    ))

    # US-7.1: Offline detectie — check op bridge offline handling
    offline_found = False
    for root in [PORTAAL_ROOT, APP_ROOT]:
        if not root.exists():
            continue
        for ext in ["*.js", "*.ts", "*.vue", "*.tsx"]:
            for f in root.rglob(ext):
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    if "offline" in content.lower() or "bridge_offline" in content.lower() or \
                       "last_seen" in content.lower():
                        offline_found = True
                        break
                except Exception:
                    pass
            if offline_found:
                break
        if offline_found:
            break
    checks.append((
        offline_found,
        "US-7.1 Bridge offline detectie",
        "offline detectie logica gevonden in portaal/app",
        "US-7.1: Bridge offline detectie nog niet geïmplementeerd"
    ))

    # Family board (US uit app-design)
    family_board_found = False
    if migrations_dir.exists():
        for f in migrations_dir.glob("*.sql"):
            try:
                if "family_board" in f.read_text(encoding="utf-8", errors="ignore").lower():
                    family_board_found = True
                    break
            except Exception:
                pass
    checks.append((
        family_board_found,
        "Familie board",
        "family_board_messages tabel gevonden in migraties",
        "Familie board: family_board_messages tabel ontbreekt in migraties"
    ))

    for found, label, ok_msg, fail_msg in checks:
        if found:
            ok()
        else:
            todo(f"{fail_msg}")


def check_adr_status():
    """Check 2f: ADR-beslissingen die actie vereisen — zijn ze doorgevoerd?"""
    print("\n--- 2f. ADR actiestatus ---")

    # ADR-002: Portaal + app samenvoegen tot één Vue 3 PWA
    # Check voortgang: TabBar aanwezig = merge in uitvoering
    app_exists = APP_ROOT.exists()
    portaal_exists = PORTAAL_ROOT.exists()
    tabbar_exists = (PORTAAL_ROOT / "src" / "components" / "TabBar.vue").exists()
    pwa_configured = (PORTAAL_ROOT / "vite.config.js").exists() and \
                     "vite-plugin-pwa" in (PORTAAL_ROOT / "vite.config.js").read_text(encoding="utf-8", errors="ignore") \
                     if (PORTAAL_ROOT / "vite.config.js").exists() else False

    app_archived = (APP_ROOT / ".archived").exists()

    if not portaal_exists:
        pass  # Niet van toepassing
    elif (not app_exists or app_archived) and tabbar_exists and pwa_configured:
        ok()  # Volledig afgerond
    elif (not app_exists or app_archived):
        ok()  # App gearchiveerd — merge klaar
    elif tabbar_exists and pwa_configured:
        todo("ADR-002: Merge bijna klaar — tab-navigatie ✅, PWA ✅, archiveer nog gerustthuis-app op GitHub")
    elif tabbar_exists and not pwa_configured:
        todo("ADR-002: Merge in uitvoering — tab-navigatie ✅, PWA configuratie (vite-plugin-pwa) nog open")
    elif not tabbar_exists:
        todo("ADR-002: gerustthuis-portaal en gerustthuis-app bestaan nog als aparte repos — samenvoegen naar één Vue 3 PWA staat open")

    # ADR-003: Tweede integratie na Hue (IKEA Dirigera) — is er al een ikea Edge Function?
    functions_dir = SUPABASE_ROOT / "supabase" / "functions"
    if functions_dir.exists():
        ikea_fn = functions_dir / "ikea-sync-state"
        if not ikea_fn.exists():
            todo("ADR-003: IKEA Dirigera is prioriteit 1 na Hue — ikea-sync-state Edge Function ontbreekt nog")
        else:
            ok()


def check_routes():
    """Check 2e: Routes in portaal.md bestaan in router.js"""
    print("\n--- 2e. Routes (docs → code) ---")
    portaal_doc = REPO_ROOT / "docs" / "architecture" / "portaal.md"
    if not portaal_doc.exists():
        risk("docs/architecture/portaal.md niet gevonden")
        return

    router_file = PORTAAL_ROOT / "src" / "router.js"
    if not router_file.exists():
        router_file = PORTAAL_ROOT / "src" / "router" / "index.js"
    if not router_file.exists():
        risk(f"Router niet gevonden in {PORTAAL_ROOT}/src/")
        return

    router_paths = set(re.findall(r"path:\s*['\"]([^'\"]+)['\"]",
                                   router_file.read_text(encoding="utf-8", errors="ignore")))
    doc_routes   = set(re.findall(r'`(/[^`\s]*)`',
                                   portaal_doc.read_text(encoding="utf-8", errors="ignore")))

    for route in sorted(doc_routes):
        normalized = re.sub(r':[^/]+', ':param', route)
        router_norm = {re.sub(r':[^/]+', ':param', r) for r in router_paths}
        if normalized in router_norm:
            ok()
        else:
            todo(f"Route `{route}` staat in portaal.md maar NIET in router.js")

    for route in router_paths:
        normalized = re.sub(r':[^/]+', ':param', route)
        doc_norm = {re.sub(r':[^/]+', ':param', r) for r in doc_routes}
        if normalized not in doc_norm:
            risk(f"Route `{route}` bestaat in router.js maar staat niet in portaal.md")


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORIE 3: CODE KWALITEIT & SECURITY — externe audit bevindingen
# ══════════════════════════════════════════════════════════════════════════════

def check_security():
    """Check 3a: Bekende security-problemen (bevestigd door externe review)"""
    print("\n--- 3a. Security ---")

    # CORS staat op '*' — alle domeinen toegestaan
    cors_file = SUPABASE_ROOT / "supabase" / "functions" / "_shared" / "cors.ts"
    if cors_file.exists():
        try:
            cors_content = cors_file.read_text(encoding="utf-8", errors="ignore")
            if "'*'" in cors_content or '"*"' in cors_content:
                problem("CORS staat op `'*'` in `_shared/cors.ts` — zet op specifieke domeinen (gerustthuis.nl, localhost)")
            else:
                ok()
        except Exception:
            pass
    else:
        risk("_shared/cors.ts niet gevonden")

    # Debug-logging van credentials in hue-token-exchange
    hue_fn = SUPABASE_ROOT / "supabase" / "functions" / "hue-token-exchange" / "index.ts"
    if hue_fn.exists():
        try:
            lines = hue_fn.read_text(encoding="utf-8", errors="ignore").splitlines()
            for i, line in enumerate(lines, 1):
                if "console.log" in line and any(k in line for k in ["CLIENT_ID", "CLIENT_SECRET", "SECRET", "client_id", "client_secret"]):
                    problem(f"`hue-token-exchange/index.ts` regel {i}: console.log met (deel van) credential — verwijder voor productie")
                    break
            else:
                ok()
        except Exception:
            pass


def check_tests():
    """Check 3b: Testen aanwezig per repo?"""
    print("\n--- 3b. Tests per repo ---")

    ADMIN_ROOT = PROJECT_ROOT / "gerustthuis-admin_portal"
    repos_to_check = [
        ("gerustthuis-portaal", PORTAAL_ROOT),
        ("gerustthuis-app",     APP_ROOT),
        ("gerustthuis-admin",   ADMIN_ROOT),
    ]

    for name, root in repos_to_check:
        if not root.exists():
            continue
        has_config = (
            list(root.glob("vitest.config.*")) or
            list(root.glob("jest.config.*")) or
            list(root.glob("playwright.config.*"))
        )
        has_test_files = (
            list(root.rglob("*.test.ts")) or
            list(root.rglob("*.test.js")) or
            list(root.rglob("*.spec.ts")) or
            list(root.rglob("*.spec.js"))
        )
        # Exclude node_modules
        has_test_files = [f for f in has_test_files if "node_modules" not in str(f)]

        if has_config or has_test_files:
            ok()
        else:
            todo(f"`{name}`: geen tests aanwezig — voeg Vitest toe (unit tests voor z-scores, auth flows, edge cases)")


def check_code_quality():
    """Check 3c: Code kwaliteitsmetrieken (bevestigd door externe review)"""
    print("\n--- 3c. Code kwaliteit ---")

    # TypeScript in portaal?
    if PORTAAL_ROOT.exists():
        tsconfig = PORTAAL_ROOT / "tsconfig.json"
        if not tsconfig.exists():
            risk("gerustthuis-portaal heeft geen TypeScript (tsconfig.json ontbreekt) — alle code is .js (verhoogt risico bij refactoring)")
        else:
            ok()

    # Fat views (> 400 regels)
    views_dir = PORTAAL_ROOT / "src" / "views"
    if views_dir.exists():
        for vue_file in views_dir.glob("*.vue"):
            try:
                line_count = vue_file.read_text(encoding="utf-8", errors="ignore").count("\n")
                if line_count > 400:
                    risk(f"portaal `{vue_file.name}`: {line_count} regels — te groot, splits in subcomponenten")
                else:
                    ok()
            except Exception:
                pass

    # supabase.js — god-file?
    supabase_svc = PORTAAL_ROOT / "src" / "services" / "supabase.js"
    if supabase_svc.exists():
        try:
            line_count = supabase_svc.read_text(encoding="utf-8", errors="ignore").count("\n")
            if line_count > 300:
                risk(f"portaal `src/services/supabase.js`: {line_count} regels — mixt auth, data en domain-logica (god-file). Splits of migreer naar Pinia stores")
            else:
                ok()
        except Exception:
            pass

    # Pinia check — portaal gebruikt reactive() ipv Pinia?
    if PORTAAL_ROOT.exists():
        has_pinia = (PORTAAL_ROOT / "node_modules" / "pinia").exists()
        package_json = PORTAAL_ROOT / "package.json"
        if package_json.exists():
            try:
                pkg = package_json.read_text(encoding="utf-8", errors="ignore")
                has_pinia = "pinia" in pkg
            except Exception:
                pass
        if not has_pinia:
            risk("gerustthuis-portaal gebruikt geen Pinia — state management via kale `reactive()`. Migreer naar Pinia (consistent met Vue 3 best practices)")
        else:
            ok()


# ══════════════════════════════════════════════════════════════════════════════
# RAPPORT SCHRIJVEN
# ══════════════════════════════════════════════════════════════════════════════

def write_report():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# GerustThuis Project Health Report",
        "",
        f"_Automatisch gegenereerd op {timestamp}_",
        "",
        "> Dit rapport is de centrale actielijst voor het project.",
        "> **❌ Problemen** moeten direct opgelost worden.",
        "> **📋 Niet gebouwd** zijn openstaande backlog items.",
        "> **⚠️ Risico** zijn zaken die aandacht verdienen.",
        "",
        "---",
        "",
    ]

    if problems:
        lines += [f"## ❌ Problemen ({len(problems)}) — moet opgelost worden", ""]
        for p in problems:
            lines.append(f"- {p}")
        lines.append("")

    if backlog:
        lines += [f"## 📋 Niet gebouwd ({len(backlog)}) — backlog items", ""]
        for b in backlog:
            lines.append(f"- {b}")
        lines.append("")

    if risks:
        lines += [f"## ⚠️ Risico ({len(risks)}) — controleer dit", ""]
        for r in risks:
            lines.append(f"- {r}")
        lines.append("")

    if not problems and not backlog and not risks:
        lines += ["## ✅ Alles in orde", "", "Geen openstaande issues gevonden.", ""]

    # Vaste sectie — bevindingen die niet automatisch detecteerbaar zijn
    lines += [
        "---",
        "",
        "## 📎 Handmatige audit bevindingen",
        "",
        "_Externe code review (feb 2026). Verwijder een item als het is opgelost._",
        "",
        "### Security",
        "- **Race condition rate limiting** (`waitlist-signup`): upsert + count check is niet-atomair. Vervang door `UPDATE ... RETURNING` of advisory lock in PostgreSQL.",
        "",
        "### Code kwaliteit",
        "- **Input-validatie portaal**: formulieren valideren niet op lengte/formaat/inhoud. Website doet dit wél (Vee-validate + Zod). Voeg validatie toe aan portaal-formulieren.",
        "- **Duplicatie portaal ↔ app**: z-score berekeningen, activiteitsdata-formattering en Hue-logica staan in beide repos. Geen shared packages. Wordt opgelost bij ADR-002 merge.",
        "- **Pinia**: portaal gebruikt `reactive()` voor global state. Migreer naar Pinia voor betere DevTools-ondersteuning en consistency.",
        "",
        "### Scorekaart externe review (startpunt)",
        "",
        "| Repository | Score | Sterk | Aandacht |",
        "|------------|-------|-------|---------|",
        "| gerustthuis-docs | 8.5/10 | ADR-kwaliteit, volledigheid | Migraties 023-030 niet gedocumenteerd |",
        "| gerustthuis-app | 7.5/10 | TypeScript strict, component-design | Geen tests, veel mock data |",
        "| gerustthuis-website | 8/10 | Productie-klaar, SEO, validatie | Geen tests |",
        "| gerustthuis-supabase | 6.5/10 | Migratie-kwaliteit, RLS | Security-lekken, CORS, race conditions |",
        "| gerustthuis-portaal | 4.5/10 | Data-science logica (z-scores) | Geen TS, fat components, geen tests |",
        "| gerustthuis-admin | 6/10 | Schone architectuur voor intern tool | Hardcoded email-allowlist, beperkt |",
        "",
    ]

    total = len(problems) + len(backlog) + len(risks)
    lines += [
        "---",
        "",
        f"_Totaal: {len(problems)} problemen · {len(backlog)} backlog · {len(risks)} risico · {ok_count} checks OK_",
    ]

    report_file = REPO_ROOT / "docs" / "consistency-report.md"
    report_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  Rapport opgeslagen: {report_file.relative_to(REPO_ROOT)}")
    return len(problems)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("GerustThuis Project Health Dashboard")
    print("=" * 45)
    print("\n=== CATEGORIE 1: PROBLEMEN ===")
    check_internal_links()
    check_forbidden_columns()
    check_tables_in_migrations()

    print("\n=== CATEGORIE 2: NIET GEBOUWD ===")
    check_portaal_views()
    check_edge_functions()
    check_app_pages()
    check_user_story_features()
    check_adr_status()
    check_routes()

    print("\n=== CATEGORIE 3: CODE KWALITEIT & SECURITY ===")
    check_security()
    check_tests()
    check_code_quality()

    write_report()

    print("\n" + "=" * 45)
    print(f"Problemen:     {len(problems)}")
    print(f"Niet gebouwd:  {len(backlog)}")
    print(f"Risico:        {len(risks)}")
    print(f"OK:            {ok_count}")

    import sys as _sys
    _sys.exit(1 if problems else 0)
