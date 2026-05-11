import customtkinter as ctk
from tkinter import messagebox
import cv2
import os
import threading



ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")



SIGN_VIDEOS = {
    "oi": "assets/oi.mp4",
    "sim": "assets/sim.mp4",
    "nao": "assets/nao.mp4",
    "não": "assets/nao.mp4",
    "e": "assets/e.mp4",
    "voce": "assets/voce.mp4",
    "você": "assets/voce.mp4",
    "tudo bem": "assets/tudo_bem.mp4"
}

def play_video(video_path):
    if not os.path.exists(video_path):
        print(f"Vídeo não encontrado: {video_path}")
        return

    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break

        cv2.imshow("Avatar Libras", frame)

        if cv2.waitKey(25) == 27:
            break

    cap.release()
    cv2.destroyWindow("Avatar Libras")

def translate_text():
    text = input_text.get("1.0", "end").strip().lower()

    if not text:
        messagebox.showwarning("Aviso", "Digite alguma coisa primeiro.")
        return

    words_to_play = []

    if "tudo bem" in text:
        words_to_play.append("tudo bem")
        text = text.replace("tudo bem", "")

    for word in text.split():
        if word in SIGN_VIDEOS:
            words_to_play.append(word)

    if not words_to_play:
        messagebox.showwarning(
            "Aviso",
            "Nenhum sinal encontrado para esse texto."
        )
        return

    status_label.configure(text="Traduzindo para Libras...")

    def run_avatar():
        for word in words_to_play:
            video_path = SIGN_VIDEOS[word]
            play_video(video_path)

        status_label.configure(text="Tradução finalizada.")

    threading.Thread(target=run_avatar, daemon=True).start()

def clear_text():
    input_text.delete("1.0", "end")
    status_label.configure(text="Aguardando texto...")

# INTERFACE

app = ctk.CTk()
app.title("Jarvis Libras")
app.geometry("700x500")
app.resizable(False, False)

main_frame = ctk.CTkFrame(app, corner_radius=20)
main_frame.pack(padx=30, pady=30, fill="both", expand=True)

title = ctk.CTkLabel(
    main_frame,
    text="Jarvis Libras",
    font=("Arial", 28, "bold")
)
title.pack(pady=(25, 5))

subtitle = ctk.CTkLabel(
    main_frame,
    text="Digite uma frase e transforme em sinais de Libras",
    font=("Arial", 15)
)
subtitle.pack(pady=(0, 25))

input_text = ctk.CTkTextbox(
    main_frame,
    width=580,
    height=140,
    font=("Arial", 16),
    corner_radius=15
)
input_text.pack(pady=10)

buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
buttons_frame.pack(pady=20)

translate_button = ctk.CTkButton(
    buttons_frame,
    text="Traduzir para Libras",
    width=220,
    height=45,
    font=("Arial", 15, "bold"),
    command=translate_text
)
translate_button.grid(row=0, column=0, padx=10)

clear_button = ctk.CTkButton(
    buttons_frame,
    text="Limpar",
    width=120,
    height=45,
    font=("Arial", 15),
    fg_color="#444444",
    hover_color="#666666",
    command=clear_text
)
clear_button.grid(row=0, column=1, padx=10)

status_label = ctk.CTkLabel(
    main_frame,
    text="Aguardando texto...",
    font=("Arial", 14)
)
status_label.pack(pady=10)

available_label = ctk.CTkLabel(
    main_frame,
    text="Sinais disponíveis: oi, sim, não, e, você, tudo bem",
    font=("Arial", 12)
)
available_label.pack(pady=(15, 5))

footer = ctk.CTkLabel(
    main_frame,
    text="Projeto Jarvis Libras • IA + Acessibilidade",
    font=("Arial", 11)
)
footer.pack(pady=(10, 20))

app.mainloop()
