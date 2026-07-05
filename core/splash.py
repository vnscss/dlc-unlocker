import os
import customtkinter as ctk
from PIL import Image


PASTA_DO_SCRIPT = os.path.dirname(os.path.abspath(__file__))


class SplashScreen(ctk.CTk):
    def __init__(self, caminho_imagem, texto="teste", titulo="Bem-vindo",
                 ao_continuar=None, tamanho_imagem=(480, 480)):
        super().__init__()
        self.ao_continuar = ao_continuar

        self.title(titulo)
        self.resizable(False, False)

        # ---------------- Container central ----------------
        container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=30)

        # ---------------- IMAGEM ----------------
        if not os.path.isabs(caminho_imagem):
            caminho_imagem = os.path.join(PASTA_DO_SCRIPT, caminho_imagem)

        try:
            img_pil = Image.open(caminho_imagem)
            ctk_img = ctk.CTkImage(
                light_image=img_pil,
                dark_image=img_pil,
                size=tamanho_imagem,
            )
            label_imagem = ctk.CTkLabel(container, image=ctk_img, text="")
            label_imagem.pack(pady=(0, 20))
        except (FileNotFoundError, OSError) as erro:
            print(f"[splash] Não foi possível carregar a imagem '{caminho_imagem}': {erro}")
            placeholder = ctk.CTkLabel(
                container,
                text="[ imagem não encontrada ]",
                width=tamanho_imagem[0],
                height=tamanho_imagem[1],
                fg_color="#333333",
                text_color="gray70",
                corner_radius=12,
            )
            placeholder.pack(pady=(0, 20))

        # ---------------- TEXTO ----------------
        label_texto = ctk.CTkLabel(
            container,
            text=texto,
            font=ctk.CTkFont(size=16),
            wraplength=360,
            justify="center",
        )
        label_texto.pack(pady=(0, 20))

        # ---------------- BOTÃO CONTINUAR ----------------
        botao_continuar = ctk.CTkButton(
            container,
            text="Continuar",
            width=140,
            command=self._continuar,
        )
        botao_continuar.pack()

        # Centraliza a janela na tela
        self.update_idletasks()
        largura = self.winfo_reqwidth()
        altura = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        # X da janela também dispara o "continuar" (fecha o splash e abre o app)
        self.protocol("WM_DELETE_WINDOW", self._continuar)

    def _continuar(self):
        self.destroy()
        if self.ao_continuar:
            self.ao_continuar()
