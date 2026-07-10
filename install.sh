#!/usr/bin/env bash
#
# install.sh - Instala tudo que o main.py precisa
# Suporta: Arch/Manjaro, Debian/Ubuntu/Mint, Fedora/RHEL, openSUSE, Alpine
#
# Uso:
#   chmod +x install.sh
#   ./install.sh
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
# Instalar dependências de sistema por distro
# ---------------------------------------------------------------------------
instalar_arch() {
    info "Instalando pacotes via pacman..."
    $SUDO pacman -Sy --needed --noconfirm \
        python python-pip tk python-pillow unzip p7zip unrar
}

instalar_debian() {
    info "Instalando pacotes via apt..."
    $SUDO apt update
    $SUDO apt install -y \
        python3 python3-pip python3-tk python3-pil unzip p7zip-full unrar
}

instalar_fedora() {
    info "Instalando pacotes via dnf..."
    $SUDO dnf install -y \
        python3 python3-pip python3-tkinter python3-pillow unzip p7zip unrar || true
}

instalar_opensuse() {
    info "Instalando pacotes via zypper..."
    $SUDO zypper --non-interactive install \
        python3 python3-pip python3-tk python3-Pillow unzip p7zip unrar || true
}

instalar_alpine() {
    info "Instalando pacotes via apk..."
    $SUDO apk add --no-cache \
        python3 py3-pip python3-tkinter py3-pillow unzip p7zip unrar || true
}

case "$DISTRO_ID" in
    arch|manjaro|endeavouros|garuda)
        instalar_arch
        ;;
    debian|ubuntu|linuxmint|pop|elementary|zorin)
        instalar_debian
        ;;
    fedora|rhel|centos|rocky|almalinux)
        instalar_fedora
        ;;
    opensuse*|sles)
        instalar_opensuse
        ;;
    alpine)
        instalar_alpine
        ;;
    *)
        aviso "Distro '$DISTRO_ID' não reconhecida diretamente."
        case "$DISTRO_LIKE" in
            *arch*)    instalar_arch ;;
            *debian*)  instalar_debian ;;
            *fedora*|*rhel*) instalar_fedora ;;
            *suse*)    instalar_opensuse ;;
            *)
                erro "Não sei como instalar pacotes nesta distro automaticamente."
                erro "Instale manualmente: python3, pip, tkinter/tk e Pillow."
                exit 1
                ;;
        esac
        ;;
esac

ok "Dependências de sistema instaladas (ou já presentes)."

# ---------------------------------------------------------------------------
# Descobrir binário do Python e pip
# ---------------------------------------------------------------------------
PYTHON_BIN="$(command -v python3 || true)"
if [ -z "$PYTHON_BIN" ]; then
    erro "python3 não encontrado após a instalação. Abortando."
    exit 1
fi
ok "Usando: $PYTHON_BIN ($($PYTHON_BIN --version))"

pip_install() {
    "$PYTHON_BIN" -m pip install --upgrade "$1" --break-system-packages 2>/dev/null \
        || "$PYTHON_BIN" -m pip install --upgrade "$1" --user 2>/dev/null \
        || "$PYTHON_BIN" -m pip install --upgrade "$1"
}

# ---------------------------------------------------------------------------
# Garantir pip atualizado
# ---------------------------------------------------------------------------
info "Atualizando pip..."
pip_install pip >/dev/null 2>&1 || aviso "Não consegui atualizar o pip, seguindo mesmo assim."

# ---------------------------------------------------------------------------
# Instalar customtkinter
# ---------------------------------------------------------------------------
info "Instalando customtkinter via pip..."
if pip_install customtkinter; then
    ok "customtkinter instalado."
else
    erro "Falha ao instalar customtkinter via pip."
    exit 1
fi

# ---------------------------------------------------------------------------
# Verificar BeautifulSoup4 (bs4)
# ---------------------------------------------------------------------------
info "Verificando módulo BeautifulSoup4 (bs4)..."
if "$PYTHON_BIN" -c "import bs4" 2>/dev/null; then
    ok "BeautifulSoup4 já está disponível para o Python."
else
    aviso "BeautifulSoup4 não encontrado. Tentando via pip..."
    if pip_install beautifulsoup4; then
        if "$PYTHON_BIN" -c "import bs4" 2>/dev/null; then
            ok "BeautifulSoup4 instalado via pip."
        else
            erro "BeautifulSoup4 foi instalado via pip mas não importa corretamente."
        fi
    else
        erro "Não foi possível instalar o BeautifulSoup4 automaticamente."
        erro "Tente instalar manualmente: pip install beautifulsoup4"
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Verificar requests
# ---------------------------------------------------------------------------
info "Verificando módulo requests..."
if "$PYTHON_BIN" -c "import requests" 2>/dev/null; then
    ok "requests já está disponível para o Python."
else
    aviso "requests não encontrado. Tentando via pip..."
    if pip_install requests; then
        if "$PYTHON_BIN" -c "import requests" 2>/dev/null; then
            ok "requests instalado via pip."
        else
            erro "requests foi instalado via pip mas não importa corretamente."
        fi
    else
        erro "Não foi possível instalar o requests automaticamente."
        erro "Tente instalar manualmente: pip install requests"
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
# Verificar Pillow
# ---------------------------------------------------------------------------
info "Verificando módulo Pillow (PIL)..."
if "$PYTHON_BIN" -c "import PIL" 2>/dev/null; then
    ok "Pillow já está disponível para o Python."
else
    aviso "Pillow não encontrado via pacote de sistema. Tentando via pip..."
    if pip_install Pillow; then
        if "$PYTHON_BIN" -c "import PIL" 2>/dev/null; then
            ok "Pillow instalado via pip."
        else
            erro "Pillow foi instalado via pip mas não importa corretamente."
        fi
    else
        erro "Não foi possível instalar o Pillow automaticamente."
        erro "Tente instalar manualmente o pacote 'Pillow' (pip) ou 'python-pillow' (sistema)."
    fi
fi

echo ""
ok "Instalação concluída!"
echo -e "${AZUL}Para rodar o programa:${RESET} python3 main.py"