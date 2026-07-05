import os
import re
import sys
import json
import time
import threading
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, filedialog

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(BASE_DIR / "core"))

import customtkinter as ctk
from splash import SplashScreen
from ea_unlocker import EAUnlocker

try:
    import libtorrent as lt
except ImportError:
    raise SystemExit(
        "O módulo 'libtorrent' não foi encontrado.\n"
        "Rode ./instalar.sh para instalar as dependências do sistema."
    )

# ---------------------------------------------------------------------------
# DADOS
# ---------------------------------------------------------------------------
ARQUIVOS = [
    {"nome": "EP01 — Get to Work",           "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:fbc3461adbc9f48b35d1f9003088515c81d7000e&dn=Sims4_DLC_EP01_Get_to_Work.zip&xl=1694934094&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP02 — Get Together",          "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:7b0ede6c6d8d4b2d1c48118790d80519be786a70&dn=Sims4_DLC_EP02_Get_Together.zip&xl=1717179184&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP03 — City Living",           "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:afb0cedd7ebfb28850b1a42ebe0dd0cdb5075857&dn=Sims4_DLC_EP03_City_Living.zip&xl=2635798353&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP04 — Cats and Dogs",         "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:3b41461c5345a34a0e2f9e2abd2b35aaf0f2ea80&dn=Sims4_DLC_EP04_Cats_and_Dogs.zip&xl=2013068744&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP05 — Seasons",               "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:f794b76b61368de6824383a367df7388e60e552a&dn=Sims4_DLC_EP05_Seasons.zip&xl=1412690473&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP06 — Get Famous",            "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:09d0e446313d238804d4b22780da9e2efa011846&dn=Sims4_DLC_EP06_Get_Famous.zip&xl=2807534837&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP07 — Island Living",         "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:449dbc717ad6f4fefca03b48a407c1df3534fd86&dn=Sims4_DLC_EP07_Island_Living.zip&xl=1446940021&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP08 — Discover University",   "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:ab06359c618a82fbf38d794daf021c2686d63fec&dn=Sims4_DLC_EP08_Discover_University.zip&xl=1618423432&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP09 — Eco Lifestyle",         "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:4b88b6e2c905181232257e7f50e0a6e4d4b11686&dn=Sims4_DLC_EP09_Eco_Lifestyle.zip&xl=1490785679&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP10 — Snowy Escape",          "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:8a492d38640cef3f450f667a7a6a7337cc9ffea5&dn=Sims4_DLC_EP10_Snowy_Escape.zip&xl=1605597860&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP11 — Cottage Living",        "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:6a425f0af1304fbec66e374d6854622eef3728a0&dn=Sims4_DLC_EP11_Cottage_Living.zip&xl=1681100841&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP12 — High School Years",     "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:dcb0fc534ae835df58f9f90b383feb97ee91302d&dn=Sims4_DLC_EP12_High_School_Years.zip&xl=1848263218&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP13 — Growing Together",      "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:0a156f75fb8692e9ea5b137d7038c342704df33c&dn=Sims4_DLC_EP13_Growing_Together.zip&xl=1397798130&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP14 — Horse Ranch",           "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:b2d54a84485119d36050fbc47d1497869b4a2d46&dn=Sims4_DLC_EP14_Horse_Ranch.zip&xl=1852411450&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP15 — For Rent",              "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:ede1f248ca30d952c645ff1b869f17a3fb4b1acc&dn=Sims4_DLC_EP15_For_Rent.zip&xl=1532830000&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP16 — Lovestruck",            "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:01e98b0b7d34284ef42d5e0028d8776f1ae9b6d4&dn=Sims4_DLC_EP16_Lovestruck.zip&xl=1725693097&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP17 — Life and Death",        "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:59cfd05a7edbdfb5439763220ce3a873a44621b4&dn=Sims4_DLC_EP17_Life_and_Death.zip&xl=2123601013&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP18 — Businesses and Hobbies","tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:5ecdbfef46508ae3930bfa72ccf9b8a6ad6ff374&dn=Sims4_DLC_EP18_Businesses_and_Hobbies.zip&xl=1517186961&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP19 — Enchanted by Nature",   "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:86f84ee365ad5b4796816d7dc470c4dfe2e148cf&dn=Sims4_DLC_EP19_Enchanted_by_Nature_Expansion_Pack.zip&xl=2089214644&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "EP20 — Adventure Awaits",      "tag": "Expansion Pack", "magnet": "magnet:?xt=urn:btih:53efbd10c6d9185c75da1fbcfc4bf174baf84688&dn=Sims4_DLC_EP20_Adventure_Awaits_Expansion_Pack.zip&xl=1567144516&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=udp%3A%2F%2Fopen.stealth.si%3A80%2Fannounce&tr=udp%3A%2F%2Ftracker.torrent.eu.org%3A451%2Fannounce&tr=udp%3A%2F%2Fexplodie.org%3A6969%2Fannounce"},
    {"nome": "KITS AINDA NÃO DISPONÍVEIS",   "tag": "KIT",            "magnet": "magnet:?xt=urn:btih:"},
]

CORES_TAG = {
    "Expansion Pack": "#98008E",
    "KIT":            "#FF0000",
}
COR_TAG_PADRAO = "#5A5A5A"

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO PERSISTENTE
# ---------------------------------------------------------------------------
PASTA_CONFIG   = BASE_DIR / "configs"
ARQUIVO_CONFIG = PASTA_CONFIG / "config.json"
PASTA_LOGS     = BASE_DIR / "logs"
PASTA_PADRAO   = os.path.expanduser("~/Downloads/DLCs")


def carregar_config():
    PASTA_CONFIG.mkdir(parents=True, exist_ok=True)
    PASTA_LOGS.mkdir(parents=True, exist_ok=True)
    if ARQUIVO_CONFIG.exists():
        try:
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                dados = json.load(f)
                dados.setdefault("pasta_downloads", PASTA_PADRAO)
                return dados
        except (json.JSONDecodeError, OSError):
            pass
    return {"pasta_downloads": PASTA_PADRAO}


def salvar_config(config):
    PASTA_CONFIG.mkdir(parents=True, exist_ok=True)
    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def escrever_log(mensagem):
    PASTA_LOGS.mkdir(parents=True, exist_ok=True)
    with open(PASTA_LOGS / "dlc_manager.log", "a", encoding="utf-8") as f:
        from datetime import datetime
        f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {mensagem}\n")



# ---------------------------------------------------------------------------
# ESTADOS DO LIBTORRENT
# ---------------------------------------------------------------------------
ESTADOS_PT = {
    lt.torrent_status.states.queued_for_checking:  "Na fila",
    lt.torrent_status.states.checking_files:       "Verificando arquivos",
    lt.torrent_status.states.downloading_metadata: "Buscando metadados",
    lt.torrent_status.states.downloading:          "Baixando",
    lt.torrent_status.states.finished:             "Concluído",
    lt.torrent_status.states.seeding:              "Concluído (semeando)",
    lt.torrent_status.states.allocating:           "Alocando espaço",
    lt.torrent_status.states.checking_resume_data: "Verificando dados",
}


# ---------------------------------------------------------------------------
# GERENCIADOR DE TORRENTS
# ---------------------------------------------------------------------------
class GerenciadorTorrents:
    def __init__(self, pasta_downloads, log=print):
        self.session         = lt.session({"listen_interfaces": "0.0.0.0:6881"})
        self.pasta_downloads = pasta_downloads
        self.log             = log
        self.handles         = {}   # item_id -> handle
        self.callbacks       = {}   # item_id -> função(status)
        self._rodando        = True
        self._thread = threading.Thread(target=self._loop_status, daemon=True)
        self._thread.start()

    def atualizar_pasta(self, nova_pasta):
        self.pasta_downloads = nova_pasta

    def adicionar_magnet(self, item_id, magnet_uri, on_update):
        os.makedirs(self.pasta_downloads, exist_ok=True)
        params = lt.parse_magnet_uri(magnet_uri)
        params.save_path    = self.pasta_downloads
        params.storage_mode = lt.storage_mode_t.storage_mode_sparse
        handle = self.session.add_torrent(params)
        self.handles[item_id]   = handle
        self.callbacks[item_id] = on_update

    def _loop_status(self):
        while self._rodando:
            for item_id, handle in list(self.handles.items()):
                if not handle.is_valid():
                    continue
                status   = handle.status()
                callback = self.callbacks.get(item_id)
                if callback:
                    callback(status)
            time.sleep(1)

    def parar(self):
        self._rodando = False


# ---------------------------------------------------------------------------
# JANELA DO UNLOCKER
# ---------------------------------------------------------------------------
class UnlockerWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("EA Unlocker Manager")
        self.geometry("500x400")
        self.attributes("-topmost", True)

        self.unlocker = EAUnlocker()

        self.status_label = ctk.CTkLabel(self, text="Inicializando...",
                                         font=ctk.CTkFont(size=14))
        self.status_label.pack(pady=20)

        self.prefix_var  = ctk.StringVar(value="Carregando...")
        self.prefix_menu = ctk.CTkOptionMenu(self, variable=self.prefix_var, values=[])
        self.prefix_menu.pack(pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Atualizar",
                      command=self._install_unlocker).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Desinstalar",
                      command=self._uninstall_unlocker,
                      fg_color="#8B0000").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Abrir Configs",
                      command=self._open_configs).pack(side="left", padx=5)

        self.after(100, self._scan_prefixes)

    def _scan_prefixes(self):
        try:
            self.unlocker.discover_prefixes()
            names = self.unlocker.all_prefix_names
            if not names:
                self.prefix_var.set("Nenhum prefixo encontrado")
                self.status_label.configure(text="Erro: Nenhum prefixo encontrado.")
                return
            self.prefix_menu.configure(values=names)
            self.prefix_var.set(names[0])
            self.status_label.configure(text=f"{len(names)} prefixo(s) encontrado(s).")
        except Exception as e:
            self.status_label.configure(text=f"Erro ao escanear: {e}")

    def _select_prefix(self):
        names = self.prefix_menu.cget("values")
        if names:
            try:
                idx = list(names).index(self.prefix_var.get())
                self.unlocker.select_prefix(idx)
            except (ValueError, Exception) as e:
                self.status_label.configure(text=f"Erro na seleção: {e}")

    def _install_unlocker(self):
        self._select_prefix()
        threading.Thread(target=self._do_install, daemon=True).start()

    def _do_install(self):
        try:
            self.unlocker.install_unlocker()
            self.after(0, lambda: self.status_label.configure(
                text="Instalação concluída com sucesso!"))
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text=f"Falha: {e}"))

    def _uninstall_unlocker(self):
        self._select_prefix()
        threading.Thread(target=self._do_uninstall, daemon=True).start()

    def _do_uninstall(self):
        try:
            self.unlocker.uninstall_unlocker()
            self.after(0, lambda: self.status_label.configure(
                text="Desinstalação concluída."))
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text=f"Falha: {e}"))

    def _open_configs(self):
        try:
            self._select_prefix()
            self.unlocker.open_configs_folder()
        except Exception as e:
            self.status_label.configure(text=f"Erro: {e}")


