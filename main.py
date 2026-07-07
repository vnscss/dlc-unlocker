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
        "Rode ./install.sh para instalar as dependências do sistema."
    )

# ---------------------------------------------------------------------------
# DADOS
# ---------------------------------------------------------------------------
PASTA_TORRENTS = BASE_DIR / "torrents"

ARQUIVOS = [
    {"nome": "EP01 — Get to Work",           "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP01_Get_to_Work.zip.torrent"},
    {"nome": "EP02 — Get Together",          "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP02_Get_Together.zip.torrent"},
    {"nome": "EP03 — City Living",           "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP03_City_Living.zip.torrent"},
    {"nome": "EP04 — Cats and Dogs",         "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP04_Cats_and_Dogs.zip.torrent"},
    {"nome": "EP05 — Seasons",               "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP05_Seasons.zip.torrent"},
    {"nome": "EP06 — Get Famous",            "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP06_Get_Famous.zip.torrent"},
    {"nome": "EP07 — Island Living",         "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP07_Island_Living.zip.torrent"},
    {"nome": "EP08 — Discover University",   "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP08_Discover_University.zip.torrent"},
    {"nome": "EP09 — Eco Lifestyle",         "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP09_Eco_Lifestyle.zip.torrent"},
    {"nome": "EP10 — Snowy Escape",          "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP10_Snowy_Escape.zip.torrent"},
    {"nome": "EP11 — Cottage Living",        "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP11_Cottage_Living.zip.torrent"},
    {"nome": "EP12 — High School Years",     "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP12_High_School_Years.zip.torrent"},
    {"nome": "EP13 — Growing Together",      "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP13_Growing_Together.zip.torrent"},
    {"nome": "EP14 — Horse Ranch",           "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP14_Horse_Ranch.zip.torrent"},
    {"nome": "EP15 — For Rent",              "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP15_For_Rent.zip.torrent"},
    {"nome": "EP16 — Lovestruck",            "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP16_Lovestruck.zip.torrent"},
    {"nome": "EP17 — Life and Death",        "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP17_Life_and_Death.zip.torrent"},
    {"nome": "EP18 — Businesses and Hobbies","tag": "Expansion Pack", "torrent": "Sims4_DLC_EP18_Businesses_and_Hobbies.zip.torrent"},
    {"nome": "EP19 — Enchanted by Nature",   "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP19_Enchanted_by_Nature_Expansion_Pack.zip.torrent"},
    {"nome": "EP20 — Adventure Awaits",      "tag": "Expansion Pack", "torrent": "Sims4_DLC_EP20_Adventure_Awaits_Expansion_Pack.zip.torrent"},
    {"nome": "KITS AINDA NÃO DISPONÍVEIS",   "tag": "KIT",            "torrent": ""},
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
        self.handles         = {}
        self.callbacks       = {}
        self._rodando        = True
        self._thread = threading.Thread(target=self._loop_status, daemon=True)
        self._thread.start()

    def atualizar_pasta(self, nova_pasta):
        self.pasta_downloads = nova_pasta

    def adicionar_torrent(self, item_id, caminho_torrent, on_update):
        os.makedirs(self.pasta_downloads, exist_ok=True)
        info   = lt.torrent_info(str(caminho_torrent))
        params = lt.add_torrent_params()
        params.ti           = info
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

    def cancelar(self, item_id):
        """Pausa o torrent e remove da sessão, mantendo os arquivos parciais."""
        handle = self.handles.pop(item_id, None)
        self.callbacks.pop(item_id, None)
        if handle and handle.is_valid():
            self.session.remove_torrent(handle, 0)  # 0 = mantém arquivos

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
        self.item_id   = item_id
        self.item      = item
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
        self.botao.grid(row=0, column=2, padx=(14, 4), pady=(14, 4))

        self.botao_cancelar = ctk.CTkButton(self, text="✕ Cancelar",
                                            width=100,
                                            fg_color="#5c1a1a",
                                            hover_color="#8B0000",
                                            command=self._cancelar)
        self.botao_cancelar.grid(row=1, column=2, padx=(14, 4), pady=(0, 14))
        self.botao_cancelar.grid_remove()  # escondido até o download começar

        self._on_cancelar = None  # callback definido pelo App

    def _clicar(self):
        self.botao.configure(state="disabled", text="Baixando...")
        self.status_label.configure(text="Iniciando...")
        self.botao_cancelar.grid()  # mostra o botão cancelar
        self.on_baixar(self.item_id, self.item)

    def _cancelar(self):
        self.botao_cancelar.configure(state="disabled", text="Cancelando…")
        if self._on_cancelar:
            self._on_cancelar(self.item_id)

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
            self.botao_cancelar.grid_remove()
        else:
            self.status_label.configure(
                text=f"{estado_texto} • {progresso*100:.1f}% • {vel_kb:.0f} KB/s • {peers} peers",
                text_color="gray60")


# ---------------------------------------------------------------------------
# JANELA DE PROGRESSO BASE (reutilizada por Extrair e Mover)
# ---------------------------------------------------------------------------
class JanelaProgresso(ctk.CTkToplevel):
    def __init__(self, master, titulo, subtitulo):
        super().__init__(master)
        self.title(titulo)
        self.geometry("540x280")
        self.resizable(False, False)
        self.grab_set()

        ctk.CTkLabel(self, text=titulo,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(24, 2))

        self.lbl_sub = ctk.CTkLabel(self, text=subtitulo,
                                    text_color="gray60",
                                    font=ctk.CTkFont(size=11))
        self.lbl_sub.pack(pady=(0, 16))

        # Barra geral
        row_g = ctk.CTkFrame(self, fg_color="transparent")
        row_g.pack(fill="x", padx=30)
        self.lbl_geral = ctk.CTkLabel(row_g, text="Aguardando…",
                                      text_color="gray60",
                                      font=ctk.CTkFont(size=10), anchor="w")
        self.lbl_geral.pack(side="left")
        self.lbl_conta = ctk.CTkLabel(row_g, text="0 / 0",
                                      text_color="gray60",
                                      font=ctk.CTkFont(size=10), anchor="e")
        self.lbl_conta.pack(side="right")
        self.prog_geral = ctk.CTkProgressBar(self, width=480)
        self.prog_geral.set(0)
        self.prog_geral.pack(padx=30, pady=(4, 14))

        # Barra atual
        self.lbl_atual = ctk.CTkLabel(self, text="",
                                      text_color="gray60",
                                      font=ctk.CTkFont(size=10), anchor="w")
        self.lbl_atual.pack(fill="x", padx=30)
        self.prog_atual = ctk.CTkProgressBar(self, width=480,
                                             progress_color="#2FA572")
        self.prog_atual.set(0)
        self.prog_atual.pack(padx=30, pady=(4, 0))

        self.lbl_detalhe = ctk.CTkLabel(self, text="",
                                        text_color="gray60",
                                        font=ctk.CTkFont(size=9))
        self.lbl_detalhe.pack(pady=(4, 0))

    def atualizar(self, geral_txt, conta_txt, geral_pct,
                  atual_txt, atual_pct, detalhe_txt=""):
        self.lbl_geral.configure(text=geral_txt)
        self.lbl_conta.configure(text=conta_txt)
        self.prog_geral.set(geral_pct)
        self.lbl_atual.configure(text=atual_txt)
        self.prog_atual.set(atual_pct)
        self.lbl_detalhe.configure(text=detalhe_txt)


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

        # Botões do lado direito (ordem reversa por causa do pack side=right)
        ctk.CTkButton(header, text="📂 Mover",
                      width=90, fg_color="#1a5c2a", hover_color="#14451f",
                      command=self._abrir_mover).pack(side="right", padx=(4, 0))

        ctk.CTkButton(header, text="📦 Extrair",
                      width=90, fg_color="#1a3a5c", hover_color="#14293f",
                      command=self._abrir_extrair).pack(side="right", padx=(4, 0))

        ctk.CTkButton(header, text="🛠 EA Unlocker", width=120,
                      command=self._abrir_unlocker).pack(side="right", padx=(4, 0))

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
            item_id = item.get("torrent", "") + str(indice)
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
        nome_torrent = item.get("torrent", "")
        if not nome_torrent:
            self._log(f"⚠ Sem arquivo .torrent para: {item['nome']}")
            cartao = self.cartoes.get(item_id)
            if cartao:
                cartao.botao.configure(state="normal", text="⬇ Baixar")
                cartao.status_label.configure(text="Torrent não disponível")
            return

        caminho = PASTA_TORRENTS / nome_torrent
        if not caminho.exists():
            self._log(f"⚠ Arquivo não encontrado: {caminho}")
            cartao = self.cartoes.get(item_id)
            if cartao:
                cartao.botao.configure(state="normal", text="⬇ Baixar")
                cartao.status_label.configure(text="Arquivo .torrent ausente")
            return

        def callback_status(status):
            cartao = self.cartoes.get(item_id)
            if cartao:
                self.after(0, lambda: cartao.atualizar_status(status))

        cartao = self.cartoes.get(item_id)
        self.gerenciador.adicionar_torrent(item_id, caminho, callback_status)
        self._log(f"Download iniciado: {item['nome']}")

        # Liga o botão cancelar ao handle do torrent
        if cartao:
            def cancelar(iid=item_id, c=cartao):
                self.gerenciador.cancelar(iid)
                c.status_label.configure(text="Cancelado", text_color="gray60")
                c.progress_bar.set(0)
                c.botao.configure(state="normal", text="⬇ Baixar")
                c.botao_cancelar.grid_remove()
                c.botao_cancelar.configure(state="normal", text="✕ Cancelar")
                self._log(f"Download cancelado: {item['nome']} (progresso mantido)")
            cartao._on_cancelar = cancelar

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
    # HELPERS COMPARTILHADOS
    # ------------------------------------------------------------------
    def _pasta_downloads(self):
        return Path(self.config_dados["pasta_downloads"])

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

    # ------------------------------------------------------------------
    # EXTRAIR
    # ------------------------------------------------------------------
    def _abrir_extrair(self):
        pasta = self._pasta_downloads()
        zips  = list(pasta.glob("*.zip"))
        if not zips:
            messagebox.showwarning("Nada encontrado",
                                   f"Nenhum .zip encontrado em:\n{pasta}")
            return

        win = JanelaProgresso(self, "📦 Extraindo DLCs",
                              f"{len(zips)} arquivo(s) .zip encontrado(s)")
        threading.Thread(target=self._executar_extracao,
                         args=(zips, win), daemon=True).start()

    def _executar_extracao(self, zips, win):
        total  = len(zips)
        erros  = []

        for i, zip_path in enumerate(zips):
            nome_zip       = zip_path.stem          # Sims4_DLC_EP02_Get_Together
            pasta_destino  = zip_path.parent / nome_zip  # extrai para subpasta com mesmo nome

            # Atualiza barra geral
            self.after(0, lambda n=nome_zip, i=i, t=total: win.atualizar(
                f"Extraindo: {n}", f"{i} / {t}", i / t,
                "Preparando…", 0))

            try:
                pasta_destino.mkdir(parents=True, exist_ok=True)

                with zipfile.ZipFile(zip_path, "r") as zf:
                    membros       = zf.infolist()
                    total_membros = len(membros)

                    for j, membro in enumerate(membros):
                        # Extrai sempre dentro de pasta_destino
                        zf.extract(membro, pasta_destino)
                        pct     = (j + 1) / total_membros
                        detalhe = f"{j+1} / {total_membros} arquivos"
                        self.after(0, lambda p=pct, d=detalhe, n=nome_zip, i=i, t=total:
                                   win.atualizar(
                                       f"Extraindo: {n}", f"{i+1} / {t}", (i + p) / t,
                                       f"Arquivo {j+1} de {total_membros}", p, d))

                self._log(f"✔ Extraído: {nome_zip}")

            except zipfile.BadZipFile:
                erros.append(f"{nome_zip}: zip corrompido")
                self._log(f"✘ Corrompido: {nome_zip}")
            except Exception as e:
                erros.append(f"{nome_zip}: {e}")
                self._log(f"✘ Erro: {nome_zip}: {e}")

        def finalizar():
            win.destroy()
            msg = f"Extração concluída!\n{total - len(erros)} de {total} arquivos extraídos."
            if erros:
                msg += "\n\nErros:\n" + "\n".join(f"• {e}" for e in erros)
                messagebox.showwarning("Extração com erros", msg)
            else:
                messagebox.showinfo("Extração concluída", msg)

        self.after(0, finalizar)

    # ------------------------------------------------------------------
    # MOVER
    # ------------------------------------------------------------------
    def _abrir_mover(self):
        pasta = self._pasta_downloads()

        # Busca pastas extraídas (subpastas que contêm EP/GP/SP no nome)
        pastas_extraidas = [
            p for p in pasta.iterdir()
            if p.is_dir() and re.match(r'Sims4_DLC_', p.name, re.IGNORECASE)
        ]

        if not pastas_extraidas:
            messagebox.showwarning(
                "Nada encontrado",
                f"Nenhuma pasta extraída encontrada em:\n{pasta}\n\n"
                "Execute primeiro o botão 📦 Extrair.")
            return

        pasta_sims = self._encontrar_pasta_sims()
        if not pasta_sims:
            messagebox.showerror(
                "Sims 4 não encontrado",
                "Não foi possível localizar a pasta do The Sims 4.\n"
                "Certifique-se de que o jogo está instalado via Steam.")
            return

        win = JanelaProgresso(self, "📂 Movendo DLCs",
                              f"{len(pastas_extraidas)} pasta(s) encontrada(s)")
        threading.Thread(target=self._executar_mover,
                         args=(pastas_extraidas, pasta_sims, win),
                         daemon=True).start()

    def _executar_mover(self, pastas_extraidas, pasta_sims, win):
        total   = len(pastas_extraidas)
        erros   = []
        pulados = []
        padrao  = re.compile(r'^(EP|GP|SP|FP|KT)\d+', re.IGNORECASE)

        dst_raiz = pasta_sims
        dst_dlc  = pasta_sims / "__Installer" / "DLC"

        for i, pasta_extracao in enumerate(pastas_extraidas):
            nome = pasta_extracao.name

            self.after(0, lambda n=nome, i=i, t=total: win.atualizar(
                f"Processando: {n}", f"{i} / {t}", i / t,
                "Localizando pastas…", 0))

            # Localiza pasta raiz (EP** direto na pasta extraída)
            pasta_raiz_dlc = next(
                (p for p in pasta_extracao.iterdir()
                 if p.is_dir() and padrao.match(p.name)), None)

            # Localiza pasta em __Installer/DLC
            installer_dlc = pasta_extracao / "__Installer" / "DLC"
            pasta_dlc_dir = None
            if installer_dlc.exists():
                pasta_dlc_dir = next(
                    (p for p in installer_dlc.iterdir()
                     if p.is_dir() and padrao.match(p.name)), None)

            movidos = 0
            alvos   = [
                (pasta_raiz_dlc, dst_raiz, "raiz do jogo"),
                (pasta_dlc_dir,  dst_dlc,  "__Installer/DLC"),
            ]

            for src, dst_base, label in alvos:
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
                movidos += 1
                self._log(f"✔ Movido: {src.name} → {label}")

            pct_atual = 1.0 if movidos > 0 else 0.0
            self.after(0, lambda n=nome, i=i+1, t=total, p=pct_atual: win.atualizar(
                f"Concluído: {n}", f"{i} / {t}", i / t,
                "Concluído", p))

        def finalizar():
            win.destroy()
            msg = "Movimento concluído!"
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