import cv2
import mediapipe as mp
import numpy as np
import os
import time


# ==========================================
# CONFIGURAÇÕES
# ==========================================

SIGN_NAME = "tudo_bem"

SEQUENCE_LENGTH = 30

TOTAL_SEQUENCES = 50

DATA_PATH = os.path.join("dataset", SIGN_NAME)

CAMERA_INDEX = 0

CAPTURE_WIDTH = 1280
CAPTURE_HEIGHT = 720

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600


# ==========================================
# CRIAR PASTAS
# ==========================================

for sequence in range(TOTAL_SEQUENCES):
    os.makedirs(
        os.path.join(DATA_PATH, str(sequence)),
        exist_ok=True
    )


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

camera = cv2.VideoCapture(CAMERA_INDEX)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

cv2.namedWindow(
    "Coletor Dataset",
    cv2.WINDOW_NORMAL
)

cv2.resizeWindow(
    "Coletor Dataset",
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)


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

    # duas mãos = 42 pontos = 126 valores
    while len(keypoints) < 126:
        keypoints.append(0)

    return np.array(keypoints[:126], dtype=np.float32)


# ==========================================
# COLETAR DATASET
# ==========================================

stop_collection = False

for sequence in range(TOTAL_SEQUENCES):

    if stop_collection:
        break

    print(f"\nPreparando sequência {sequence}")

    # Contagem antes de gravar
    for countdown in range(2, 0, -1):
        success, frame = camera.read()

        if not success:
            stop_collection = True
            break

        frame = cv2.flip(frame, 1)

        cv2.putText(
            frame,
            f'Prepare o sinal: {SIGN_NAME}',
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f'Comecando em {countdown}...',
            (30, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2
        )

        frame_small = cv2.resize(
            frame,
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        cv2.imshow("Coletor Dataset", frame_small)

        key = cv2.waitKey(1000)

        if key == 27 or key == ord("q"):
            stop_collection = True
            break

    if stop_collection:
        break

    print(f"Gravando sequência {sequence}")

    for frame_num in range(SEQUENCE_LENGTH):

        success, frame = camera.read()

        if not success:
            stop_collection = True
            break

        # Espelhar
        frame = cv2.flip(frame, 1)

        # RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Processar mãos
        results = hands.process(rgb_frame)

        # Desenhar mãos
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

        # Extrair keypoints
        keypoints = extract_keypoints(results)

        # Salvar frame
        npy_path = os.path.join(
            DATA_PATH,
            str(sequence),
            str(frame_num)
        )

        np.save(npy_path, keypoints)

        # Texto tela
        cv2.putText(
            frame,
            f'Coletando: {SIGN_NAME}',
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f'Sequencia: {sequence + 1}/{TOTAL_SEQUENCES}',
            (30, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f'Frame: {frame_num + 1}/{SEQUENCE_LENGTH}',
            (30, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            'ESC ou Q para sair',
            (30, CAPTURE_HEIGHT - 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2
        )

        # Reduzir janela
        frame_small = cv2.resize(
            frame,
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        # Mostrar
        cv2.imshow("Coletor Dataset", frame_small)

        key = cv2.waitKey(1)

        if key == 27 or key == ord("q"):
            stop_collection = True
            break


# ==========================================
# FINALIZAR
# ==========================================

camera.release()
cv2.destroyAllWindows()

print("\nColeta finalizada.")