# ---------------------------------------------------------------------------
# CARD DE ARQUIVO
# ---------------------------------------------------------------------------
class CartaoArquivo(ctk.CTkFrame):
    def __init__(self, master, item_id, item, on_baixar, **kwargs):
        super().__init__(master, corner_radius=12,
                         fg_color=("#EAEAEA", "#242424"), **kwargs)
        self.item_id  = item_id
        self.item     = item
        self.on_baixar = on_baixar

        self.grid_columnconfigure(1, weight=1)

        cor   = CORES_TAG.get(item["tag"], COR_TAG_PADRAO)
        badge = ctk.CTkLabel(self, text=item["tag"],
                             fg_color=cor, text_color="white",
                             corner_radius=8, width=60, height=26,
                             font=ctk.CTkFont(size=12, weight="bold"))
        badge.grid(row=0, column=0, padx=(14, 10), pady=14, sticky="n")

        ctk.CTkLabel(self, text=item["nome"], anchor="w",
                     font=ctk.CTkFont(size=15, weight="bold")
                     ).grid(row=0, column=1, sticky="w", pady=(14, 0))

        self.status_label = ctk.CTkLabel(self, text="Aguardando", anchor="w",
                                         text_color="gray60",
                                         font=ctk.CTkFont(size=11))
        self.status_label.grid(row=1, column=1, sticky="w", pady=(2, 6))

        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=2, column=1, sticky="ew",
                               pady=(0, 14), padx=(0, 10))

        self.botao = ctk.CTkButton(self, text="⬇ Baixar",
                                   width=100, command=self._clicar)
        self.botao.grid(row=0, column=2, rowspan=3, padx=14, pady=14)

    def _clicar(self):
        self.botao.configure(state="disabled", text="Baixando...")
        self.status_label.configure(text="Iniciando...")
        self.on_baixar(self.item_id, self.item)

    def atualizar_status(self, status):
        progresso    = status.progress
        estado_texto = ESTADOS_PT.get(status.state, str(status.state))
        vel_kb       = status.download_rate / 1024
        peers        = status.num_peers

        self.progress_bar.set(progresso)

        concluido = status.state in (
            lt.torrent_status.states.finished,
            lt.torrent_status.states.seeding,
        )
        if concluido:
            self.status_label.configure(text="Concluído ✔", text_color="#2FA572")
            self.botao.configure(text="Concluído", state="disabled")
        else:
            self.status_label.configure(
                text=f"{estado_texto} • {progresso*100:.1f}% • {vel_kb:.0f} KB/s • {peers} peers",
                text_color="gray60")


