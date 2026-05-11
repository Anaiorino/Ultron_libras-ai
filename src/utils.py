import cv2
import mediapipe as mp
import time
from collections import deque

# CONFIG MEDIAPIPE

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# ABRIR Cam

camera = cv2.VideoCapture(0)

texto = ""

ultimo_gesto = ""
ultimo_tempo = time.time()

DELAY_GESTO = 2

# Histórico de movimentos
movement_history = deque(maxlen=15)

# Controle mãos
left_hand_detected = False
right_hand_detected = False

# DETECTAR DEDOS

finger_tips = [8, 12, 16, 20]

def detect_fingers(landmarks):

    fingers = []
    
    # POLEGAR

    thumb_tip = landmarks[4].x
    thumb_base = landmarks[3].x

    if thumb_tip < thumb_base:
        fingers.append(1)
    else:
        fingers.append(0)

    # OUTROS DEDOS

    for tip in finger_tips:

        tip_y = landmarks[tip].y
        base_y = landmarks[tip - 2].y

        if tip_y < base_y:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers


# LOOP PRINCIPAL


while True:

    success, frame = camera.read()

    if not success:
        break

    # Espelhar imagem
    frame = cv2.flip(frame, 1)

    # Converter RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Processar mãos
    results = hands.process(rgb_frame)

    gesto = "..."

    # Reset mãos
    left_hand_detected = False
    right_hand_detected = False

    # DETECTOU MÃOS?

    if results.multi_hand_landmarks and results.multi_handedness:

        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):

            # Desenhar mão
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # IDENTIFICAR MÃO
            
            hand_label = results.multi_handedness[idx].classification[0].label

            if hand_label == "Left":
                left_hand_detected = True

            elif hand_label == "Right":
                right_hand_detected = True

            landmarks = hand_landmarks.landmark


            # DETECTAR DEDOS

            fingers = detect_fingers(landmarks)

            # CENTRO DA PALMA
    

            palm = landmarks[0]

            current_x = palm.x
            current_y = palm.y

            # Guardar histórico movimento
            movement_history.append((current_x, current_y))

            # RECONHECIMENTO DE LIBRAS

            # OI
            # Palma aberta + movimento direita

            if fingers == [1, 1, 1, 1, 1]:

                if len(movement_history) >= 10:

                    start_x = movement_history[0][0]
                    end_x = movement_history[-1][0]

                    movement_x = end_x - start_x

                    if movement_x > 0.10:
                        gesto = "OI"


            # TCHAU
            # Palma aberta + movimento esquerda
  

            if fingers == [1, 1, 1, 1, 1]:

                if len(movement_history) >= 10:

                    start_x = movement_history[0][0]
                    end_x = movement_history[-1][0]

                    movement_x = end_x - start_x

                    if movement_x < -0.10:
                        gesto = "TCHAU"


            # SIM
            # Punho fechado movendo cima/baixo
      

            if fingers == [0, 0, 0, 0, 0]:

                if len(movement_history) >= 10:

                    start_y = movement_history[0][1]
                    end_y = movement_history[-1][1]

                    movement_y = end_y - start_y

                    if abs(movement_y) > 0.08:
                        gesto = "SIM"

 
            # NÃO
            # Indicador levantado mexendo lateralmente
          

            if fingers == [0, 1, 0, 0, 0]:

                if len(movement_history) >= 10:

                    start_x = movement_history[0][0]
                    end_x = movement_history[-1][0]

                    movement_x = end_x - start_x

                    if abs(movement_x) > 0.08:
                        gesto = "NAO"

            # AJUDA
            # Duas mãos abertas
       

            if left_hand_detected and right_hand_detected:

                gesto = "AJUDA"

    

            tempo_atual = time.time()

            if (
                gesto != "..."
                and gesto != ultimo_gesto
                and tempo_atual - ultimo_tempo > DELAY_GESTO
            ):

                texto += gesto + " "

                ultimo_gesto = gesto
                ultimo_tempo = tempo_atual

    # MOSTRAR GESTO
  

    cv2.putText(
        frame,
        f'Gesto: {gesto}',
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0),
        3
    )

    # MOSTRAR TEXTO
 

    cv2.putText(
        frame,
        f'Texto: {texto}',
        (10, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    # MOSTRAR QUANTIDADE MÃOS


    total_hands = 0

    if left_hand_detected:
        total_hands += 1

    if right_hand_detected:
        total_hands += 1

    cv2.putText(
        frame,
        f'Maos: {total_hands}',
        (10, 170),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )

  
    # EXIBIR Cam


    cv2.imshow("Jarvis Libras", frame)

    # TECLAS
 

    key = cv2.waitKey(1)

    # ESC fecha
    if key == 27:
        break

    # BACKSPACE limpa texto
    elif key == 8:
        texto = ""


camera.release()
cv2.destroyAllWindows()
