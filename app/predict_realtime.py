import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from tensorflow.keras.models import load_model
from voice import speak
import time

# ==========================================
# CARREGAR MODELO
# ==========================================

model = load_model("models/libras_model.h5")

actions = np.load("models/actions.npy", allow_pickle=True)

# ==========================================
# MEDIAPIPE
# ==========================================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# ==========================================
# CÂMERA
# ==========================================

camera = cv2.VideoCapture(0)

# ==========================================
# CONFIGURAÇÕES
# ==========================================

SEQUENCE_LENGTH = 30
sequence = deque(maxlen=SEQUENCE_LENGTH)

last_prediction = ""
last_added_time = 0
last_spoken_word = ""

PREDICTION_DELAY = 3

recognized_word = "..."
confidence = 0.0

frame_counter = 0
PREDICT_EVERY = 5

CONFIDENCE_THRESHOLD = 0.90

candidate_word = ""
candidate_count = 0
CONFIRMATION_FRAMES = 5

# ==========================================
# EXTRAIR LANDMARKS
# ==========================================

def extract_keypoints(results):
    keypoints = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for landmark in hand_landmarks.landmark:
                keypoints.extend([
                    landmark.x,
                    landmark.y,
                    landmark.z
                ])

    while len(keypoints) < 126:
        keypoints.append(0)

    return np.array(keypoints[:126], dtype=np.float32)

# ==========================================
# INTERFACE COM PAINEL LATERAL
# ==========================================

def draw_panel(frame, recognized_word, confidence, candidate_word, candidate_count):
    cam_h, cam_w, _ = frame.shape

    panel_w = 360
    total_w = cam_w + panel_w
    total_h = cam_h

    black = (8, 8, 12)
    dark = (18, 18, 24)
    baby_pink = (203, 182, 255)
    white_soft = (235, 235, 240)
    gray = (90, 90, 100)

    layout = np.zeros((total_h, total_w, 3), dtype=np.uint8)
    layout[:] = black

    layout[0:cam_h, 0:cam_w] = frame

    x0 = cam_w

    cv2.rectangle(layout, (x0, 0), (total_w, total_h), dark, -1)
    cv2.line(layout, (x0, 0), (x0, total_h), baby_pink, 2)

    cv2.putText(
        layout,
        "JARVIS",
        (x0 + 35, 55),
        cv2.FONT_HERSHEY_DUPLEX,
        1.2,
        baby_pink,
        3
    )

    cv2.putText(
        layout,
        "LIBRAS IA",
        (x0 + 35, 95),
        cv2.FONT_HERSHEY_DUPLEX,
        0.9,
        white_soft,
        2
    )

    cv2.rectangle(
        layout,
        (x0 + 25, 135),
        (total_w - 25, 235),
        black,
        -1
    )

    cv2.rectangle(
        layout,
        (x0 + 25, 135),
        (total_w - 25, 235),
        baby_pink,
        2
    )

    cv2.putText(
        layout,
        "PALAVRA",
        (x0 + 45, 170),
        cv2.FONT_HERSHEY_DUPLEX,
        0.65,
        gray,
        2
    )

    cv2.putText(
        layout,
        recognized_word.upper(),
        (x0 + 45, 215),
        cv2.FONT_HERSHEY_DUPLEX,
        1.0,
        baby_pink,
        2
    )

    cv2.rectangle(
        layout,
        (x0 + 25, 265),
        (total_w - 25, 365),
        black,
        -1
    )

    cv2.rectangle(
        layout,
        (x0 + 25, 265),
        (total_w - 25, 365),
        baby_pink,
        2
    )

    cv2.putText(
        layout,
        f"CONFIANCA: {confidence:.2f}",
        (x0 + 45, 305),
        cv2.FONT_HERSHEY_DUPLEX,
        0.7,
        white_soft,
        2
    )

    bar_x = x0 + 45
    bar_y = 325
    bar_w = panel_w - 90
    bar_h = 22

    cv2.rectangle(
        layout,
        (bar_x, bar_y),
        (bar_x + bar_w, bar_y + bar_h),
        gray,
        -1
    )

    filled = int(bar_w * confidence)

    cv2.rectangle(
        layout,
        (bar_x, bar_y),
        (bar_x + filled, bar_y + bar_h),
        baby_pink,
        -1
    )

    cv2.rectangle(
        layout,
        (bar_x, bar_y),
        (bar_x + bar_w, bar_y + bar_h),
        baby_pink,
        2
    )

    cv2.rectangle(
        layout,
        (x0 + 25, 395),
        (total_w - 25, 495),
        black,
        -1
    )

    cv2.rectangle(
        layout,
        (x0 + 25, 395),
        (total_w - 25, 495),
        baby_pink,
        2
    )

    cv2.putText(
        layout,
        "CONFIRMACAO",
        (x0 + 45, 430),
        cv2.FONT_HERSHEY_DUPLEX,
        0.65,
        gray,
        2
    )

    cv2.putText(
        layout,
        candidate_word.upper(),
        (x0 + 45, 465),
        cv2.FONT_HERSHEY_DUPLEX,
        0.75,
        white_soft,
        2
    )

    cv2.putText(
        layout,
        f"{candidate_count}/{CONFIRMATION_FRAMES}",
        (total_w - 120, 465),
        cv2.FONT_HERSHEY_DUPLEX,
        0.75,
        baby_pink,
        2
    )

    cv2.putText(
        layout,
        "ESC  sair",
        (x0 + 35, total_h - 65),
        cv2.FONT_HERSHEY_DUPLEX,
        0.6,
        white_soft,
        2
    )

    cv2.putText(
        layout,
        "BACKSPACE  resetar",
        (x0 + 35, total_h - 35),
        cv2.FONT_HERSHEY_DUPLEX,
        0.6,
        baby_pink,
        2
    )

    return layout