# ---------------------------------------------------------------------------
# APP PRINCIPAL
# ---------------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DLC Unlocker by LinaPy")
        self.geometry("680x620")
        self.minsize(520, 420)

        self.config_dados = carregar_config()
        self.gerenciador  = GerenciadorTorrents(
            pasta_downloads=self.config_dados["pasta_downloads"],
            log=self._log,
        )

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._fechar)

    # ------------------------------------------------------------------
    def _build_ui(self):
        # Cabeçalho
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkLabel(header, text="DLC Unlocker",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        ctk.CTkButton(header, text="📂  Organizar DLCs", width=140,
                      command=self._abrir_janela_organizar
                      ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(header, text="🛠 EA Unlocker", width=120,
                      command=self._abrir_unlocker).pack(side="right")

        self.contador_label = ctk.CTkLabel(header,
                                           text=f"{len(ARQUIVOS)} itens",
                                           text_color="gray60",
                                           font=ctk.CTkFont(size=13))
        self.contador_label.pack(side="right", padx=(0, 10))

        # Pasta de downloads
        pasta_frame = ctk.CTkFrame(self, fg_color="transparent")
        pasta_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(pasta_frame, text="Pasta de downloads:",
                     font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 8))

        self.pasta_entry = ctk.CTkEntry(pasta_frame)
        self.pasta_entry.insert(0, self.config_dados["pasta_downloads"])
        self.pasta_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(pasta_frame, text="Alterar", width=80,
                      command=self._alterar_pasta).pack(side="left")

        # Busca
        busca_frame = ctk.CTkFrame(self, fg_color="transparent")
        busca_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.busca_entry = ctk.CTkEntry(
            busca_frame, placeholder_text="🔍 Filtrar por nome ou tag...")
        self.busca_entry.pack(fill="x")
        self.busca_entry.bind("<KeyRelease>", lambda e: self._filtrar())

        # Lista
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.cartoes = {}
        self._montar_lista()

        # Log
        self.log_label = ctk.CTkLabel(self, text="", text_color="gray60",
                                      anchor="w", font=ctk.CTkFont(size=11))
        self.log_label.pack(fill="x", padx=20, pady=(0, 16))

    # ------------------------------------------------------------------
    def _abrir_unlocker(self):
        for w in self.winfo_children():
            if isinstance(w, UnlockerWindow):
                w.lift()
                return
        UnlockerWindow(self).focus_force()

    def _log(self, mensagem):
        self.after(0, lambda: self.log_label.configure(text=mensagem))
        try:
            escrever_log(mensagem)
        except Exception:
            pass
    def _montar_lista(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        self.cartoes = {}

        for indice, item in enumerate(ARQUIVOS):
            item_id = item.get("magnet", "") + str(indice)
            cartao  = CartaoArquivo(self.scroll_frame, item_id, item,
                                    self._baixar_item)
            cartao.pack(fill="x", pady=6)
            self.cartoes[item_id] = cartao
            item["_item_id"] = item_id

        self.contador_label.configure(text=f"{len(ARQUIVOS)} itens")

    def _filtrar(self):
        termo    = self.busca_entry.get().strip().lower()
        visiveis = 0
        for item in ARQUIVOS:
            cartao = self.cartoes.get(item.get("_item_id"))
            if not cartao:
                continue
            if not termo or termo in item["nome"].lower() or termo in item["tag"].lower():
                cartao.pack(fill="x", pady=6)
                visiveis += 1
            else:
                cartao.pack_forget()
        self.contador_label.configure(text=f"{visiveis} itens")

    def _baixar_item(self, item_id, item):
        magnet = item.get("magnet", "")
        if not magnet or magnet.endswith("btih:"):
            self._log(f"⚠ Magnet inválido para: {item['nome']}")
            return

        def callback_status(status):
            cartao = self.cartoes.get(item_id)
            if cartao:
                self.after(0, lambda: cartao.atualizar_status(status))

        self.gerenciador.adicionar_magnet(item_id, magnet, callback_status)
        self._log(f"Download iniciado: {item['nome']}")

    def _alterar_pasta(self):
        nova = filedialog.askdirectory(
            title="Escolher pasta de downloads",
            initialdir=self.config_dados["pasta_downloads"])
        if nova:
            self.pasta_entry.delete(0, "end")
            self.pasta_entry.insert(0, nova)
            self.config_dados["pasta_downloads"] = nova
            self.gerenciador.atualizar_pasta(nova)
            salvar_config(self.config_dados)
            self._log(f"Pasta alterada para: {nova}")

    def _fechar(self):
        self.gerenciador.parar()
        self.destroy()

    # ------------------------------------------------------------------
    # ORGANIZAR DLCs
    # ------------------------------------------------------------------
    def _encontrar_pasta_sims(self):
        home = Path.home()
        steam_paths = [
            home / ".local/share/Steam",
            home / ".steam/steam",
            home / "snap/steam/common/.local/share/Steam",
            home / ".var/app/com.valvesoftware.Steam/.local/share/Steam",
            home / ".var/app/com.valvesoftware.Steam/.steam/steam",
        ]
        for steam in steam_paths:
            sims = steam / "steamapps/common/The Sims 4"
            if sims.exists():
                return sims
            vdf = steam / "steamapps/libraryfolders.vdf"
            if vdf.exists():
                try:
                    content = vdf.read_text(encoding="utf-8", errors="ignore")
                    for lib_path in re.findall(r'"path"\s+"([^"]+)"', content):
                        sims = Path(lib_path) / "steamapps/common/The Sims 4"
                        if sims.exists():
                            return sims
                except Exception:
                    pass
        return None

    def _abrir_janela_organizar(self):
        pasta_downloads = Path(self.config_dados["pasta_downloads"])
        zips = list(pasta_downloads.glob("*.zip"))
        if not zips:
            messagebox.showwarning("Nada encontrado",
                                   f"Nenhum .zip encontrado em:\n{pasta_downloads}")
            return

        pasta_sims = self._encontrar_pasta_sims()
        if not pasta_sims:
            messagebox.showerror(
                "Sims 4 não encontrado",
                "Não foi possível localizar a pasta do The Sims 4.\n"
                "Certifique-se de que o jogo está instalado via Steam.")
            return

        # Janela de progresso
        win = ctk.CTkToplevel(self)
        win.title("Organizando DLCs")
        win.geometry("520x300")
        win.resizable(False, False)
        win.grab_set()
        self._janela_prog = win

        ctk.CTkLabel(win, text="Extraindo e organizando DLCs",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(24, 4))

        self._lbl_arquivo_atual = ctk.CTkLabel(win, text="Iniciando…",
                                               text_color="gray60",
                                               font=ctk.CTkFont(size=11))
        self._lbl_arquivo_atual.pack(pady=(0, 8))

        self._prog_geral = ctk.CTkProgressBar(win, width=460)
        self._prog_geral.set(0)
        self._prog_geral.pack(pady=(0, 4))

        self._lbl_prog_geral = ctk.CTkLabel(win, text=f"0 / {len(zips)} arquivos",
                                            text_color="gray60",
                                            font=ctk.CTkFont(size=10))
        self._lbl_prog_geral.pack()

        ctk.CTkLabel(win, text="Progresso do zip atual:",
                     font=ctk.CTkFont(size=11)).pack(pady=(16, 4))

        self._prog_zip = ctk.CTkProgressBar(win, width=460,
                                            progress_color="#2FA572")
        self._prog_zip.set(0)
        self._prog_zip.pack(pady=(0, 4))

        self._lbl_prog_zip = ctk.CTkLabel(win, text="",
                                          text_color="gray60",
                                          font=ctk.CTkFont(size=10))
        self._lbl_prog_zip.pack()

        threading.Thread(target=self._executar_organizacao,
                         args=(zips, pasta_sims), daemon=True).start()

    def _executar_organizacao(self, zips, pasta_sims):
        total   = len(zips)
        erros   = []
        pulados = []
        padrao  = re.compile(r'^(EP|GP|SP|FP|KT)\d+', re.IGNORECASE)

        dst_raiz = pasta_sims
        dst_dlc  = pasta_sims / "__Installer" / "DLC"

        for i, zip_path in enumerate(zips):
            nome_zip = zip_path.stem

            self.after(0, lambda n=nome_zip, i=i, t=total: (
                self._lbl_arquivo_atual.configure(text=f"Extraindo: {n}"),
                self._prog_geral.set(i / t),
                self._lbl_prog_geral.configure(text=f"{i} / {t} arquivos"),
                self._prog_zip.set(0),
                self._lbl_prog_zip.configure(text=""),
            ))

            # Extração
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    membros       = zf.infolist()
                    total_membros = len(membros)
                    for j, membro in enumerate(membros):
                        zf.extract(membro, zip_path.parent)
                        pct   = (j + 1) / total_membros
                        texto = f"{j+1} / {total_membros} arquivos"
                        self.after(0, lambda p=pct, tx=texto: (
                            self._prog_zip.set(p),
                            self._lbl_prog_zip.configure(text=tx),
                        ))
            except zipfile.BadZipFile:
                erros.append(f"{nome_zip}: zip corrompido")
                continue
            except Exception as e:
                erros.append(f"{nome_zip}: {e}")
                continue

            # Localiza pastas
            pasta_extracao = zip_path.parent / nome_zip
            if not pasta_extracao.exists():
                erros.append(f"{nome_zip}: pasta extraída não encontrada")
                continue

            pasta_raiz_dlc = next(
                (p for p in pasta_extracao.iterdir()
                 if p.is_dir() and padrao.match(p.name)), None)

            installer_dlc = pasta_extracao / "__Installer" / "DLC"
            pasta_dlc_dir = None
            if installer_dlc.exists():
                pasta_dlc_dir = next(
                    (p for p in installer_dlc.iterdir()
                     if p.is_dir() and padrao.match(p.name)), None)

            # Move as pastas
            for src, dst_base, label in [
                (pasta_raiz_dlc, dst_raiz, "raiz do jogo"),
                (pasta_dlc_dir,  dst_dlc,  "__Installer/DLC"),
            ]:
                if src is None:
                    continue

                dst = dst_base / src.name

                if dst.exists():
                    ev  = threading.Event()
                    res = [False]

                    def perguntar(s=src, lb=label, ev=ev, res=res):
                        res[0] = messagebox.askyesno(
                            "Pasta já existe",
                            f"'{s.name}' já existe em {lb}.\n\nSubstituir?")
                        ev.set()

                    self.after(0, perguntar)
                    ev.wait()

                    if not res[0]:
                        pulados.append(f"{src.name} em {label}")
                        continue
                    shutil.rmtree(dst)

                dst_base.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))

            # Atualiza progresso geral
            self.after(0, lambda i=i+1, t=total, n=nome_zip: (
                self._prog_geral.set(i / t),
                self._lbl_prog_geral.configure(text=f"{i} / {t} arquivos"),
                self._lbl_arquivo_atual.configure(text=f"Concluído: {n}"),
            ))

        # Finaliza
        def finalizar():
            self._janela_prog.destroy()
            msg = "Organização concluída!"
            if pulados:
                msg += f"\n\nPulados ({len(pulados)}):\n" + "\n".join(f"• {p}" for p in pulados)
            if erros:
                msg += f"\n\nErros ({len(erros)}):\n" + "\n".join(f"• {e}" for e in erros)
            if erros:
                messagebox.showwarning("Concluído com erros", msg)
            else:
                messagebox.showinfo("Concluído", msg)

        self.after(0, finalizar)


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    def abrir_app_principal():
        app = App()
        app.mainloop()

    splash = SplashScreen(
        caminho_imagem=str(BASE_DIR / "assets" / "__.jpeg"),
        texto=(
            "A pirataria surge quando o valor de uma obra encontra a realidade "
            "de quem não pode alcançá-la.\n\npirateie TUDO que você puder!"
        ),
        ao_continuar=abrir_app_principal,
    )
    splash.mainloop()