import edge_tts
import asyncio
import pygame
import tempfile
import os
import threading

# Voz neural em português do Brasil
VOICE = "pt-BR-FranciscaNeural"

# Corrigir pronúncia das palavras
PRONUNCIATION_MAP = {
    "maca": "maçã",
    "america": "América",
    "voce": "você",
    "nao": "não",
    "tudo_bem": "tudo bem"
}


def normalize_text(text):
    text = text.lower().strip()
    return PRONUNCIATION_MAP.get(text, text.replace("_", " "))


async def _speak_async(text):
    text = normalize_text(text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        audio_path = temp_audio.name

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="-5%",
        volume="+0%"
    )

    await communicate.save(audio_path)

    pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    pygame.mixer.quit()

    try:
        os.remove(audio_path)
    except:
        pass


def speak(text):
    threading.Thread(
        target=lambda: asyncio.run(_speak_async(text)),
        daemon=True
    ).start()