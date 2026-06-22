# Jarvis Libras AI

Sistema inteligente para **tradução e apoio ao aprendizado de Libras**, combinando **visão computacional**, **inteligência artificial**, **interface desktop** e **API backend**.
O projeto foi desenvolvido com foco em acessibilidade, organização em camadas, autenticação segura, testes automatizados e boas práticas de entrega acadêmica.

---

# Sumário

* [1. Visão Geral](#1-visão-geral)
* [2. Objetivo do Projeto](#2-objetivo-do-projeto)
* [3. Problema que o Projeto Resolve](#3-problema-que-o-projeto-resolve)
* [4. Funcionalidades Implementadas](#4-funcionalidades-implementadas)
* [5. Tecnologias Utilizadas](#5-tecnologias-utilizadas)
* [6. Arquitetura do Projeto](#6-arquitetura-do-projeto)
* [7. Estrutura de Pastas](#7-estrutura-de-pastas)
* [8. Backend da Aplicação](#8-backend-da-aplicação)
* [9. IA / Visão Computacional](#9-ia--visão-computacional)
* [10. Interface Desktop](#10-interface-desktop)
* [11. Banco de Dados](#11-banco-de-dados)
* [12. Segurança e Autenticação](#12-segurança-e-autenticação)
* [13. Testes Automatizados](#13-testes-automatizados)
* [14. Dockerização](#14-dockerização)
* [15. Como Executar o Projeto](#15-como-executar-o-projeto)
* [16. Endpoints da API](#16-endpoints-da-api)
* [17. Documentação Swagger](#17-documentação-swagger)
* [18. Status Atual do Projeto](#18-status-atual-do-projeto)
* [19. Melhorias Futuras](#19-melhorias-futuras)
* [20. Evidências para Rubrica / Entrega](#20-evidências-para-rubrica--entrega)
* [21. Autora](#21-autora)

---

# 1. Visão Geral

O **Jarvis Libras AI** é um sistema voltado para **tradução e apoio à comunicação em Libras**, integrando:

* **captura de sinais pela câmera**;
* **extração de pontos do corpo/mãos com MediaPipe**;
* **treinamento de modelo de IA para reconhecimento de sinais**;
* **interface desktop em Python**;
* **backend em FastAPI** com autenticação, histórico e gerenciamento de sinais;
* **testes automatizados** e **dockerização**.

A proposta do projeto é servir como base para um **assistente multimodal acessível**, capaz de reconhecer sinais em Libras e oferecer recursos de apoio à comunicação e aprendizado.

---

# 2. Objetivo do Projeto

Desenvolver uma aplicação capaz de **reconhecer sinais em Libras** a partir de vídeos ou captura em tempo real, oferecendo:

* **tradução / interpretação de sinais**;
* **cadastro e organização de sinais**;
* **histórico de traduções**;
* **estrutura backend segura e testável**;
* **base para evolução futura para assistente inteligente multimodal**.

---

# 3. Problema que o Projeto Resolve

A comunicação entre pessoas surdas e ouvintes ainda enfrenta barreiras importantes no cotidiano.
Além disso, soluções de acessibilidade com Libras nem sempre estão disponíveis em sistemas acadêmicos, aplicações locais ou projetos personalizados.

Este projeto busca contribuir com esse cenário ao propor uma solução que:

* apoia a **interpretação de sinais**;
* organiza uma **base de sinais**;
* registra **histórico de uso**;
* permite futura expansão para **tradução em tempo real** e **assistente virtual acessível**.

---

# 4. Funcionalidades Implementadas

## Funcionalidades já implementadas

* Captura de vídeos/sinais para formação de dataset
* Conversão de vídeos em dataset estruturado
* Pipeline de treinamento do modelo de classificação
* Interface desktop com Python / CustomTkinter
* Backend em **FastAPI**
* CRUD de sinais (`/signs`)
* Cadastro e login de usuários (`/auth`)
* Autenticação com **JWT**
* Controle de acesso por usuário e administrador
* Histórico de traduções (`/history`)
* Endpoint de saúde da API (`/health`)
* Testes automatizados com **Pytest**
* Dockerização do backend
* Documentação automática via **Swagger**

## Funcionalidades previstas / em evolução

* Tradução em tempo real integrada ao modelo treinado
* Dashboard com métricas de uso
* Upload e gestão de vídeos pela API
* Deploy em nuvem
* Integração completa entre interface desktop e backend
* Expansão do conjunto de sinais em Libras

---

# 5. Tecnologias Utilizadas

## Linguagens

* **Python**

## Backend / API

* **FastAPI**
* **Uvicorn**
* **SQLAlchemy**
* **Pydantic**
* **Python-Jose (JWT)**
* **python-dotenv**

## Banco de dados

* **SQLite**

## Testes

* **Pytest**
* **FastAPI TestClient**

## IA / Visão Computacional

* **TensorFlow / Keras**
* **NumPy**
* **OpenCV**
* **MediaPipe**
* **scikit-learn**

## Interface

* **CustomTkinter**
* **Tkinter**
* **Pillow**
* **Matplotlib**

## Infraestrutura / DevOps

* **Docker**
* **Git**
* **GitHub**

---

# 6. Arquitetura do Projeto

O projeto foi organizado em **módulos independentes**, separando:

1. **Interface Desktop**

   * captura de vídeo
   * interação com usuário
   * visualização de tradução e histórico

2. **Pipeline de IA**

   * coleta de vídeos
   * conversão para dataset
   * treinamento do modelo
   * carregamento do modelo para inferência

3. **Backend FastAPI**

   * autenticação de usuários
   * gerenciamento de sinais
   * histórico de traduções
   * documentação da API
   * testes automatizados

Essa separação facilita:

* manutenção;
* testes;
* evolução do projeto;
* futura integração com frontend web/mobile.

---

# 7. Estrutura de Pastas

A estrutura do projeto está organizada da seguinte forma:

```bash
jarvis-libras/
├── app/                         # interface / aplicação principal (quando aplicável)
├── assets/                      # imagens, ícones e recursos visuais
├── backend/                     # API FastAPI
│   ├── middlewares/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── health.py
│   │   ├── history.py
│   │   └── signs.py
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_health.py
│   │   ├── test_history.py
│   │   └── test_signs.py
│   ├── __init__.py
│   ├── create_admin.py
│   ├── database.py
│   ├── Dockerfile
│   ├── main.py
│   ├── metrics.py
│   ├── models.py
│   ├── requirements.txt
│   ├── schemas.py
│   └── security.py
│
├── dataset/                     # dataset já convertido em .npy
├── dataset_videos/              # vídeos brutos por sinal
├── docs/                        # documentos, relatórios e evidências
├── Logs/                        # logs de treinamento / TensorBoard
├── models/                      # modelo treinado e actions.npy
├── relatorios/                  # relatórios do projeto
├── src/                         # scripts de coleta, conversão, treino etc.
│   ├── collect_data.py
│   ├── video_to_dataset.py
│   ├── train_model.py
│   └── ...
├── README.md
└── requirements.txt
```

> Observação: alguns nomes de arquivos podem variar de acordo com a evolução do projeto, mas a estrutura geral segue a organização acima.

---

# 8. Backend da Aplicação

O backend foi desenvolvido com **FastAPI** e tem como objetivo fornecer uma camada de serviços para o sistema, incluindo:

* autenticação de usuários;
* cadastro e gerenciamento de sinais;
* histórico de traduções;
* endpoint de monitoramento da API.

## Principais recursos do backend

* arquitetura modular com rotas separadas;
* uso de **Pydantic** para validação;
* persistência com **SQLAlchemy + SQLite**;
* autenticação via **JWT**;
* testes automatizados com **Pytest**;
* documentação automática via **Swagger**;
* execução local ou em **Docker**.

---

# 9. IA / Visão Computacional

A parte de inteligência artificial do projeto utiliza **MediaPipe + TensorFlow/Keras**.

## Pipeline geral

### 1. Coleta de vídeos

Os sinais são gravados e organizados em pastas por classe dentro de `dataset_videos/`.

### 2. Conversão para dataset

Os vídeos são processados para extração de keypoints (pontos do corpo/mãos/rosto, dependendo da configuração), gerando arquivos `.npy` organizados em `dataset/`.

### 3. Treinamento

O script `train_model.py` carrega as sequências, prepara os dados e treina uma rede **LSTM** para classificação temporal dos sinais.

### 4. Inferência

O modelo treinado é salvo na pasta `models/` e pode ser carregado pela aplicação desktop para reconhecimento.

## Situação atual da IA

Até o momento, o projeto já passou pelas etapas de:

* definição de classes/sinais;
* organização do dataset de vídeos;
* conversão para dataset processado;
* treinamento do modelo inicial.

---

# 10. Interface Desktop

A interface desktop foi construída em **Python com CustomTkinter**, com o objetivo de servir como ambiente de interação com o usuário.

## Possíveis recursos da interface

* iniciar câmera
* visualizar detecção / reconhecimento
* exibir texto traduzido
* consultar histórico
* interagir com voz (quando aplicável)
* servir como “assistente Jarvis” futuramente

---

# 11. Banco de Dados

O projeto utiliza **SQLite** para persistência local dos dados do backend.

## Tabelas principais

### `users`

Armazena usuários cadastrados:

* id
* name
* email
* password
* role
* created_at

### `signs`

Armazena os sinais cadastrados:

* id
* name
* description
* video_path
* created_at

### `translation_history`

Armazena o histórico de traduções:

* id
* user_id
* input_text
* output_text
* translation_type
* confidence
* created_at

---

# 12. Segurança e Autenticação

A autenticação da API foi implementada com **JWT (JSON Web Token)**.

## Fluxo de autenticação

1. O usuário se registra em `/auth/register`
2. O usuário faz login em `/auth/login`
3. A API retorna um `access_token`
4. O token é enviado no header:

   ```http
   Authorization: Bearer SEU_TOKEN
   ```
5. Rotas protegidas validam o token antes de permitir acesso

## Regras implementadas

* usuários autenticados podem acessar rotas protegidas
* algumas ações podem ser limitadas por perfil (`USER` / `ADMIN`)
* o histórico é protegido por usuário
* o backend usa variáveis de ambiente para chave secreta e tempo de expiração

---

# 13. Testes Automatizados

Foram implementados testes automatizados com **Pytest** para validar o comportamento do backend.

## Cobertura atual

* autenticação (`/auth`)
* health check (`/health`)
* CRUD de sinais (`/signs`)
* histórico de traduções (`/history`)

## Benefícios dos testes

* validar comportamento esperado das rotas
* reduzir regressões
* facilitar manutenção
* demonstrar qualidade técnica do projeto

## Executar os testes

Na raiz do projeto:

```bash
pytest backend/tests -v
```

Ou, dentro da pasta `backend/`:

```bash
pytest tests -v
```

---

# 14. Dockerização

O backend foi dockerizado para facilitar a execução em diferentes ambientes e padronizar a entrega.

## Benefícios

* simplifica execução da API
* evita problemas de dependências locais
* melhora reprodutibilidade
* aproxima o projeto de um cenário real de deploy

## Build da imagem

Na raiz do projeto:

```bash
docker build -t jarvis-backend ./backend
```

## Rodar o container

```bash
docker run -p 8000:8000 jarvis-backend
```

---

# 15. Como Executar o Projeto

## 15.1. Pré-requisitos

Antes de começar, tenha instalado:

* Python 3.10+ (ou compatível com o ambiente do projeto)
* pip
* Git
* Docker (opcional, para executar container)
* ambiente virtual Python recomendado

---

## 15.2. Clonar o repositório

```bash
git clone https://github.com/Anaiorino/Ultron_libras-ai.git
cd jarvis-libras
```

---

## 15.3. Criar e ativar ambiente virtual

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

---

## 15.4. Instalar dependências do projeto

Na raiz:

```bash
pip install -r requirements.txt
```

Se quiser rodar só o backend, também pode instalar as dependências da pasta `backend`:

```bash
pip install -r backend/requirements.txt
```

---

## 15.5. Configurar variáveis de ambiente

Crie um arquivo `.env` dentro da pasta `backend/` com o conteúdo:

```env
SECRET_KEY=jarvis_libras_2026_super_secreta
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=60
ADMIN_EMAIL=admin@jarvis.com
```

---

## 15.6. Rodar o backend

Na **raiz do projeto** (`jarvis-libras`):

```bash
uvicorn backend.main:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

---

## 15.7. Acessar a documentação Swagger

Depois de subir o backend, abra no navegador:

```text
http://127.0.0.1:8000/docs
```

---

## 15.8. Rodar os testes

Na raiz do projeto:

```bash
pytest backend/tests -v
```

---

## 15.9. Rodar com Docker

Build:

```bash
docker build -t jarvis-backend ./backend
```

Run:

```bash
docker run -p 8000:8000 jarvis-backend
```

---

# 16. Endpoints da API

## Auth

### `POST /auth/register`

Cria um novo usuário.

### `POST /auth/login`

Realiza login e retorna JWT.

---

## Signs

### `POST /signs/`

Cria um novo sinal.

### `GET /signs/`

Lista todos os sinais.

### `GET /signs/{sign_id}`

Busca um sinal pelo ID.

### `PUT /signs/{sign_id}`

Atualiza um sinal existente.

### `DELETE /signs/{sign_id}`

Remove um sinal.

---

## History

### `POST /history/`

Salva um item no histórico de tradução.

### `GET /history/`

Lista histórico do usuário autenticado (ou geral, dependendo da regra de acesso).

### `DELETE /history/{history_id}`

Remove um item do histórico.

---

## Health

### `GET /health`

Retorna o status da API.

---

# 17. Documentação Swagger

A documentação da API é gerada automaticamente pelo FastAPI.

## Acesso

```text
http://127.0.0.1:8000/docs
```

## O que pode ser testado no Swagger

* cadastro de usuário
* login
* autenticação com token
* CRUD de sinais
* histórico de traduções
* health check

## Fluxo recomendado de teste no Swagger

1. usar `POST /auth/register`
2. usar `POST /auth/login`
3. copiar o `access_token`
4. clicar em **Authorize**
5. informar:

   ```text
   Bearer SEU_TOKEN
   ```
6. testar as rotas protegidas

---

# 18. Status Atual do Projeto

## Etapas concluídas até o momento

* estrutura inicial do projeto definida
* organização do dataset de vídeos
* conversão de vídeos para dataset
* pipeline de treinamento implementado
* backend em FastAPI criado
* autenticação JWT implementada
* CRUD de sinais implementado
* histórico de traduções implementado
* endpoint de health criado
* testes automatizados criados
* backend dockerizado
* README e documentação em construção

## Etapas em andamento / próximas

* integração completa do modelo de Libras à interface
* refinamento da inferência em tempo real
* dashboard / métricas
* deploy
* ampliação do dataset e melhoria de acurácia

---

# 19. Melhorias Futuras

As próximas evoluções planejadas para o projeto incluem:

* integração completa da IA com a API e a interface desktop
* tradução de Libras em tempo real pela câmera
* expansão do número de sinais reconhecidos
* cadastro e upload de vídeos de sinais pela API
* dashboard com métricas de uso
* controle de permissões mais robusto
* persistência mais robusta com PostgreSQL
* deploy do backend em nuvem
* criação de frontend web ou app mobile
* evolução do Jarvis para assistente multimodal com voz, câmera e IA

---

# 20. Evidências para Rubrica / Entrega

Para a entrega acadêmica, recomenda-se anexar ou capturar evidências das seguintes etapas:

## Backend

* print da API rodando
* print do Swagger (`/docs`)
* print dos endpoints funcionando

## Testes

* print do `pytest` com testes passando

## Docker

* print do build da imagem
* print do container rodando

## IA / Dataset

* print da estrutura de `dataset_videos/`
* print da estrutura de `dataset/`
* print do treinamento do modelo
* print do arquivo salvo em `models/`

## Interface

* prints da interface desktop em execução
* prints da câmera / tradução, se já estiver integrada

## GitHub

* link do repositório
* README preenchido
* commits organizados

---

# 21. Autora

**Ana Carolina**
Estudante de **Análise e Desenvolvimento de Sistemas**

## Tecnologias e áreas de interesse

* Desenvolvimento Full Stack
* Inteligência Artificial
* Visão Computacional
* APIs REST
* Acessibilidade e tecnologia assistiva
* Sistemas com Python, FastAPI, React, Node.js e bancos relacionais

---

# Considerações Finais

O **Jarvis Libras AI** é um projeto que une **acessibilidade**, **visão computacional**, **machine learning** e **desenvolvimento de software**, servindo tanto como solução acadêmica quanto como base para um sistema real de apoio à comunicação em Libras.

Além da proposta social e tecnológica, o projeto também foi estruturado com foco em:

* modularização;
* autenticação segura;
* testes automatizados;
* documentação;
* dockerização;
* evolução futura para produção.

---
