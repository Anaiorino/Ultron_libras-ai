import cv2
import mediapipe as mp
import numpy as np
import os
import time


# CONFIG


SIGN_NAME = "voce"

SEQUENCE_LENGTH = 30

TOTAL_SEQUENCES = 30

DATA_PATH = os.path.join("dataset", SIGN_NAME)





for sequence in range(TOTAL_SEQUENCES):

    os.makedirs(
        os.path.join(DATA_PATH, str(sequence)),
        exist_ok=True
    )


# MEDIAPIPE


mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils


# Cam


camera = cv2.VideoCapture(0)


# EXTRAIR LANDMARKS


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

    return np.array(keypoints)


# COLETAR DATASET


for sequence in range(TOTAL_SEQUENCES):

    print(f"\nGravando sequência {sequence}")

    time.sleep(2)

    for frame_num in range(SEQUENCE_LENGTH):

        success, frame = camera.read()

        if not success:
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
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0,255,0),
            2
        )

        cv2.putText(
            frame,
            f'Seq: {sequence} Frame: {frame_num}',
            (10, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            2
        )

        # Mostrar
        cv2.imshow("Coletor Dataset", frame)

        # ESC fecha
        if cv2.waitKey(1) == 27:
            break



camera.release()
cv2.destroyAllWindows()
