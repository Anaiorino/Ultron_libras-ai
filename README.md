🤟 Jarvis Libras IA

Sistema inteligente de tradução e reconhecimento de Libras utilizando Inteligência Artificial, Visão Computacional e Deep Learning em tempo real.

✨ Sobre o Projeto

O Jarvis Libras IA foi desenvolvido com o objetivo de tornar a comunicação mais acessível através da tecnologia.

O sistema utiliza:

câmera em tempo real
reconhecimento de movimentos das mãos
inteligência artificial
tradução de voz para Libras
autenticação de usuários
métricas e monitoramento da API

Tudo integrado em uma aplicação desktop moderna.

🖥️ Preview
Tela inicial
✔ Interface moderna
✔ Tema dark neon
✔ Dashboard interativo
✔ Controle ADMIN/USER
Funcionalidades
🤟 Reconhecimento de Libras em tempo real
🎙️ Voz para Libras
🔐 Sistema de Login e Cadastro
📊 Métricas da API
🧠 IA treinada com Deep Learning
👤 Controle de acesso por usuário
🛡️ Segurança com JWT
📂 Backend modularizado
✅ Testes automatizados
🧠 Tecnologias Utilizadas
Backend
Python
FastAPI
SQLAlchemy
SQLite
JWT Authentication
Passlib
Inteligência Artificial
TensorFlow
Keras
MediaPipe
OpenCV
NumPy
Frontend Desktop
CustomTkinter
PIL/Pillow
Testes
Pytest
🏗️ Arquitetura do Projeto
jarvis-libras/
│
├── app/
│   ├── main_app.py
│   └── voice.py
│
├── backend/
│   ├── routes/
│   ├── middlewares/
│   ├── tests/
│   ├── models.py
│   ├── schemas.py
│   └── main.py
│
├── models/
│   ├── libras_model.h5
│   └── actions.npy
│
├── assets/
│
├── dataset/
│
├── src/
│   ├── train_model.py
│   ├── predict.py
│   └── video_to_dataset.py
│
└── README.md
🤖 Como Funciona a IA

O sistema utiliza:

Câmera → MediaPipe → Extração de Keypoints →
LSTM Neural Network → Predição →
Tradução → Voz/Sinal

A IA identifica os pontos das mãos em tempo real utilizando o MediaPipe, processa os movimentos e envia para uma rede neural LSTM treinada para reconhecer sinais em Libras.

🔐 Segurança

O projeto implementa:

JWT Authentication
Controle ADMIN/USER
Rotas protegidas
Middleware de logs
Trace ID nas requisições
Controle de permissões
Senhas criptografadas
📊 Funcionalidades do ADMIN

Usuários administradores possuem acesso exclusivo a:

métricas da API
monitoramento
estatísticas
logs do sistema
🧪 Testes

O projeto possui testes automatizados utilizando:

pytest

Exemplo:

5 passed
🚀 Como Executar
1. Clone o projeto
git clone https://github.com/SEU_USUARIO/jarvis-libras-ia.git
2. Entre na pasta
cd jarvis-libras-ia
3. Crie o ambiente virtual
Windows
python -m venv venv
venv\Scripts\activate
Linux/Mac
python3 -m venv venv
source venv/bin/activate
4. Instale as dependências
pip install -r requirements.txt
▶️ Rodando o Backend
uvicorn backend.main:app --reload

Backend disponível em:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs
🖥️ Rodando o Frontend
python app/main_app.py
🧠 Treinando a IA
Converter dataset
python src/video_to_dataset.py
Treinar modelo
python src/train_model.py
📸 Reconhecimento em Tempo Real

O sistema:

abre a webcam
detecta as mãos
reconhece os sinais
traduz em tempo real
reproduz áudio automaticamente
🎙️ Voz para Libras

O usuário:

fala no microfone
a voz é convertida em texto
o sistema traduz para Libras
o avatar reproduz os sinais
📈 Melhorias Futuras
Avatar 3D
Tradução contextual
Reconhecimento facial
Deploy web/mobile
Mais sinais
Multi idiomas
Fine tuning da IA
API pública

> ⚠️ This repository is licensed under a Non-Commercial License (CC BY-NC 4.0).
> Commercial use, resale, SaaS distribution, rebranding, or monetization of this project is strictly prohibited without prior authorization from the repository owner.

No Settings > License ou criar manualmente o arquivo LICENSE

Creative Commons Attribution-NonCommercial 4.0 International

Copyright (c) 2026 Anaiorino

This work is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

To view a copy of this license, visit:
https://creativecommons.org/licenses/by-nc/4.0/
