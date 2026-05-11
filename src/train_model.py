import numpy as np
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import TensorBoard

actions = np.array([
    'oi',
    'sim',
    'nao',
    'e',
    'voce',
    'tudo bem'
])

# CONFIG


DATA_PATH = 'dataset'

SEQUENCE_LENGTH = 30

label_map = {label:num for num, label in enumerate(actions)}

# CARREGAR DADOS

sequences = []
labels = []

for action in actions:

    action_path = os.path.join(DATA_PATH, action)

    if not os.path.exists(action_path):
        continue

    for sequence in os.listdir(action_path):

        window = []

        sequence_path = os.path.join(action_path, sequence)

        for frame_num in range(SEQUENCE_LENGTH):

            frame_path = os.path.join(
                sequence_path,
                f"{frame_num}.npy"
            )

            if os.path.exists(frame_path):

                res = np.load(frame_path)

                window.append(res)

        if len(window) == SEQUENCE_LENGTH:

            sequences.append(window)

            labels.append(label_map[action])

# PREPARAR DADOS

X = np.array(sequences)

y = to_categorical(labels).astype(int)


# TREINO 


X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.05
)


# MODELO LSTM


model = Sequential()

model.add(
    LSTM(
        64,
        return_sequences=True,
        activation='relu',
        input_shape=(30,126)
    )
)

model.add(
    LSTM(
        128,
        return_sequences=True,
        activation='relu'
    )
)

model.add(
    LSTM(
        64,
        return_sequences=False,
        activation='relu'
    )
)

model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))

model.add(Dense(actions.shape[0], activation='softmax'))


# COMPILAR


model.compile(
    optimizer='Adam',
    loss='categorical_crossentropy',
    metrics=['categorical_accuracy']
)


# LOGS


log_dir = os.path.join('Logs')

tb_callback = TensorBoard(log_dir=log_dir)


# TREINAR


model.fit(
    X_train,
    y_train,
    epochs=100,
    callbacks=[tb_callback]
)


# SALVAR MODELO


os.makedirs("models", exist_ok=True)

model.save('models/libras_model.h5')

print("\nModelo treinado e salvo com sucesso 😎")
