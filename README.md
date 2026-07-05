# DLC Unlocker

![Screenshot do projeto](https://i.imgur.com/PRTLrT1.png)

Este projeto é uma ferramenta em Python para gerenciar downloads e instalação de DLCs do The Sims 4, além de integrar um desbloqueio/assistente para o EA App em prefixes Wine/Steam/Lutris/Bottles.

## O que faz

- Exibe uma interface gráfica para baixar DLCs via torrents magnet.
- Organiza os downloads em uma pasta escolhida pelo usuário.
- Permite instalar e desinstalar um unlocker para o EA App em prefixes compatíveis.
- Gerencia arquivos de configuração usados pelo processo de desbloqueio.

## Requisitos

Antes de executar, certifique-se de ter instalado:

- Python 3
- Tkinter
- customtkinter
- Pillow
- libtorrent
- unzip, p7zip e unrar

No Linux, a forma mais simples de instalar tudo é rodar:

```bash
chmod +x install.sh
./install.sh
```

## Como usar

1. Entre na pasta do projeto.
2. Execute:

```bash
python3 main.py
```

3. Na interface, escolha a pasta de downloads e inicie os downloads desejados.
4. Se necessário, use o painel de unlocker para instalar ou remover os arquivos de configuração no prefixo selecionado.

## Estrutura principal

- main.py: ponto de entrada da interface.
- install.sh: instala dependências do sistema e Python.
- core/: módulos principais do desbloqueio e da interface.
- configs/: arquivos de configuração persistentes.
- logs/: logs da execução.

## Observações

- Este projeto depende de um ambiente compatível com Wine/Steam/EA App.
- O uso de torrents e conteúdo de terceiros pode variar conforme a disponibilidade dos arquivos.
- Utilize com responsabilidade e somente em ambientes onde você tenha permissão para modificar os arquivos do jogo.

## Licença

Este projeto é fornecido como está, sem garantias explícitas ou implícitas.
