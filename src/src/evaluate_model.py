import numpy as np
import os
from tensorflow.keras.models import load_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

DATA_PATH = "dataset"
SEQUENCE_LENGTH = 30

model = load_model("models/libras_model.h5")
actions = np.load("models/actions.npy", allow_pickle=True)

label_map = {label: num for num, label in enumerate(actions)}

sequences = []
labels = []

print("\nCarregando dataset para avaliação...")

for action in actions:
    action_path = os.path.join(DATA_PATH, action)

    if not os.path.exists(action_path):
        continue

    for sequence in os.listdir(action_path):
        sequence_path = os.path.join(action_path, sequence)

        if not os.path.isdir(sequence_path):
            continue

        window = []

        for frame_num in range(SEQUENCE_LENGTH):
            frame_path = os.path.join(sequence_path, f"{frame_num}.npy")

            if os.path.exists(frame_path):
                res = np.load(frame_path)
                window.append(res)

        if len(window) == SEQUENCE_LENGTH:
            sequences.append(window)
            labels.append(label_map[action])

X = np.array(sequences, dtype=np.float32)
y = np.array(labels)

_, X_test, _, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    shuffle=True
)

predictions = model.predict(X_test)

y_pred = np.argmax(predictions, axis=1)

accuracy = np.mean(y_pred == y_test)

print("\nAcuracidade geral:")
print(f"{accuracy * 100:.2f}%")

print("\nRelatório por sinal:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=actions,
        zero_division=0
    )
)

print("\nMatriz de confusão:")
print(confusion_matrix(y_test, y_pred))