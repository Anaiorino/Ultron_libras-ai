import numpy as np
import os

from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
from tensorflow.keras.callbacks import TensorBoard, EarlyStopping, ModelCheckpoint


# ==========================================
# CONFIGURAÇÕES
# ==========================================

DATA_PATH = "dataset"

SEQUENCE_LENGTH = 30

KEYPOINTS_LENGTH = 126
# ou 246 se estiver usando rosto

# ==========================================
# ACTIONS
# ==========================================

actions = np.array([
    folder for folder in os.listdir(DATA_PATH)
    if os.path.isdir(os.path.join(DATA_PATH, folder))
])

actions = np.sort(actions)

# Mapeia cada sinal (nome da pasta) para um índice numérico
# Ex: {'acontecer': 0, 'aluno': 1, 'amarelo': 2, ...}
label_map = {label: num for num, label in enumerate(actions)}

print("Sinais encontrados:")
print(actions)

print("\nMapeamento de labels (label_map):")
print(label_map)

# ==========================================
# CARREGAR DADOS
# ==========================================

sequences = []
labels = []

print("\nCarregando dataset...\n")

for action in actions:

    action_path = os.path.join(DATA_PATH, action)

    if not os.path.exists(action_path):
        print(f"[AVISO] Pasta não encontrada: {action_path}")
        continue

    valid_sequences = 0

    for sequence in os.listdir(action_path):

        sequence_path = os.path.join(action_path, sequence)

        if not os.path.isdir(sequence_path):
            continue

        window = []

        for frame_num in range(SEQUENCE_LENGTH):

            frame_path = os.path.join(
                sequence_path,
                f"{frame_num}.npy"
            )

            if os.path.exists(frame_path):

                res = np.load(frame_path)

                if res.shape[0] != KEYPOINTS_LENGTH:
                    print(
                        f"[IGNORADO] Shape inválido em {frame_path}: {res.shape}"
                    )
                    continue

                window.append(res)

        if len(window) == SEQUENCE_LENGTH:

            sequences.append(window)

            labels.append(label_map[action])

            valid_sequences += 1

    print(f"{action}: {valid_sequences} sequências válidas")


# ==========================================
# VALIDAR DATASET
# ==========================================

if len(sequences) == 0:
    raise ValueError(
        "\nNenhuma sequência válida foi encontrada.\n"
        "Verifique se você rodou primeiro:\n\n"
        "python src/video_to_dataset.py\n\n"
        "E se a pasta dataset/ tem arquivos .npy dentro.\n"
    )

unique_labels = np.unique(labels)

if len(unique_labels) < 2:
    raise ValueError(
        "\nO dataset tem apenas 1 classe válida.\n"
        "Para treinar um classificador, grave/converta pelo menos 2 sinais.\n"
        "Exemplo: dataset/oi e dataset/sim.\n"
    )


# ==========================================
# PREPARAR DADOS
# ==========================================

X = np.array(sequences, dtype=np.float32)

y = to_categorical(
    labels,
    num_classes=len(actions)
).astype(int)

print("\nFormato X:", X.shape)
print("Formato y:", y.shape)
print("Classes encontradas:", unique_labels)
print("Total de sinais configurados:", len(actions))


# ==========================================
# TREINO / TESTE
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.10,
    random_state=42,
    shuffle=True,
    stratify=labels
)


# ==========================================
# MODELO LSTM
# ==========================================

model = Sequential()

model.add(
    Input(
        shape=(SEQUENCE_LENGTH, KEYPOINTS_LENGTH)
    )
)

model.add(
    LSTM(
        64,
        return_sequences=True,
        activation="tanh"
    )
)

model.add(
    LSTM(
        128,
        return_sequences=True,
        activation="tanh"
    )
)

model.add(
    LSTM(
        64,
        return_sequences=False,
        activation="tanh"
    )
)

model.add(Dense(64, activation="relu"))
model.add(Dropout(0.3))

model.add(Dense(32, activation="relu"))

model.add(
    Dense(
        actions.shape[0],
        activation="softmax"
    )
)


# ==========================================
# COMPILAR
# ==========================================

model.compile(
    optimizer="Adam",
    loss="categorical_crossentropy",
    metrics=["categorical_accuracy"]
)


# ==========================================
# CALLBACKS
# ==========================================

log_dir = os.path.join("Logs")

tb_callback = TensorBoard(
    log_dir=log_dir
)

early_stop = EarlyStopping(
    monitor="val_categorical_accuracy",
    patience=20,
    restore_best_weights=True
)

checkpoint = ModelCheckpoint(
    "models/libras_model.h5",
    monitor="val_categorical_accuracy",
    save_best_only=True,
    mode="max"
)


# ==========================================
# TREINAR
# ==========================================

os.makedirs("models", exist_ok=True)

model.fit(
    X_train,
    y_train,
    epochs=100,
    validation_data=(X_test, y_test),
    callbacks=[
        tb_callback,
        early_stop,
        checkpoint
    ]
)


# ==========================================
# SALVAR MODELO / ACTIONS
# ==========================================

model.save("models/libras_model.h5")

np.save(
    "models/actions.npy",
    actions
)

print("\nModelo treinado e salvo com sucesso.")
print("Modelo salvo em: models/libras_model.h5")
print("Actions salvas em: models/actions.npy")