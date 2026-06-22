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

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# Mesmo tamanho de sequência usado no treino (SEQUENCE_LENGTH em
# train_model.py / video_to_dataset.py)
SEQUENCE_LENGTH = 30


def get_frame_indexes(total_frames, sequence_length):
    """Reamostra um buffer de frames para `sequence_length` posições,
    da mesma forma que video_to_dataset.py faz com np.linspace ao
    converter os vídeos de treino."""

    if total_frames <= 0:
        return []

    return np.linspace(
        0,
        total_frames - 1,
        sequence_length,
        dtype=int
    )


class JarvisLibrasApp:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Jarvis Libras IA")
        self.app.geometry("1280x720")
        self.app.resizable(False, False)
        self.app.configure(fg_color="#07070d")

        self.current_user = None
        self.access_token = None

        self.model = load_model("models/libras_model.h5")
        self.actions = np.load("models/actions.npy", allow_pickle=True)

        self.recognizer = sr.Recognizer()

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.camera = None

        # Buffer com (timestamp, keypoints) cobrindo os últimos
        # SEQUENCE_DURATION segundos de câmera. Na hora de prever, esse
        # buffer é reamostrado para SEQUENCE_LENGTH frames com
        # get_frame_indexes, igual ao que video_to_dataset.py faz com os
        # vídeos de treino (que duram ~3 a 4 segundos).
        self.frame_buffer = deque()
        self.SEQUENCE_DURATION = 3.5

        self.last_prediction = ""
        self.last_spoken_word = ""
        self.last_added_time = 0
        self.frame_counter = 0

        self.recognized_word = "..."
        self.confidence = 0.0

        self.PREDICT_EVERY = 8
        self.CONFIDENCE_THRESHOLD = 0.75
        self.PREDICTION_DELAY = 2

        self.avatar_cap = None
        self.words_queue = []

        self.sign_videos = {
            "oi": "assets/oi.mp4",
            "sim": "assets/sim.mp4",
            "nao": "assets/nao.mp4",
            "não": "assets/nao.mp4",
            "e": "assets/e.mp4",
            "voce": "assets/voce.mp4",
            "você": "assets/voce.mp4",
            "tudo_bem": "assets/tudo_bem.mp4",
            "tudo bem": "assets/tudo_bem.mp4"
        }

        self.show_login_screen()
        self.app.mainloop()

    def clear_window(self):
        for widget in self.app.winfo_children():
            widget.destroy()

    def clear_content(self):
        self.stop_camera()
        self.stop_avatar()

        for widget in self.content.winfo_children():
            widget.destroy()

    def pink_button(self, parent, text, command, width=240):
        return ctk.CTkButton(
            parent,
            text=text,
            width=width,
            height=46,
            corner_radius=14,
            fg_color="#ff7ab8",
            hover_color="#ff9ccd",
            text_color="#111111",
            font=("Arial", 14, "bold"),
            command=command
        )

    def dark_button(self, parent, text, command, width=190):
        return ctk.CTkButton(
            parent,
            text=text,
            width=width,
            height=44,
            corner_radius=14,
            fg_color="#15151f",
            hover_color="#232334",
            border_width=1,
            border_color="#2f2f3f",
            text_color="#f5f5f5",
            font=("Arial", 14, "bold"),
            command=command
        )

    # =========================
    # LOGIN
    # =========================

    def show_login_screen(self):
        self.clear_window()
        self.app.configure(fg_color="#07070d")

        card = ctk.CTkFrame(
            self.app,
            width=430,
            height=520,
            corner_radius=28,
            fg_color="#11111a",
            border_width=1,
            border_color="#2e2e3d"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card,
            text="🤟 Jarvis",
            font=("Arial", 34, "bold"),
            text_color="#ff7ab8"
        ).pack(pady=(45, 0))

        ctk.CTkLabel(
            card,
            text="Libras IA",
            font=("Arial", 20),
            text_color="#ffffff"
        ).pack(pady=(0, 30))

        self.email_entry = ctk.CTkEntry(
            card,
            width=310,
            height=45,
            placeholder_text="E-mail",
            fg_color="#1a1a25",
            border_color="#333344",
            text_color="#ffffff",
            font=("Arial", 14)
        )
        self.email_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            card,
            width=310,
            height=45,
            placeholder_text="Senha",
            show="*",
            fg_color="#1a1a25",
            border_color="#333344",
            text_color="#ffffff",
            font=("Arial", 14)
        )
        self.password_entry.pack(pady=10)

        self.pink_button(card, "Entrar  →", self.login_user, width=310).pack(pady=(30, 12))
        self.dark_button(card, "Criar conta", self.show_register_screen, width=310).pack()

    def show_register_screen(self):
        self.clear_window()

        card = ctk.CTkFrame(
            self.app,
            width=430,
            height=560,
            corner_radius=28,
            fg_color="#11111a",
            border_width=1,
            border_color="#2e2e3d"
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            card,
            text="Criar conta",
            font=("Arial", 30, "bold"),
            text_color="#ff7ab8"
        ).pack(pady=(40, 25))

        self.register_name = ctk.CTkEntry(card, width=310, height=45, placeholder_text="Nome")
        self.register_name.pack(pady=9)

        self.register_email = ctk.CTkEntry(card, width=310, height=45, placeholder_text="E-mail")
        self.register_email.pack(pady=9)

        self.register_password = ctk.CTkEntry(
            card,
            width=310,
            height=45,
            placeholder_text="Senha",
            show="*"
        )
        self.register_password.pack(pady=9)

        ctk.CTkLabel(
            card,
            text="Novas contas são cadastradas como USUÁRIO.",
            font=("Arial", 12),
            text_color="#bcbcbc"
        ).pack(pady=(10, 10))

        self.pink_button(card, "Cadastrar", self.register_user, width=310).pack(pady=(10, 12))
        self.dark_button(card, "Voltar", self.show_login_screen, width=310).pack()

    def login_user(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Aviso", "Preencha e-mail e senha.")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:8000/auth/login",
                json={"email": email, "password": password}
            )

            if response.status_code != 200:
                messagebox.showerror("Erro", "Usuário ou senha inválidos.")
                return

            data = response.json()
            self.current_user = data["user"]
            self.access_token = data["access_token"]

            self.clear_window()
            self.build_layout()
            self.show_home()

        except Exception:
            messagebox.showerror("Erro", "Backend não está rodando.")

    def register_user(self):
        name = self.register_name.get().strip()
        email = self.register_email.get().strip()
        password = self.register_password.get().strip()

        if not name or not email or not password:
            messagebox.showwarning("Aviso", "Preencha todos os campos.")
            return

        try:
            response = requests.post(
                "http://127.0.0.1:8000/auth/register",
                json={"name": name, "email": email, "password": password}
            )

            if response.status_code != 200:
                messagebox.showerror(
                    "Erro",
                    response.json().get("detail", "Erro ao cadastrar.")
                )
                return

            messagebox.showinfo("Sucesso", "Conta criada com sucesso.")
            self.show_login_screen()

        except Exception:
            messagebox.showerror("Erro", "Backend não está rodando.")

    # =========================
    # LAYOUT PRINCIPAL
    # =========================

    def build_layout(self):
        self.sidebar = ctk.CTkFrame(
            self.app,
            width=285,
            corner_radius=0,
            fg_color="#0d0d16",
            border_width=1,
            border_color="#242435"
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ctk.CTkFrame(
            self.app,
            corner_radius=0,
            fg_color="#07070d"
        )
        self.content.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(
            self.sidebar,
            text="🤟 Jarvis",
            font=("Arial", 30, "bold"),
            text_color="#ff7ab8"
        ).pack(pady=(45, 0), padx=25, anchor="w")

        ctk.CTkLabel(
            self.sidebar,
            text="Libras IA",
            font=("Arial", 20),
            text_color="#ffffff"
        ).pack(pady=(0, 30), padx=75, anchor="w")

        profile = ctk.CTkFrame(
            self.sidebar,
            height=90,
            corner_radius=18,
            fg_color="#15151f",
            border_width=1,
            border_color="#303044"
        )
        profile.pack(padx=24, pady=(0, 25), fill="x")
        profile.pack_propagate(False)

        ctk.CTkLabel(
            profile,
            text="👤",
            font=("Arial", 30),
            text_color="#ff7ab8"
        ).pack(side="left", padx=(18, 12))

        ctk.CTkLabel(
            profile,
            text=f"{self.current_user['name']}\n{self.current_user['role']}",
            font=("Arial", 13, "bold"),
            text_color="#ffffff",
            justify="left"
        ).pack(side="left")

        self.nav_button("🏠  Início", self.show_home, active=True)
        self.nav_button("🤟  Reconhecer Libras", self.show_predict)
        self.nav_button("🎙️  Voz para Libras", self.show_voice_to_libras)
        self.nav_button("🕘  Histórico", self.show_history)

        if self.current_user["role"] == "ADMIN":
            self.nav_button("📊  Métricas da API", self.show_metrics)

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#242435").pack(
            fill="x",
            padx=35,
            pady=18
        )

        self.nav_button("↪  Logout", self.logout_user)
        self.nav_button("🚪  Sair", self.close_app)

        ctk.CTkLabel(
            self.sidebar,
            text="Jarvis Libras IA\nv1.0.0",
            font=("Arial", 12),
            text_color="#999999"
        ).pack(side="bottom", pady=35)

    def nav_button(self, text, command, active=False):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            width=235,
            height=56,
            corner_radius=14,
            fg_color="#d9528f" if active else "#15151f",
            hover_color="#ff7ab8",
            border_width=1,
            border_color="#303044",
            text_color="#ffffff",
            font=("Arial", 14, "bold"),
            anchor="w",
            command=command
        )
        btn.pack(padx=24, pady=6)

    def logout_user(self):
        self.stop_camera()
        self.stop_avatar()
        self.current_user = None
        self.access_token = None
        self.show_login_screen()

    # =========================
    # HOME
    # =========================

    def show_home(self):
        self.clear_content()

        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=45, pady=35)

        top = ctk.CTkFrame(main, fg_color="transparent", height=190)
        top.pack(fill="x")
        top.pack_propagate(False)

        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            left,
            text=f"Olá, {self.current_user['name'].split()[0]}! 👋",
            font=("Arial", 38, "bold"),
            text_color="#ffffff"
        ).pack(anchor="w", pady=(20, 8))

        ctk.CTkLabel(
            left,
            text="Bem-vinda ao Jarvis Libras IA",
            font=("Arial", 22),
            text_color="#cccccc"
        ).pack(anchor="w")

        ctk.CTkFrame(
            left,
            width=80,
            height=4,
            corner_radius=10,
            fg_color="#ff7ab8"
        ).pack(anchor="w", pady=(28, 0))

        hero = ctk.CTkFrame(
            top,
            width=250,
            height=165,
            corner_radius=24,
            fg_color="#11111a",
            border_width=1,
            border_color="#28283a"
        )
        hero.pack(side="right", padx=(20, 0), pady=(5, 0))
        hero.pack_propagate(False)

        ctk.CTkLabel(
            hero,
            text="🤟",
            font=("Arial", 70),
            text_color="#ff7ab8"
        ).pack(pady=(25, 0))

        ctk.CTkLabel(
            hero,
            text="IA + Acessibilidade",
            font=("Arial", 15, "bold"),
            text_color="#ff7ab8"
        ).pack(pady=(0, 8))

        cards = ctk.CTkFrame(main, fg_color="transparent")
        cards.pack(fill="x", pady=(28, 25))

        self.home_card(
            cards,
            "🤟",
            "Reconhecer Libras",
            "Use a câmera para reconhecer\nsinais em Libras em tempo real.",
            self.show_predict
        ).grid(row=0, column=0, padx=(0, 18))

        self.home_card(
            cards,
            "🎙️",
            "Voz para Libras",
            "Fale algo e veja a tradução\nem Libras com nosso avatar.",
            self.show_voice_to_libras
        ).grid(row=0, column=1, padx=18)

        if self.current_user["role"] == "ADMIN":
            self.home_card(
                cards,
                "📊",
                "Métricas da API",
                "Visualize estatísticas e métricas\nde uso da API.",
                self.show_metrics
            ).grid(row=0, column=2, padx=(18, 0))
        else:
            self.home_card(
                cards,
                "🔒",
                "Métricas da API",
                "Disponível somente para\nadministradores.",
                None
            ).grid(row=0, column=2, padx=(18, 0))

        bottom = ctk.CTkFrame(
            main,
            height=92,
            corner_radius=20,
            fg_color="#11111a",
            border_width=1,
            border_color="#28283a"
        )
        bottom.pack(fill="x", pady=(5, 0))
        bottom.pack_propagate(False)

        today = datetime.now().strftime("%d/%m/%Y")
        hour = datetime.now().strftime("%H:%M")

        self.info_item(bottom, "👥", "Seu perfil", self.current_user["role"]).pack(side="left", expand=True, fill="both")
        self.info_item(bottom, "📅", "Data de acesso", today).pack(side="left", expand=True, fill="both")
        self.info_item(bottom, "🕒", "Horário", hour).pack(side="left", expand=True, fill="both")
        self.info_item(bottom, "🛡️", "Sessão segura", "Ativa").pack(side="left", expand=True, fill="both")

    def home_card(self, parent, icon, title, desc, command):
        card = ctk.CTkFrame(
            parent,
            width=225,
            height=275,
            corner_radius=22,
            fg_color="#11111a",
            border_width=1,
            border_color="#2d2d3d"
        )
        card.grid_propagate(False)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=icon,
            font=("Arial", 48),
            text_color="#ff7ab8"
        ).pack(pady=(30, 8))

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 20, "bold"),
            text_color="#ff7ab8"
        ).pack()

        ctk.CTkLabel(
            card,
            text=desc,
            font=("Arial", 13),
            text_color="#d2d2d2",
            justify="center"
        ).pack(pady=(16, 14))

        if command:
            self.dark_button(card, "Abrir módulo   →", command, width=175).pack(pady=5)
        else:
            ctk.CTkButton(
                card,
                text="Bloqueado",
                width=175,
                height=42,
                corner_radius=14,
                fg_color="#2a2a35",
                text_color="#888888",
                state="disabled"
            ).pack(pady=5)

        return card




    def metric_card(self, parent, icon, title, value):
        card = ctk.CTkFrame(
            parent,
            width=200,
            height=170,
            corner_radius=22,
            fg_color="#11111a",
            border_width=1,
            border_color="#2d2d3d"
        )

        card.grid_propagate(False)
        card.pack_propagate(False)

        ctk.CTkLabel(
            card,
            text=icon,
            font=("Arial", 42),
            text_color="#ff7ab8"
        ).pack(pady=(25, 8))

        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 16, "bold"),
            text_color="#cccccc"
        ).pack()

        ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 22, "bold"),
            text_color="#ffffff"
        ).pack(pady=(8, 0))

        return card


    def info_item(self, parent, icon, label, value):
        item = ctk.CTkFrame(parent, fg_color="transparent")

        ctk.CTkLabel(
            item,
            text=icon,
            font=("Arial", 25),
            text_color="#ff7ab8"
        ).pack(side="left", padx=(20, 10))

        ctk.CTkLabel(
            item,
            text=f"{label}\n{value}",
            font=("Arial", 12),
            text_color="#ffffff",
            justify="left"
        ).pack(side="left")

        return item

    # =========================
    # RECONHECER LIBRAS
    # =========================

    def show_predict(self):
        self.clear_content()

        frame_page = ctk.CTkFrame(self.content, fg_color="transparent")
        frame_page.pack(fill="both", expand=True, padx=45, pady=35)

        ctk.CTkLabel(
            frame_page,
            text="Reconhecimento de Libras",
            font=("Arial", 34, "bold"),
            text_color="#ff7ab8"
        ).pack(anchor="w", pady=(0, 20))

        self.camera_label = ctk.CTkLabel(frame_page, text="")
        self.camera_label.pack(pady=10)

        self.status_label = ctk.CTkLabel(
            frame_page,
            text="Iniciando câmera...",
            font=("Arial", 18),
            text_color="#ffffff"
        )
        self.status_label.pack(pady=10)

        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.update_camera()

    def extract_keypoints(self, results):
        keypoints = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for landmark in hand_landmarks.landmark:
                    keypoints.extend([landmark.x, landmark.y, landmark.z])

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

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

        keypoints = self.extract_keypoints(results)

        current_time = time.time()
        self.frame_buffer.append((current_time, keypoints))

        # Mantém no buffer apenas os últimos SEQUENCE_DURATION segundos
        while (
            self.frame_buffer
            and current_time - self.frame_buffer[0][0] > self.SEQUENCE_DURATION
        ):
            self.frame_buffer.popleft()

        if len(self.frame_buffer) >= 15 and self.frame_counter % self.PREDICT_EVERY == 0:
            buffer_keypoints = [kp for (_, kp) in self.frame_buffer]

            # Reamostra o buffer para SEQUENCE_LENGTH frames, igual ao
            # np.linspace usado em video_to_dataset.py
            indexes = get_frame_indexes(len(buffer_keypoints), SEQUENCE_LENGTH)
            input_sequence = [buffer_keypoints[i] for i in indexes]

            input_data = np.array(input_sequence, dtype=np.float32)

            prediction = self.model.predict(
                np.expand_dims(input_data, axis=0),
                verbose=0
            )[0]

            predicted_index = np.argmax(prediction)
            predicted_action = self.actions[predicted_index]
            self.confidence = float(prediction[predicted_index])

            # Debug: remova estes prints depois de validar o reconhecimento
            print("Predição:", np.round(prediction, 3))
            print("Classe prevista:", predicted_action, "| Confiança:", round(self.confidence, 3))

            if self.confidence > self.CONFIDENCE_THRESHOLD:
                if predicted_action == "neutro":
                    self.recognized_word = "..."
                    self.last_prediction = "neutro"
                    self.last_spoken_word = ""
                else:
                    self.recognized_word = predicted_action

                    if (
                        predicted_action != self.last_prediction
                        or current_time - self.last_added_time > self.PREDICTION_DELAY
                    ):
                        
                        if predicted_action != self.last_spoken_word:

                            translated_word = predicted_action.replace("_", " ")

                            speak(translated_word)

                            self.save_history(
                                input_text=predicted_action,
                                output_text=translated_word,
                                translation_type="LIBRAS_TO_TEXT",
                                confidence=round(self.confidence, 2)
                            )

                            self.last_spoken_word = predicted_action
                        
                        
                        
                        self.last_prediction = predicted_action
                        self.last_added_time = current_time

        self.status_label.configure(
            text=f"Palavra: {self.recognized_word.upper()} | Confiança: {self.confidence:.2f}"
        )

        frame = cv2.resize(frame, (700, 400))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        self.camera_label.configure(image=imgtk)
        self.camera_label.image = imgtk

        self.app.after(15, self.update_camera)

    # =========================
    # VOZ PARA LIBRAS
    # =========================

    def show_voice_to_libras(self):
        self.clear_content()

        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.pack(fill="both", expand=True, padx=45, pady=35)

        ctk.CTkLabel(
            page,
            text="Voz para Libras",
            font=("Arial", 34, "bold"),
            text_color="#ff7ab8"
        ).pack(anchor="w", pady=(0, 20))

        self.voice_text = ctk.CTkTextbox(
            page,
            width=760,
            height=130,
            font=("Arial", 16),
            corner_radius=18,
            fg_color="#11111a",
            border_width=1,
            border_color="#2d2d3d"
        )
        self.voice_text.pack(pady=10)

        buttons = ctk.CTkFrame(page, fg_color="transparent")
        buttons.pack(pady=15)

        self.pink_button(buttons, "🎙️  Falar", self.start_voice_capture, width=190).grid(row=0, column=0, padx=10)
        self.dark_button(buttons, "Traduzir para Libras  →", self.translate_voice_to_libras, width=250).grid(row=0, column=1, padx=10)

        self.avatar_label = ctk.CTkLabel(page, text="")
        self.avatar_label.pack(pady=20)

        self.text_status = ctk.CTkLabel(
            page,
            text="Clique em Falar para usar o microfone.",
            font=("Arial", 15),
            text_color="#cccccc"
        )
        self.text_status.pack(pady=5)

    def start_voice_capture(self):
        threading.Thread(target=self.capture_voice, daemon=True).start()

    def capture_voice(self):
        try:
            self.text_status.configure(text="Ouvindo...")

            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=6)

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

        self.save_history(
            input_text=text,
            output_text=", ".join(words_to_play),
            translation_type="VOICE_TO_LIBRAS",
            confidence=None
        )

        self.words_queue = words_to_play
        self.play_next_avatar_video()

    def play_next_avatar_video(self):
        if not self.words_queue:
            self.text_status.configure(text="Tradução finalizada.")
            return

        word = self.words_queue.pop(0)
        video_path = self.sign_videos[word]

        self.text_status.configure(text=f"Mostrando sinal: {word}")

        self.avatar_cap = cv2.VideoCapture(video_path)
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

        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        self.avatar_label.configure(image=imgtk)
        self.avatar_label.image = imgtk

        self.app.after(30, self.update_avatar_video)

    # =========================
    # HISTÓRICO
    # =========================

    def save_history(self, input_text, output_text, translation_type, confidence=None):
        try:
            requests.post(
                "http://127.0.0.1:8000/history/",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                },
                json={
                    "user_id": self.current_user["id"],
                    "input_text": input_text,
                    "output_text": output_text,
                    "translation_type": translation_type,
                    "confidence": str(confidence) if confidence is not None else None
                }
            )

        except Exception:
            pass

    def show_history(self):
        self.clear_content()

        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.pack(fill="both", expand=True, padx=45, pady=35)

        ctk.CTkLabel(
            page,
            text="Histórico de Traduções",
            font=("Arial", 34, "bold"),
            text_color="#ff7ab8"
        ).pack(anchor="w", pady=(0, 20))

        try:
            response = requests.get(
                "http://127.0.0.1:8000/history/",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )

            if response.status_code != 200:
                ctk.CTkLabel(
                    page,
                    text="Não foi possível carregar o histórico.",
                    font=("Arial", 16),
                    text_color="#ffffff"
                ).pack(anchor="w")
                return

            history = response.json()

        except Exception:
            ctk.CTkLabel(
                page,
                text="Backend não está rodando.",
                font=("Arial", 16),
                text_color="#ffffff"
            ).pack(anchor="w")
            return

        if not history:
            ctk.CTkLabel(
                page,
                text="Nenhuma tradução registrada ainda.",
                font=("Arial", 16),
                text_color="#cccccc"
            ).pack(anchor="w")
            return

        scroll = ctk.CTkScrollableFrame(
            page,
            width=850,
            height=520,
            fg_color="transparent"
        )
        scroll.pack(fill="both", expand=True)

        for item in reversed(history):
            card = ctk.CTkFrame(
                scroll,
                corner_radius=18,
                fg_color="#11111a",
                border_width=1,
                border_color="#2d2d3d"
            )
            card.pack(fill="x", pady=8, padx=5)

            title = (
                f"{item['translation_type']}  |  "
                f"Confiança: {item['confidence'] or 'N/A'}"
            )

            if self.current_user["role"] == "ADMIN":
                ctk.CTkLabel(
                    card,
                    text=f"Usuário: {item.get('user_name', 'N/A')} | {item.get('user_email', 'N/A')}",
                    font=("Arial", 13, "bold"),
                    text_color="#ffffff"
            ).pack(anchor="w", padx=20, pady=(0, 6))

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 14, "bold"),
                text_color="#ff7ab8"
            ).pack(anchor="w", padx=20, pady=(12, 4))

            ctk.CTkLabel(
                card,
                text=f"Entrada: {item['input_text']}",
                font=("Arial", 14),
                text_color="#ffffff"
            ).pack(anchor="w", padx=20)

            ctk.CTkLabel(
                card,
                text=f"Saída: {item['output_text']}",
                font=("Arial", 14),
                text_color="#cccccc"
            ).pack(anchor="w", padx=20, pady=(0, 12))

    # =========================
    # MÉTRICAS
    # =========================

    def show_metrics(self):
        self.clear_content()

        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.pack(fill="both", expand=True, padx=45, pady=35)

        ctk.CTkLabel(
            page,
            text="Dashboard Administrativo",
            font=("Arial", 34, "bold"),
            text_color="#ff7ab8"
        ).pack(anchor="w", pady=(0, 25))

        try:
            response = requests.get(
                "http://127.0.0.1:8000/dashboard/",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )

            if response.status_code != 200:
                raise Exception()

            data = response.json()

        except Exception:
            ctk.CTkLabel(
                page,
                text="Não foi possível carregar o dashboard.",
                font=("Arial", 18),
                text_color="#ffffff"
            ).pack(anchor="w")
            return

        cards = ctk.CTkFrame(page, fg_color="transparent")
        cards.pack(fill="x", pady=(0, 22))

        self.metric_card(
            cards,
            "👥",
            "Usuários",
            str(data.get("total_users", 0))
        ).grid(row=0, column=0, padx=(0, 12))

        self.metric_card(
            cards,
            "🤟",
            "Traduções",
            str(data.get("total_translations", 0))
        ).grid(row=0, column=1, padx=12)

        self.metric_card(
            cards,
            "📅",
            "Hoje",
            str(data.get("translations_today", 0))
        ).grid(row=0, column=2, padx=12)

        self.metric_card(
            cards,
            "🕒",
            "Última atividade",
            str(data.get("last_translation", "N/A"))
        ).grid(row=0, column=3, padx=(12, 0))

        charts = ctk.CTkFrame(page, fg_color="transparent")
        charts.pack(fill="both", expand=True)

        left_chart = ctk.CTkFrame(
            charts,
            corner_radius=22,
            fg_color="#11111a",
            border_width=1,
            border_color="#2d2d3d"
        )
        left_chart.pack(side="left", fill="both", expand=True, padx=(0, 12))

        right_chart = ctk.CTkFrame(
            charts,
            corner_radius=22,
            fg_color="#11111a",
            border_width=1,
            border_color="#2d2d3d"
        )
        right_chart.pack(side="right", fill="both", expand=True, padx=(12, 0))

        ctk.CTkLabel(
            left_chart,
            text="Traduções por Dia",
            font=("Arial", 20, "bold"),
            text_color="#ff7ab8"
        ).pack(anchor="w", padx=22, pady=(20, 5))

        ctk.CTkLabel(
            right_chart,
            text="Tipos de Tradução",
            font=("Arial", 20, "bold"),
            text_color="#ff7ab8"
        ).pack(anchor="w", padx=22, pady=(20, 5))

        self.draw_bar_chart(
            left_chart,
            data.get("translations_by_day", []),
            x_key="date",
            y_key="total"
        )

        self.draw_bar_chart(
            right_chart,
            data.get("translations_by_type", []),
            x_key="type",
            y_key="total"
        )

    def draw_bar_chart(self, parent, data, x_key, y_key):
        chart_container = ctk.CTkFrame(parent, fg_color="transparent")
        chart_container.pack(fill="both", expand=True, padx=20, pady=15)

        if not data:
            ctk.CTkLabel(
                chart_container,
                text="Sem dados para exibir.",
                font=("Arial", 15),
                text_color="#cccccc"
            ).pack(expand=True)
            return

        labels = [str(item.get(x_key, "")) for item in data]
        values = [item.get(y_key, 0) for item in data]

        fig = Figure(
            figsize=(4.2, 2.7),
            dpi=100,
            facecolor="#11111a"
        )

        ax = fig.add_subplot(111)
        ax.set_facecolor("#11111a")

        ax.bar(labels, values, color="#ff7ab8")

        ax.tick_params(axis="x", colors="#ffffff", labelsize=8, rotation=25)
        ax.tick_params(axis="y", colors="#ffffff", labelsize=8)

        ax.spines["bottom"].set_color("#444455")
        ax.spines["left"].set_color("#444455")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.grid(axis="y", color="#2d2d3d", linestyle="--", linewidth=0.6)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # =========================
    # FINALIZAR
    # =========================

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