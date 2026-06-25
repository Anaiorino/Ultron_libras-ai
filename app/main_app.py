import customtkinter as ctk
import cv2
import mediapipe as mp
import numpy as np
import time
import requests
import threading
import speech_recognition as sr

from PIL import Image, ImageTk
from collections import deque
from tkinter import messagebox
from tensorflow.keras.models import load_model
from voice import speak
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG         = "#f0ede6"
CARD       = "#ffffff"
SIDEBAR    = "#e8e4dc"
TEAL       = "#6b9fa8"
TEAL_HOVER = "#7fb3bc"
TEXT_DARK  = "#1a1a1a"
TEXT_MID   = "#555555"
TEXT_LIGHT = "#888888"
BORDER     = "#d5d0c8"
ACCENT_RED = "#c0392b"

SEQUENCE_LENGTH = 30


def get_frame_indexes(total_frames, sequence_length):
    if total_frames <= 0:
        return []
    return np.linspace(0, total_frames - 1, sequence_length, dtype=int)


class JarvisLibrasApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Jarvis Libras IA")
        self.app.geometry("1280x720")
        self.app.resizable(False, False)
        self.app.configure(fg_color=BG)

        self.current_user  = None
        self.access_token  = None

        self.model   = load_model("models/libras_model.h5")
        self.actions = np.load("models/actions.npy", allow_pickle=True)

        self.recognizer = sr.Recognizer()

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.camera       = None
        self.frame_buffer = deque()
        self.SEQUENCE_DURATION = 3.5

        self.last_prediction  = ""
        self.last_spoken_word = ""
        self.last_added_time  = 0
        self.frame_counter    = 0

        self.recognized_word = "..."
        self.confidence      = 0.0

        self.PREDICT_EVERY        = 8
        self.CONFIDENCE_THRESHOLD = 0.75
        self.PREDICTION_DELAY     = 2

        self.avatar_cap  = None
        self.words_queue = []

        self.sign_videos = {
            "oi":       "assets/oi.mp4",
            "sim":      "assets/sim.mp4",
            "nao":      "assets/nao.mp4",
            "não":      "assets/nao.mp4",
            "e":        "assets/e.mp4",
            "voce":     "assets/voce.mp4",
            "você":     "assets/voce.mp4",
            "tudo_bem": "assets/tudo_bem.mp4",
            "tudo bem": "assets/tudo_bem.mp4",
        }

        self.show_login_screen()
        self.app.mainloop()

    def clear_window(self):
        for w in self.app.winfo_children():
            w.destroy()

    def clear_content(self):
        self.stop_camera()
        self.stop_avatar()
        for w in self.content.winfo_children():
            w.destroy()

    def primary_button(self, parent, text, command, width=310):
        return ctk.CTkButton(
            parent, text=text, width=width, height=46, corner_radius=12,
            fg_color=TEAL, hover_color=TEAL_HOVER,
            text_color="#ffffff", font=("Arial", 14, "bold"),
            command=command
        )

    def outline_button(self, parent, text, command, width=310):
        return ctk.CTkButton(
            parent, text=text, width=width, height=44, corner_radius=12,
            fg_color="transparent", hover_color="#ddd8ce",
            border_width=1, border_color=BORDER,
            text_color=TEXT_DARK, font=("Arial", 14),
            command=command
        )

    #LOGIN

    def show_login_screen(self):
        self.clear_window()
        self.app.configure(fg_color=BG)

        left = ctk.CTkFrame(self.app, width=420, corner_radius=0,
                            fg_color=SIDEBAR, border_width=0)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        ctk.CTkLabel(left, text="🤟", font=("Arial", 90),
                     text_color=TEAL).pack(pady=(100, 0))
        ctk.CTkLabel(left, text="Jarvis", font=("Arial", 38, "bold"),
                     text_color=TEXT_DARK).pack()
        ctk.CTkLabel(left, text="Libras IA", font=("Arial", 22),
                     text_color=TEAL).pack()
        ctk.CTkLabel(left, text="Traduzindo sinais em tempo real",
                     font=("Arial", 13), text_color=TEXT_MID,
                     wraplength=300, justify="center").pack(pady=(14, 0))

        right = ctk.CTkFrame(self.app, corner_radius=0, fg_color=BG)
        right.pack(side="right", fill="both", expand=True)

        card = ctk.CTkFrame(right, width=400, corner_radius=20,
                            fg_color=CARD, border_width=1, border_color=BORDER)
        card.place(relx=0.5, rely=0.5, anchor="center")

        tab_row = ctk.CTkFrame(card, fg_color="transparent")
        tab_row.pack(pady=(32, 0))

        self._tab_login = ctk.CTkButton(
            tab_row, text="LOGIN", width=130, height=38, corner_radius=10,
            fg_color=TEAL, hover_color=TEAL_HOVER, text_color="#fff",
            font=("Arial", 14, "bold"), command=lambda: self._switch_login_tab()
        )
        self._tab_login.grid(row=0, column=0, padx=(0, 4))

        self._tab_register = ctk.CTkButton(
            tab_row, text="REGISTRAR", width=130, height=38, corner_radius=10,
            fg_color="transparent", hover_color="#ddd8ce",
            border_width=1, border_color=BORDER,
            text_color=TEXT_MID, font=("Arial", 14),
            command=lambda: self._switch_register_tab()
        )
        self._tab_register.grid(row=0, column=1, padx=(4, 0))

        self._tab_content = ctk.CTkFrame(card, fg_color="transparent", width=360)
        self._tab_content.pack(pady=18, padx=20)

        self._build_login_form(self._tab_content)

    def _switch_login_tab(self):
        self._tab_login.configure(fg_color=TEAL, text_color="#fff", border_width=0)
        self._tab_register.configure(fg_color="transparent", text_color=TEXT_MID, border_width=1)
        for w in self._tab_content.winfo_children():
            w.destroy()
        self._build_login_form(self._tab_content)

    def _switch_register_tab(self):
        self._tab_register.configure(fg_color=TEAL, text_color="#fff", border_width=0)
        self._tab_login.configure(fg_color="transparent", text_color=TEXT_MID, border_width=1)
        for w in self._tab_content.winfo_children():
            w.destroy()
        self._build_register_form(self._tab_content)

    def _field(self, parent, placeholder, show=""):
        return ctk.CTkEntry(
            parent, width=320, height=44, corner_radius=10,
            placeholder_text=placeholder,
            fg_color="#f5f2ec", border_color=BORDER,
            text_color=TEXT_DARK, font=("Arial", 13),
            show=show
        )

    def _build_login_form(self, parent):
        ctk.CTkLabel(parent, text="E-mail", font=("Arial", 12),
                     text_color=TEXT_MID).pack(anchor="w", pady=(10, 2))
        self.email_entry = self._field(parent, "E-mail")
        self.email_entry.pack()

        ctk.CTkLabel(parent, text="Senha", font=("Arial", 12),
                     text_color=TEXT_MID).pack(anchor="w", pady=(10, 2))
        self.password_entry = self._field(parent, "Senha", show="*")
        self.password_entry.pack()

        self.primary_button(parent, "Entrar", self.login_user, width=320).pack(pady=(22, 6))

        ctk.CTkLabel(parent, text="Esqueceu a senha?",
                     font=("Arial", 12), text_color=TEAL, cursor="hand2").pack()
        ctk.CTkLabel(parent, text="Login com Google",
                     font=("Arial", 12), text_color=TEXT_MID, cursor="hand2").pack(pady=(6, 20))

    def _build_register_form(self, parent):
        ctk.CTkLabel(parent, text="Nome Completo", font=("Arial", 12),
                     text_color=TEXT_MID).pack(anchor="w", pady=(10, 2))
        self.register_name = self._field(parent, "Nome Completo")
        self.register_name.pack()

        ctk.CTkLabel(parent, text="E-mail", font=("Arial", 12),
                     text_color=TEXT_MID).pack(anchor="w", pady=(10, 2))
        self.register_email = self._field(parent, "E-mail")
        self.register_email.pack()

        ctk.CTkLabel(parent, text="Senha", font=("Arial", 12),
                     text_color=TEXT_MID).pack(anchor="w", pady=(10, 2))
        self.register_password = self._field(parent, "Senha", show="*")
        self.register_password.pack()

        ctk.CTkLabel(parent, text="Novas contas são cadastradas como USUÁRIO.",
                     font=("Arial", 11), text_color=TEXT_LIGHT,
                     wraplength=300).pack(pady=(8, 0))

        self.primary_button(parent, "Registrar", self.register_user, width=320).pack(pady=(16, 20))

    #AUTH

    def login_user(self):
        email    = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        if not email or not password:
            messagebox.showwarning("Aviso", "Preencha e-mail e senha.")
            return
        try:
            r = requests.post("http://127.0.0.1:8000/auth/login",
                              json={"email": email, "password": password})
            if r.status_code != 200:
                messagebox.showerror("Erro", "Usuário ou senha inválidos.")
                return
            data = r.json()
            self.current_user = data["user"]
            self.access_token = data["access_token"]
            self.clear_window()
            self.build_layout()
            self.show_home()
        except Exception:
            messagebox.showerror("Erro", "Backend não está rodando.")

    def register_user(self):
        name     = self.register_name.get().strip()
        email    = self.register_email.get().strip()
        password = self.register_password.get().strip()
        if not name or not email or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return
        try:
            r = requests.post("http://127.0.0.1:8000/auth/register",
                              json={"name": name, "email": email, "password": password})
            if r.status_code != 200:
                messagebox.showerror("Erro", r.json().get("detail", "Erro ao cadastrar."))
                return
            messagebox.showinfo("Sucesso", "Conta criada com sucesso.")
            self.show_login_screen()
        except Exception:
            messagebox.showerror("Erro", "Backend não está rodando.")

    #LAYOUT PRINCIPAL

    def build_layout(self):
        self.sidebar = ctk.CTkFrame(self.app, width=270, corner_radius=0,
                                    fg_color=SIDEBAR, border_width=1,
                                    border_color=BORDER)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(self.app, corner_radius=0, fg_color=BG)
        self.content.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(self.sidebar, text="🤟 Jarvis",
                     font=("Arial", 26, "bold"), text_color=TEXT_DARK
                     ).pack(pady=(36, 0), padx=22, anchor="w")
        ctk.CTkLabel(self.sidebar, text="Libras IA",
                     font=("Arial", 15), text_color=TEAL
                     ).pack(pady=(0, 20), padx=22, anchor="w")

        profile = ctk.CTkFrame(self.sidebar, height=78, corner_radius=14,
                               fg_color=CARD, border_width=1, border_color=BORDER)
        profile.pack(padx=18, pady=(0, 20), fill="x")
        profile.pack_propagate(False)

        ib = ctk.CTkFrame(profile, width=44, height=44, corner_radius=22, fg_color="#e0eff1")
        ib.pack(side="left", padx=(14, 10))
        ib.pack_propagate(False)
        ctk.CTkLabel(ib, text="👤", font=("Arial", 22),
                     text_color=TEAL).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(profile,
                     text=f"{self.current_user['name']}\n{self.current_user['role']}",
                     font=("Arial", 12, "bold"), text_color=TEXT_DARK,
                     justify="left").pack(side="left")

        self.nav_button("🏠  Início",             self.show_home,           active=True)
        self.nav_button("🤟  Reconhecer Libras",  self.show_predict)
        self.nav_button("🎙️  Voz para Libras",    self.show_voice_to_libras)
        self.nav_button("🕘  Histórico",           self.show_history)

        if self.current_user["role"] == "ADMIN":
            self.nav_button("📊  Métricas da API", self.show_metrics)
        else:
            self.nav_button("🔒  Métricas da API", None, locked=True)

        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER
                     ).pack(fill="x", padx=24, pady=14)

        self.nav_button("↪  Logout", self.logout_user, danger=True)
        self.nav_button("🚪  Sair",   self.close_app,  danger=True)

        ctk.CTkLabel(self.sidebar, text="Jarvis Libras IA\nv1.0.0",
                     font=("Arial", 11), text_color=TEXT_LIGHT
                     ).pack(side="bottom", pady=28)

    def nav_button(self, text, command, active=False, locked=False, danger=False):
        if locked:
            fg, hover, tc = SIDEBAR, SIDEBAR, TEXT_LIGHT
        elif active:
            fg, hover, tc = TEAL, TEAL_HOVER, "#ffffff"
        elif danger:
            fg, hover, tc = "transparent", "#f5ddd9", ACCENT_RED
        else:
            fg, hover, tc = "transparent", "#ddd8ce", TEXT_DARK

        ctk.CTkButton(
            self.sidebar, text=text, width=230, height=50, corner_radius=12,
            fg_color=fg, hover_color=hover, border_width=0,
            text_color=tc, font=("Arial", 13, "bold"), anchor="w",
            command=(command if command else lambda: None),
            state="disabled" if locked else "normal"
        ).pack(padx=18, pady=3)

    def logout_user(self):
        self.stop_camera(); self.stop_avatar()
        self.current_user = None; self.access_token = None
        self.show_login_screen()

    #HOME

    def show_home(self):
        self.clear_content()

        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=42, pady=32)

        top = ctk.CTkFrame(main, fg_color="transparent", height=175)
        top.pack(fill="x")
        top.pack_propagate(False)

        lt = ctk.CTkFrame(top, fg_color="transparent")
        lt.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(lt, text=f"Olá, {self.current_user['name'].split()[0]}! 👋",
                     font=("Arial", 36, "bold"), text_color=TEXT_DARK
                     ).pack(anchor="w", pady=(16, 6))
        ctk.CTkLabel(lt, text="Bem-vindo ao Jarvis Libras IA",
                     font=("Arial", 18), text_color=TEXT_MID).pack(anchor="w")
        ctk.CTkFrame(lt, width=70, height=4, corner_radius=8,
                     fg_color=TEAL).pack(anchor="w", pady=(20, 0))

        hero = ctk.CTkFrame(top, width=220, height=150, corner_radius=20, fg_color=TEAL)
        hero.pack(side="right", padx=(16, 0), pady=(6, 0))
        hero.pack_propagate(False)
        ctk.CTkLabel(hero, text="🤟", font=("Arial", 56), text_color="#ffffff").pack(pady=(20, 0))
        ctk.CTkLabel(hero, text="IA + Acessibilidade",
                     font=("Arial", 13, "bold"), text_color="#ffffff").pack(pady=(0, 6))

        cards_row = ctk.CTkFrame(main, fg_color="transparent")
        cards_row.pack(fill="x", pady=(24, 20))

        self.home_card(cards_row, "🤟", "Reconhecer Libras",
                       "Use a câmera para reconhecer\nsinais em Libras em tempo real.",
                       self.show_predict).grid(row=0, column=0, padx=(0, 16))
        self.home_card(cards_row, "🎙️", "Voz para Libras",
                       "Fale algo e veja a tradução\nem Libras com nosso avatar.",
                       self.show_voice_to_libras).grid(row=0, column=1, padx=16)

        if self.current_user["role"] == "ADMIN":
            self.home_card(cards_row, "📊", "Métricas da API",
                           "Visualize estatísticas e métricas\nde uso da API.",
                           self.show_metrics).grid(row=0, column=2, padx=(16, 0))
        else:
            self.home_card(cards_row, "🔒", "Métricas da API",
                           "Disponível somente para\nadministradores.",
                           None).grid(row=0, column=2, padx=(16, 0))

        bottom = ctk.CTkFrame(main, height=86, corner_radius=16,
                              fg_color=CARD, border_width=1, border_color=BORDER)
        bottom.pack(fill="x")
        bottom.pack_propagate(False)

        today = datetime.now().strftime("%d/%m/%Y")
        hour  = datetime.now().strftime("%H:%M")

        self.info_item(bottom, "👥", "Seu perfil",     self.current_user["role"]).pack(side="left", expand=True, fill="both")
        self.info_item(bottom, "📅", "Data de acesso", today).pack(side="left", expand=True, fill="both")
        self.info_item(bottom, "🕒", "Horário",        hour).pack(side="left", expand=True, fill="both")
        self.info_item(bottom, "🛡️", "Sessão segura", "Ativa").pack(side="left", expand=True, fill="both")

    def home_card(self, parent, icon, title, desc, command):
        card = ctk.CTkFrame(parent, width=220, height=268, corner_radius=20,
                            fg_color=CARD, border_width=1, border_color=BORDER)
        card.grid_propagate(False)
        card.pack_propagate(False)

        ib = ctk.CTkFrame(card, width=72, height=72, corner_radius=36, fg_color=TEAL)
        ib.pack(pady=(28, 10))
        ib.pack_propagate(False)
        ctk.CTkLabel(ib, text=icon, font=("Arial", 32),
                     text_color="#ffffff").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text=title, font=("Arial", 15, "bold"), text_color=TEXT_DARK).pack()
        ctk.CTkLabel(card, text=desc, font=("Arial", 12),
                     text_color=TEXT_MID, justify="center").pack(pady=(10, 14))

        if command:
            self.primary_button(card, "Abrir módulo  →", command, width=175).pack(pady=4)
        else:
            ctk.CTkButton(card, text="Bloqueado", width=175, height=40,
                          corner_radius=12, fg_color="#e8e4dc",
                          text_color=TEXT_LIGHT, state="disabled").pack(pady=4)
        return card

    def info_item(self, parent, icon, label, value):
        item = ctk.CTkFrame(parent, fg_color="transparent")
        ib = ctk.CTkFrame(item, width=42, height=42, corner_radius=21, fg_color="#e0eff1")
        ib.pack(side="left", padx=(18, 10))
        ib.pack_propagate(False)
        ctk.CTkLabel(ib, text=icon, font=("Arial", 18),
                     text_color=TEAL).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(item, text=f"{label}\n{value}",
                     font=("Arial", 11), text_color=TEXT_DARK, justify="left").pack(side="left")
        return item

    def metric_card(self, parent, icon, title, value):
        card = ctk.CTkFrame(parent, width=195, height=165, corner_radius=20,
                            fg_color=CARD, border_width=1, border_color=BORDER)
        card.grid_propagate(False)
        card.pack_propagate(False)
        ib = ctk.CTkFrame(card, width=52, height=52, corner_radius=26, fg_color=TEAL)
        ib.pack(pady=(22, 6))
        ib.pack_propagate(False)
        ctk.CTkLabel(ib, text=icon, font=("Arial", 22),
                     text_color="#fff").place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(card, text=title, font=("Arial", 13, "bold"), text_color=TEXT_MID).pack()
        ctk.CTkLabel(card, text=value, font=("Arial", 22, "bold"), text_color=TEXT_DARK).pack(pady=(6, 0))
        return card

    #RECONHECER LIBRAS

    def show_predict(self):
        self.clear_content()

        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.pack(fill="both", expand=True, padx=42, pady=32)

        ctk.CTkLabel(page, text="Reconhecimento de Libras",
                     font=("Arial", 32, "bold"), text_color=TEXT_DARK
                     ).pack(anchor="w", pady=(0, 18))

        self.camera_label = ctk.CTkLabel(page, text="")
        self.camera_label.pack(pady=8)

        self.status_label = ctk.CTkLabel(page, text="Iniciando câmera...",
                                         font=("Arial", 16), text_color=TEXT_MID)
        self.status_label.pack(pady=8)

        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS,          30)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE,   1)

        self.update_camera()

    def extract_keypoints(self, results):
        keypoints = []
        if results.multi_hand_landmarks:
            for hl in results.multi_hand_landmarks:
                for lm in hl.landmark:
                    keypoints.extend([lm.x, lm.y, lm.z])
        while len(keypoints) < 126:
            keypoints.append(0)
        return np.array(keypoints[:126], dtype=np.float32)

    def update_camera(self):
        if self.camera is None:
            return
        success, frame = self.camera.read()
        if not success:
            self.status_label.configure(text="Erro ao abrir câmera.")
            return

        self.frame_counter += 1
        frame     = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results   = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hl in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hl, self.mp_hands.HAND_CONNECTIONS)

        keypoints    = self.extract_keypoints(results)
        current_time = time.time()
        self.frame_buffer.append((current_time, keypoints))

        while (self.frame_buffer and
               current_time - self.frame_buffer[0][0] > self.SEQUENCE_DURATION):
            self.frame_buffer.popleft()

        if len(self.frame_buffer) >= 15 and self.frame_counter % self.PREDICT_EVERY == 0:
            buf_kp   = [kp for (_, kp) in self.frame_buffer]
            indexes  = get_frame_indexes(len(buf_kp), SEQUENCE_LENGTH)
            inp_seq  = [buf_kp[i] for i in indexes]
            inp_data = np.array(inp_seq, dtype=np.float32)

            prediction       = self.model.predict(np.expand_dims(inp_data, 0), verbose=0)[0]
            predicted_index  = np.argmax(prediction)
            predicted_action = self.actions[predicted_index]
            self.confidence  = float(prediction[predicted_index])

            print("Predição:", np.round(prediction, 3))
            print("Classe prevista:", predicted_action, "| Confiança:", round(self.confidence, 3))

            if self.confidence > self.CONFIDENCE_THRESHOLD:
                if predicted_action == "neutro":
                    self.recognized_word  = "..."
                    self.last_prediction  = "neutro"
                    self.last_spoken_word = ""
                else:
                    self.recognized_word = predicted_action
                    if (predicted_action != self.last_prediction or
                            current_time - self.last_added_time > self.PREDICTION_DELAY):
                        if predicted_action != self.last_spoken_word:
                            translated = predicted_action.replace("_", " ")
                            speak(translated)
                            self.save_history(predicted_action, translated,
                                              "LIBRAS_TO_TEXT", round(self.confidence, 2))
                            self.last_spoken_word = predicted_action
                        self.last_prediction = predicted_action
                        self.last_added_time = current_time

        self.status_label.configure(
            text=f"Palavra: {self.recognized_word.upper()} | Confiança: {self.confidence:.2f}"
        )

        frame = cv2.resize(frame, (700, 400))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img   = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.camera_label.configure(image=imgtk)
        self.camera_label.image = imgtk

        self.app.after(15, self.update_camera)

    #VOZ PARA LIBRAS

    def show_voice_to_libras(self):
        self.clear_content()

        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.pack(fill="both", expand=True, padx=42, pady=32)

        ctk.CTkLabel(page, text="Voz para Libras",
                     font=("Arial", 32, "bold"), text_color=TEXT_DARK
                     ).pack(anchor="w", pady=(0, 18))

        self.voice_text = ctk.CTkTextbox(
            page, width=760, height=120, font=("Arial", 15),
            corner_radius=14, fg_color=CARD,
            border_width=1, border_color=BORDER, text_color=TEXT_DARK
        )
        self.voice_text.pack(pady=8)

        btns = ctk.CTkFrame(page, fg_color="transparent")
        btns.pack(pady=12)

        self.primary_button(btns, "🎙️  Falar", self.start_voice_capture, width=180).grid(row=0, column=0, padx=10)
        self.outline_button(btns, "Traduzir para Libras  →", self.translate_voice_to_libras, width=240).grid(row=0, column=1, padx=10)

        self.avatar_label = ctk.CTkLabel(page, text="")
        self.avatar_label.pack(pady=16)

        self.text_status = ctk.CTkLabel(page, text="Clique em Falar para usar o microfone.",
                                        font=("Arial", 14), text_color=TEXT_MID)
        self.text_status.pack(pady=4)

    def start_voice_capture(self):
        threading.Thread(target=self.capture_voice, daemon=True).start()

    def capture_voice(self):
        try:
            self.text_status.configure(text="Ouvindo...")
            with sr.Microphone() as src:
                self.recognizer.adjust_for_ambient_noise(src, duration=1)
                audio = self.recognizer.listen(src, timeout=5, phrase_time_limit=6)
            text = self.recognizer.recognize_google(audio, language="pt-BR")
            self.voice_text.delete("1.0", "end")
            self.voice_text.insert("1.0", text)
            self.text_status.configure(text=f"Texto reconhecido: {text}")
        except sr.UnknownValueError:
            self.text_status.configure(text="Não consegui entender a fala.")
        except Exception as e:
            self.text_status.configure(text=f"Erro: {str(e)}")

    def translate_voice_to_libras(self):
        text = self.voice_text.get("1.0", "end").strip().lower()
        if not text:
            messagebox.showwarning("Aviso", "Nenhum texto reconhecido.")
            return

        words_to_play = []
        if "tudo bem" in text:
            words_to_play.append("tudo bem")
            text = text.replace("tudo bem", "")
        for word in text.split():
            if word in self.sign_videos:
                words_to_play.append(word)

        if not words_to_play:
            messagebox.showwarning("Aviso", "Nenhum sinal encontrado para esse texto.")
            return

        self.save_history(text, ", ".join(words_to_play), "VOICE_TO_LIBRAS", None)
        self.words_queue = words_to_play
        self.play_next_avatar_video()

    def play_next_avatar_video(self):
        if not self.words_queue:
            self.text_status.configure(text="Tradução finalizada.")
            return
        word = self.words_queue.pop(0)
        self.text_status.configure(text=f"Mostrando sinal: {word}")
        self.avatar_cap = cv2.VideoCapture(self.sign_videos[word])
        self.update_avatar_video()

    def update_avatar_video(self):
        if self.avatar_cap is None:
            return
        success, frame = self.avatar_cap.read()
        if not success:
            self.avatar_cap.release()
            self.avatar_cap = None
            self.play_next_avatar_video()
            return
        frame = cv2.resize(frame, (520, 310))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img   = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.avatar_label.configure(image=imgtk)
        self.avatar_label.image = imgtk
        self.app.after(30, self.update_avatar_video)

    #HISTÓRICO
    def save_history(self, input_text, output_text, translation_type, confidence=None):
        try:
            requests.post(
                "http://127.0.0.1:8000/history/",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={
                    "user_id": self.current_user["id"],
                    "input_text": input_text,
                    "output_text": output_text,
                    "translation_type": translation_type,
                    "confidence": str(confidence) if confidence is not None else None,
                }
            )
        except Exception:
            pass

    def show_history(self):
        self.clear_content()

        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.pack(fill="both", expand=True, padx=42, pady=32)

        ctk.CTkLabel(page, text="Histórico de Traduções",
                     font=("Arial", 32, "bold"), text_color=TEXT_DARK
                     ).pack(anchor="w", pady=(0, 18))

        try:
            r = requests.get("http://127.0.0.1:8000/history/",
                             headers={"Authorization": f"Bearer {self.access_token}"})
            if r.status_code != 200:
                raise Exception()
            history = r.json()
        except Exception:
            ctk.CTkLabel(page, text="Não foi possível carregar o histórico.",
                         font=("Arial", 15), text_color=TEXT_MID).pack(anchor="w")
            return

        if not history:
            ctk.CTkLabel(page, text="Nenhuma tradução registrada ainda.",
                         font=("Arial", 15), text_color=TEXT_LIGHT).pack(anchor="w")
            return

        scroll = ctk.CTkScrollableFrame(page, width=850, height=520,
                                         fg_color="transparent",
                                         scrollbar_button_color=TEAL)
        scroll.pack(fill="both", expand=True)

        for item in reversed(history):
            card = ctk.CTkFrame(scroll, corner_radius=16, fg_color=CARD,
                                border_width=1, border_color=BORDER)
            card.pack(fill="x", pady=7, padx=4)

            title = f"{item['translation_type']}  |  Confiança: {item['confidence'] or 'N/A'}"

            if self.current_user["role"] == "ADMIN":
                ctk.CTkLabel(card,
                             text=f"Usuário: {item.get('user_name','N/A')} | {item.get('user_email','N/A')}",
                             font=("Arial", 12, "bold"),
                             text_color=TEXT_MID).pack(anchor="w", padx=18, pady=(10, 0))

            ctk.CTkLabel(card, text=title, font=("Arial", 13, "bold"),
                         text_color=TEAL).pack(anchor="w", padx=18, pady=(10, 3))
            ctk.CTkLabel(card, text=f"Entrada: {item['input_text']}",
                         font=("Arial", 13), text_color=TEXT_DARK).pack(anchor="w", padx=18)
            ctk.CTkLabel(card, text=f"Saída: {item['output_text']}",
                         font=("Arial", 13), text_color=TEXT_MID).pack(anchor="w", padx=18, pady=(0, 12))

    #MÉTRICAS

    def show_metrics(self):
        self.clear_content()

        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.pack(fill="both", expand=True, padx=42, pady=32)

        ctk.CTkLabel(page, text="Dashboard Administrativo",
                     font=("Arial", 32, "bold"), text_color=TEXT_DARK
                     ).pack(anchor="w", pady=(0, 22))

        try:
            r = requests.get("http://127.0.0.1:8000/dashboard/",
                             headers={"Authorization": f"Bearer {self.access_token}"})
            if r.status_code != 200:
                raise Exception()
            data = r.json()
        except Exception:
            ctk.CTkLabel(page, text="Não foi possível carregar o dashboard.",
                         font=("Arial", 16), text_color=TEXT_MID).pack(anchor="w")
            return

        cards_row = ctk.CTkFrame(page, fg_color="transparent")
        cards_row.pack(fill="x", pady=(0, 20))

        self.metric_card(cards_row, "👥", "Usuários",
                         str(data.get("total_users", 0))).grid(row=0, column=0, padx=(0, 12))
        self.metric_card(cards_row, "🤟", "Traduções",
                         str(data.get("total_translations", 0))).grid(row=0, column=1, padx=12)
        self.metric_card(cards_row, "📅", "Hoje",
                         str(data.get("translations_today", 0))).grid(row=0, column=2, padx=12)
        self.metric_card(cards_row, "🕒", "Última atividade",
                         str(data.get("last_translation", "N/A"))).grid(row=0, column=3, padx=(12, 0))

        charts = ctk.CTkFrame(page, fg_color="transparent")
        charts.pack(fill="both", expand=True)

        lc = ctk.CTkFrame(charts, corner_radius=18, fg_color=CARD,
                          border_width=1, border_color=BORDER)
        lc.pack(side="left", fill="both", expand=True, padx=(0, 10))

        rc = ctk.CTkFrame(charts, corner_radius=18, fg_color=CARD,
                          border_width=1, border_color=BORDER)
        rc.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ctk.CTkLabel(lc, text="Traduções por Dia",
                     font=("Arial", 18, "bold"), text_color=TEXT_DARK
                     ).pack(anchor="w", padx=20, pady=(18, 4))
        ctk.CTkLabel(rc, text="Tipos de Tradução",
                     font=("Arial", 18, "bold"), text_color=TEXT_DARK
                     ).pack(anchor="w", padx=20, pady=(18, 4))

        self.draw_bar_chart(lc, data.get("translations_by_day",  []), "date", "total")
        self.draw_bar_chart(rc, data.get("translations_by_type", []), "type", "total")

    def draw_bar_chart(self, parent, data, x_key, y_key):
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=18, pady=12)

        if not data:
            ctk.CTkLabel(container, text="Sem dados para exibir.",
                         font=("Arial", 14), text_color=TEXT_LIGHT).pack(expand=True)
            return

        labels = [str(i.get(x_key, "")) for i in data]
        values = [i.get(y_key, 0) for i in data]

        fig = Figure(figsize=(4.2, 2.7), dpi=100, facecolor="#ffffff")
        ax  = fig.add_subplot(111)
        ax.set_facecolor("#ffffff")
        ax.bar(labels, values, color=TEAL, width=0.55)
        ax.tick_params(axis="x", colors=TEXT_MID, labelsize=8, rotation=25)
        ax.tick_params(axis="y", colors=TEXT_MID, labelsize=8)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["bottom"].set_color(BORDER)
        ax.spines["left"].set_color(BORDER)
        ax.grid(axis="y", color="#ece9e2", linestyle="--", linewidth=0.7)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    #FINALIZAR
    def stop_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.frame_buffer.clear()

    def stop_avatar(self):
        if self.avatar_cap is not None:
            self.avatar_cap.release()
            self.avatar_cap = None

    def close_app(self):
        self.stop_camera()
        self.stop_avatar()
        self.app.destroy()


if __name__ == "__main__":
    JarvisLibrasApp()