#!/usr/bin/env bash
#
# uninstall.sh — Remove tudo que o install.sh instalou
# Suporta: Arch/Manjaro, Debian/Ubuntu/Mint, Fedora/RHEL, openSUSE, Bazzite/Silverblue
#
# Uso:
#   chmod +x uninstall.sh
#   ./uninstall.sh
#
set -uo pipefail

VERMELHO="\033[0;31m"
VERDE="\033[0;32m"
AMARELO="\033[1;33m"
CIANO="\033[0;36m"
RESET="\033[0m"

info()  { echo -e "${CIANO}[INFO]${RESET}  $1"; }
ok()    { echo -e "${VERDE}[OK]${RESET}    $1"; }
aviso() { echo -e "${AMARELO}[AVISO]${RESET} $1"; }
erro()  { echo -e "${VERMELHO}[ERRO]${RESET}  $1"; }

# ---------------------------------------------------------------------------
# Detectar distro
# ---------------------------------------------------------------------------
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO_ID="${ID:-desconhecido}"
    DISTRO_LIKE="${ID_LIKE:-}"
else
    erro "Não foi possível detectar sua distribuição."
    exit 1
fi

echo ""
echo -e "${CIANO}╔══════════════════════════════════════════╗${RESET}"
echo -e "${CIANO}║       DLC Unlocker — Desinstalador       ║${RESET}"
echo -e "${CIANO}╚══════════════════════════════════════════╝${RESET}"
echo ""

info "Distribuição: ${PRETTY_NAME:-$DISTRO_ID}"

# Detecta sistema imutável
IMUTAVEL=false
if command -v rpm-ostree &>/dev/null; then
    IMUTAVEL=true
    aviso "Sistema imutável detectado (rpm-ostree)."
fi

SUDO=""
[ "$(id -u)" -ne 0 ] && SUDO="sudo"

# ---------------------------------------------------------------------------
# Pergunta sobre Python, vai ter genta marcando sim, melhor deixar o python no pc deles
# ---------------------------------------------------------------------------
echo ""
echo -e "${AMARELO}══════════════════════════════════════════${RESET}"
echo -e "${AMARELO}  ATENÇÃO: Remoção do Python${RESET}"
echo -e "${AMARELO}══════════════════════════════════════════${RESET}"
echo ""
echo "  O Python pode ser usado por outros programas no sistema."
echo "  Removê-lo pode quebrar ferramentas do sistema."
echo ""
echo -e "  ${VERDE}[s]${RESET} Sim, remover Python e pip também"
echo -e "  ${CIANO}[n]${RESET} Não, manter Python e pip  ${AMARELO}(recomendado)${RESET}"
echo ""
read -rp "  Sua escolha [s/N]: " REMOVER_PYTHON
echo ""

REMOVER_PYTHON="${REMOVER_PYTHON,,}"
if [[ "$REMOVER_PYTHON" == "s" || "$REMOVER_PYTHON" == "sim" ]]; then
    REMOVER_PYTHON=true
    aviso "Python e pip serão removidos."
else
    REMOVER_PYTHON=false
    ok "Python e pip serão mantidos."
fi

# ---------------------------------------------------------------------------
# Remove pacotes pip
# ---------------------------------------------------------------------------
PYTHON_BIN="$(command -v python3 || true)"

pip_uninstall() {
    local pkg="$1"
    if [ -n "$PYTHON_BIN" ]; then
        "$PYTHON_BIN" -m pip uninstall -y "$pkg" --break-system-packages 2>/dev/null \
            || "$PYTHON_BIN" -m pip uninstall -y "$pkg" 2>/dev/null \
            || aviso "  $pkg — não encontrado via pip (pode já estar ausente)."
    fi
}

info "Removendo pacotes pip..."
for pkg in customtkinter beautifulsoup4 requests Pillow; do
    pip_uninstall "$pkg"
done
ok "Pacotes pip removidos."

# ---------------------------------------------------------------------------
# Remove pacotes de sistema por distro
# ---------------------------------------------------------------------------

remover_arch() {
    info "Removendo pacotes via pacman..."
    $SUDO pacman -Rns --noconfirm \
        python-requests python-beautifulsoup4 python-pillow tk 2>/dev/null || true

    if [ "$REMOVER_PYTHON" = true ]; then
        $SUDO pacman -Rns --noconfirm python python-pip 2>/dev/null || true
    fi
}

remover_debian() {
    info "Removendo pacotes via apt..."
    $SUDO apt remove -y \
        python3-tk \
        python3-requests \
        python3-bs4 \
        python3-pil \
        python3-pil.imagetk 2>/dev/null || true

    if [ "$REMOVER_PYTHON" = true ]; then
        $SUDO apt remove -y python3 python3-pip 2>/dev/null || true
    fi

    $SUDO apt autoremove -y
}

remover_fedora() {
    info "Removendo pacotes via dnf..."
    $SUDO dnf remove -y \
        python3-tkinter \
        python3-requests \
        python3-beautifulsoup4 \
        python3-pillow 2>/dev/null || true

    if [ "$REMOVER_PYTHON" = true ]; then
        $SUDO dnf remove -y python3 python3-pip 2>/dev/null || true
    fi
}

remover_opensuse() {
    info "Removendo pacotes via zypper..."
    $SUDO zypper --non-interactive remove \
        python3-tk \
        python3-requests \
        python3-beautifulsoup4 \
        python3-Pillow 2>/dev/null || true

    if [ "$REMOVER_PYTHON" = true ]; then
        $SUDO zypper --non-interactive remove python3 python3-pip 2>/dev/null || true
    fi
}

remover_imutavel() {
    aviso "Sistema imutável — pacotes do sistema não serão removidos via rpm-ostree."
    info  "Apenas os pacotes pip foram removidos acima."
    echo ""
    echo -e "  Se você instalou ${CIANO}python3-tkinter${RESET} via rpm-ostree, remova manualmente:"
    echo -e "  ${CIANO}rpm-ostree uninstall python3-tkinter${RESET}"
    echo -e "  (reinicie após a remoção)"
}

# Escolha do método de remoção
if $IMUTAVEL; then
    remover_imutavel
else
    case "$DISTRO_ID" in
        arch|manjaro|endeavouros|garuda|cachyos)
            remover_arch ;;
        debian|ubuntu|linuxmint|pop|elementary|zorin|kali)
            remover_debian ;;
        fedora|rhel|centos|rocky|almalinux)
            remover_fedora ;;
        opensuse*|sles)
            remover_opensuse ;;
        *)
            aviso "Distro '$DISTRO_ID' não reconhecida diretamente. Tentando via ID_LIKE..."
            case "$DISTRO_LIKE" in
                *arch*)          remover_arch ;;
                *debian*|*ubuntu*) remover_debian ;;
                *fedora*|*rhel*) remover_fedora ;;
                *suse*)          remover_opensuse ;;
                *)
                    erro "Não sei remover pacotes nesta distro automaticamente."
                    erro "Remova manualmente: tkinter/tk, requests, beautifulsoup4, Pillow."
                    exit 1
                    ;;
            esac
            ;;
    esac
fi

echo ""
ok "Desinstalação concluída."
echo ""