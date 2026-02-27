#!/bin/bash
# Installeer git hooks voor gerustthuis-docs
# Uitvoeren vanuit de gerustthuis-docs root: bash scripts/install-git-hooks.sh

HOOK_DIR=".git/hooks"
PRE_PUSH="$HOOK_DIR/pre-push"

cat > "$PRE_PUSH" << 'EOF'
#!/bin/bash
echo ""
echo "🔍 GerustThuis consistency check..."
python3 scripts/check_consistency.py
STATUS=$?

if [ $STATUS -ne 0 ]; then
  echo ""
  echo "⚠️  Er zijn inconsistenties gevonden in de documentatie."
  echo "   Zie docs/consistency-report.md voor details."
  echo ""
  echo "   Push doorgaan? (problemen worden ook zichtbaar via GitHub Actions)"
  echo "   Druk op Ctrl+C om te annuleren, of wacht 5 seconden..."
  sleep 5
fi

exit 0   # Blokkeer push niet — GitHub Actions pakt het ook op
EOF

chmod +x "$PRE_PUSH"
echo "✅ Pre-push hook geïnstalleerd in $PRE_PUSH"
echo ""
echo "Werking:"
echo "  - Draait bij elke 'git push'"
echo "  - Toont problemen maar blokkeert push niet"
echo "  - GitHub Actions doet de definitieve check na push"
