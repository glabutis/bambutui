#!/usr/bin/env bash
set -e

INSTALL_DIR="$HOME/.local/share/bambutui"
BIN_DIR="$HOME/.local/bin"
REPO="https://github.com/YOUR_USERNAME/bambutui"

# ── Check Python ──────────────────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Error: Python 3.9+ is required but not found." >&2
    exit 1
fi

PY_VERSION=$($PYTHON -c "import sys; print(sys.version_info[:2])")
# Quick version check (works for tuples printed as "(3, 9)")
if $PYTHON -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
    :
else
    echo "Error: Python 3.9 or newer is required. Found: $($PYTHON --version)" >&2
    exit 1
fi

# ── Set up isolated venv ──────────────────────────────────────────────────────
echo "→ Installing bambutui to $INSTALL_DIR"
rm -rf "$INSTALL_DIR"
$PYTHON -m venv "$INSTALL_DIR/venv"

"$INSTALL_DIR/venv/bin/pip" install --upgrade pip -q
"$INSTALL_DIR/venv/bin/pip" install "git+$REPO.git" -q

# ── Create launcher script ────────────────────────────────────────────────────
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/bambutui" <<EOF
#!/usr/bin/env bash
exec "$INSTALL_DIR/venv/bin/python" -m bambutui "\$@"
EOF
chmod +x "$BIN_DIR/bambutui"

# ── PATH hint ─────────────────────────────────────────────────────────────────
echo ""
echo "✓ bambutui installed successfully!"
echo ""

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "  Add this to your shell profile (~/.zshrc or ~/.bashrc) to use 'bambutui' anywhere:"
    echo ""
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "  Then reload your shell:  source ~/.zshrc"
    echo ""
fi

echo "  Run with:  bambutui"
echo "  Or:        $INSTALL_DIR/venv/bin/python -m bambutui"
