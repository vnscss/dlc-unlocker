<div align="center">

# 🎮 DLC Unlocker

**Gerenciador gráfico de DLCs do The Sims 4 para Linux**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=flat-square&logo=linux)
![License](https://img.shields.io/badge/License-As--is-gray?style=flat-square)

</div>

---

<!-- Substitua pela URL real da sua screenshot -->
![Screenshot](assets/png.png)

---

## O que é

DLC Unlocker é uma interface gráfica em Python para baixar, extrair e instalar DLCs do The Sims 4 no Linux. Também integra um gerenciador do EA App Unlocker para prefixes Wine, Steam, Lutris e Bottles.

---

## Funcionalidades

- Download direto via Mediafire com barra de progresso e suporte a cancelamento
- Filtro em tempo real por nome ou tipo de pacote
- Extração automática dos `.zip` com progresso por arquivo
- Movimentação das pastas extraídas para o local correto do jogo (detectado automaticamente via Steam)
- Gerenciador do EA Unlocker — instala, desinstala e abre a pasta de configs no prefix correto
- Splash screen configurável
- Logs persistentes em `logs/dlc_manager.log`
- Configuração salva entre sessões

---

## Requisitos

- Python 3.10 ou superior
- Steam com The Sims 4 instalado
- Wine, Lutris, Bottles ou Steam Play (para o EA Unlocker)

---

## Instalação

```bash
git clone https://github.com/seu-usuario/dlc-unlocker.git
cd dlc-unlocker
chmod +x install.sh
./install.sh
```

O `install.sh` detecta a sua distribuição automaticamente e instala as dependências:

| Distro | Gerenciador |
|---|---|
| Arch / Manjaro | `pacman` |
| Ubuntu / Debian / Mint | `apt` |
| Fedora / RHEL | `dnf` |
| openSUSE | `zypper` |

---

## Como usar

```bash
python3 main.py
```

### Fluxo recomendado

```
1. Escolha a pasta de destino dos downloads
2. Selecione os DLCs que quer baixar e clique em ⬇ Baixar
3. Após o download, clique em 📦 Extrair
4. Após a extração, clique em 📂 Mover
5. Use 🛠 EA Unlocker para ativar os DLCs no jogo
```

---

## Estrutura do projeto

```
dlc-unlocker/
├── main.py               # Ponto de entrada
├── install.sh            # Instalador de dependências
├── assets/               # Imagens da interface
│   ├── _.jpeg
│   ├── __.jpeg
│   └── png.png
├── core/                 # Módulos internos
│   ├── ea_unlocker.py    # Lógica do EA Unlocker
│   ├── splash.py         # Tela de splash
│   ├── config.ini        # Config do unlocker
│   ├── g_TS4.ini         # Config do jogo
│   └── ea_app/
│       └── version.dll
├── configs/              # Configurações do app (gerado automaticamente)
│   └── config.json
└── logs/                 # Logs de execução (gerado automaticamente)
    └── dlc_manager.log
```

---

## Adicionando novos DLCs

Abra `main.py` e adicione uma entrada na lista `ARQUIVOS`:

```python
{"nome": "GP01 — Outdoor Retreat", "tag": "Game Pack", "mediafire": "https://www.mediafire.com/file/.../file"},
```

Tags disponíveis e suas cores:

| Tag | Cor |
|---|---|
| `Expansion Pack` | Roxo |
| `Game Pack` | — |
| `Stuff Pack` | — |
| `Kit` | — |

---

## Screenshots

<!-- Adicione suas screenshots aqui -->

| Interface principal | EA Unlocker | Extração |
|---|---|---|
| ![main](assets/_.jpeg) | *em breve* | *em breve* |

---

## Observações

- O cancelamento de download mantém o arquivo parcial no disco para retomada futura.
- A detecção da pasta do Sims 4 é automática via `libraryfolders.vdf` da Steam, incluindo bibliotecas externas.
- O EA Unlocker suporta prefixes de Wine nativo, Lutris, Bottles e Steam (Proton).

---

<div align="center">

*A pirataria surge quando o valor de uma obra encontra a realidade de quem não pode alcançá-la.*

</div>