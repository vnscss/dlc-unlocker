<div align="center">

# 🎮 DLC Unlocker

**Gerenciador gráfico de DLCs do The Sims 4 para Linux**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=flat-square&logo=linux)
![License](https://img.shields.io/badge/License-As--is-gray?style=flat-square)

</div>

---

<!-- Substitua pela URL real da sua screenshot -->
![Screenshot](https://i.imgur.com/qzyTwHG.png)

---

## O que é

DLC Unlocker é uma interface gráfica em Python para baixar, extrair e instalar DLCs do The Sims 4 no Linux. Também integra um gerenciador do EA App Unlocker para prefixes Wine, Steam, Lutris e Bottles.

---

## Funcionalidades

- Download direto via Mediafire com barra de progresso
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

---

## Instalação
abra o dlc-unlocker no terminal e rode para instalar as dependências.
```bash
chmod +x install.sh
./install.sh
```
depois de instalar as dependências, rode para abrir o programa.
```bash
python3 main.py
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


## Screenshots

<!-- Adicione suas screenshots aqui -->

| Interface principal | EA Unlocker | Extração |
|---|---|---|
| ![main](https://i.imgur.com/0rKU67W.png) | ![unlocker](https://i.imgur.com/17UNqjl.png) | ![zip](https://i.imgur.com/fAZd0B5.png) |

---

## Observações

- O cancelamento de download mantém o arquivo parcial no disco para retomada futura.
- A detecção da pasta do Sims 4 é automática via `libraryfolders.vdf` da Steam, incluindo bibliotecas externas.
- O EA Unlocker suporta prefixes de Wine nativo, Lutris, Bottles e Steam (Proton).

---

<div align="center">

*A pirataria surge quando o valor de uma obra encontra a realidade de quem não pode alcançá-la.*

</div>