# ==========================================
# LOOP PRINCIPAL
# ==========================================

while True:
    success, frame = camera.read()

    if not success:
        break

    frame_counter += 1

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

    keypoints = extract_keypoints(results)
    sequence.append(keypoints)

    if len(sequence) == SEQUENCE_LENGTH and frame_counter % PREDICT_EVERY == 0:
        input_data = np.array(sequence, dtype=np.float32)

        prediction = model.predict(
            np.expand_dims(input_data, axis=0),
            verbose=0
        )[0]

        predicted_index = np.argmax(prediction)
        predicted_action = actions[predicted_index]
        confidence = float(prediction[predicted_index])

        current_time = time.time()

        if confidence > CONFIDENCE_THRESHOLD:

            if predicted_action == "neutro":
                recognized_word = "..."
                candidate_word = ""
                candidate_count = 0
                last_prediction = "neutro"
                last_spoken_word = ""

            else:
                if predicted_action == candidate_word:
                    candidate_count += 1
                else:
                    candidate_word = predicted_action
                    candidate_count = 1

                if candidate_count >= CONFIRMATION_FRAMES:
                    recognized_word = predicted_action

                    if (
                        predicted_action != last_prediction
                        or current_time - last_added_time > PREDICTION_DELAY
                    ):
                        if predicted_action != last_spoken_word:
                            speak(predicted_action.replace("_", " "))
                            last_spoken_word = predicted_action

                        last_prediction = predicted_action
                        last_added_time = current_time

        else:
            candidate_word = ""
            candidate_count = 0

    frame = draw_panel(
        frame,
        recognized_word,
        confidence,
        candidate_word,
        candidate_count
    )

    cv2.imshow("Jarvis Libras IA", frame)

    key = cv2.waitKey(1)

    if key == 27:
        break

    elif key == 8:
        last_prediction = ""
        last_spoken_word = ""
        recognized_word = "..."
        confidence = 0.0
        candidate_word = ""
        candidate_count = 0
        sequence.clear()
        frame_counter = 0

camera.release()
cv2.destroyAllWindows()