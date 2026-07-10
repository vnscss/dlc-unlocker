#!/usr/bin/env bash
#
# uninstall.sh - Remove tudo que o install.sh instalou
# Suporta: Arch/Manjaro, Debian/Ubuntu/Mint, Fedora/RHEL, openSUSE, Alpine
#
# Uso:
#   chmod +x uninstall.sh
#   ./uninstall.sh
#
set -uo pipefail

VERMELHO="\033[0;31m"
VERDE="\033[0;32m"
AMARELO="\033[1;33m"
AZUL="\033[0;34m"
RESET="\033[0m"

info()  { echo -e "${AZUL}[INFO]${RESET} $1"; }
ok()    { echo -e "${VERDE}[OK]${RESET} $1"; }
aviso() { echo -e "${AMARELO}[AVISO]${RESET} $1"; }
erro()  { echo -e "${VERMELHO}[ERRO]${RESET} $1"; }

# ---------------------------------------------------------------------------
# Detectar a distribuição
# ---------------------------------------------------------------------------
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO_ID="${ID:-desconhecido}"
    DISTRO_LIKE="${ID_LIKE:-}"
else
    erro "Não foi possível detectar sua distribuição (/etc/os-release não encontrado)."
    exit 1
fi

info "Distribuição detectada: $DISTRO_ID"

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
fi

# ---------------------------------------------------------------------------
# Descobrir binário do Python
# ---------------------------------------------------------------------------
PYTHON_BIN="$(command -v python3 || true)"

pip_uninstall() {
    if [ -n "$PYTHON_BIN" ]; then
        "$PYTHON_BIN" -m pip uninstall -y "$1" --break-system-packages 2>/dev/null \
            || "$PYTHON_BIN" -m pip uninstall -y "$1" 2>/dev/null \
            || aviso "Não foi possível remover $1 via pip (pode já estar ausente)."
    fi
}

# ---------------------------------------------------------------------------
# Remover pacotes pip instalados pelo install.sh
# ---------------------------------------------------------------------------
info "Removendo pacotes pip: customtkinter, beautifulsoup4, requests, Pillow..."
pip_uninstall customtkinter
pip_uninstall beautifulsoup4
pip_uninstall requests
pip_uninstall Pillow
ok "Pacotes pip removidos."

# ---------------------------------------------------------------------------
# Remover dependências de sistema por distro
# ---------------------------------------------------------------------------
remover_arch() {
    info "Removendo pacotes via pacman..."
    $SUDO pacman -Rns --noconfirm \
        python-pillow unzip p7zip unrar 2>/dev/null || true
    aviso "python, python-pip e tk não foram removidos — podem ser dependências de outros programas."
}

remover_debian() {
    info "Removendo pacotes via apt..."
    $SUDO apt remove -y \
        python3-tk python3-pil unzip p7zip-full unrar 2>/dev/null || true
    $SUDO apt autoremove -y
    aviso "python3 e python3-pip não foram removidos — podem ser dependências de outros programas."
}

remover_fedora() {
    info "Removendo pacotes via dnf..."
    $SUDO dnf remove -y \
        python3-tkinter python3-pillow unzip p7zip unrar 2>/dev/null || true
    aviso "python3 e python3-pip não foram removidos — podem ser dependências de outros programas."
}

remover_opensuse() {
    info "Removendo pacotes via zypper..."
    $SUDO zypper --non-interactive remove \
        python3-tk python3-Pillow unzip p7zip unrar 2>/dev/null || true
    aviso "python3 e python3-pip não foram removidos — podem ser dependências de outros programas."
}

remover_alpine() {
    info "Removendo pacotes via apk..."
    $SUDO apk del \
        python3-tkinter py3-pillow unzip p7zip unrar 2>/dev/null || true
    aviso "python3 e py3-pip não foram removidos — podem ser dependências de outros programas."
}

case "$DISTRO_ID" in
    arch|manjaro|endeavouros|garuda)
        remover_arch
        ;;
    debian|ubuntu|linuxmint|pop|elementary|zorin)
        remover_debian
        ;;
    fedora|rhel|centos|rocky|almalinux)
        remover_fedora
        ;;
    opensuse*|sles)
        remover_opensuse
        ;;
    alpine)
        remover_alpine
        ;;
    *)
        aviso "Distro '$DISTRO_ID' não reconhecida diretamente."
        case "$DISTRO_LIKE" in
            *arch*)    remover_arch ;;
            *debian*)  remover_debian ;;
            *fedora*|*rhel*) remover_fedora ;;
            *suse*)    remover_opensuse ;;
            *)
                erro "Não sei como remover pacotes nesta distro automaticamente."
                erro "Remova manualmente: tkinter/tk, Pillow, unzip, p7zip, unrar."
                exit 1
                ;;
        esac
        ;;
esac

echo ""
ok "Desinstalação concluída."