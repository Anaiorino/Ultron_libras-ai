import cv2
import mediapipe as mp
import numpy as np
import os
import shutil

VIDEOS_PATH = "dataset_videos"
DATASET_PATH = "dataset"
SEQUENCE_LENGTH = 30

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils


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


def get_frame_indexes(total_frames, sequence_length):
    if total_frames <= 0:
        return []

    return np.linspace(
        0,
        total_frames - 1,
        sequence_length,
        dtype=int
    )


def process_video(video_path, output_folder):
    cap = cv2.VideoCapture(video_path)

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_indexes = get_frame_indexes(total_frames, SEQUENCE_LENGTH)

    sequence_data = []
    current_frame = 0
    selected_position = 0

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break

        if selected_position < len(frame_indexes) and current_frame == frame_indexes[selected_position]:
            frame = cv2.flip(frame, 1)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            keypoints = extract_keypoints(results)
            sequence_data.append(keypoints)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS
                    )

            cv2.imshow("Convertendo Videos para Dataset", frame)
            selected_position += 1

        current_frame += 1

        if cv2.waitKey(1) == 27:
            break

    cap.release()

    if len(sequence_data) == SEQUENCE_LENGTH:
        os.makedirs(output_folder, exist_ok=True)

        for frame_num, keypoints in enumerate(sequence_data):
            np.save(
                os.path.join(output_folder, str(frame_num)),
                keypoints
            )

        return True

    return False


def main():
    if not os.path.exists(VIDEOS_PATH):
        print("Pasta dataset_videos não encontrada.")
        return

    os.makedirs(DATASET_PATH, exist_ok=True)

    signs = [
        sign for sign in os.listdir(VIDEOS_PATH)
        if os.path.isdir(os.path.join(VIDEOS_PATH, sign))
    ]

    for sign in signs:
        sign_path = os.path.join(VIDEOS_PATH, sign)
        dataset_sign_path = os.path.join(DATASET_PATH, sign)

        os.makedirs(dataset_sign_path, exist_ok=True)

        existing_sequences = [
            folder for folder in os.listdir(dataset_sign_path)
            if os.path.isdir(os.path.join(dataset_sign_path, folder))
        ]

        sequence_counter = len(existing_sequences)

        videos = [
            video for video in os.listdir(sign_path)
            if video.lower().endswith((".mp4", ".avi", ".mov", ".mkv"))
        ]

        print(f"\nProcessando sinal: {sign}")
        print(f"Vídeos encontrados: {len(videos)}")

        for video in videos:
            video_path = os.path.join(sign_path, video)

            output_folder = os.path.join(
                dataset_sign_path,
                str(sequence_counter)
            )

            print(f"Convertendo: {video}")

            success = process_video(video_path, output_folder)

            if success:
                print(f"Salvo em: {output_folder}")
                sequence_counter += 1
            else:
                print(f"Falha ao processar: {video}")

    cv2.destroyAllWindows()
    print("\nConversão finalizada.")


if __name__ == "__main__":
    main()