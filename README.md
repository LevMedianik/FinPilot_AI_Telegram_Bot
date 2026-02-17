## EN: 🤖 FinPilot – Controlled RAG AI Assistant for Document-Based Q&A

FinPilot is a Telegram-based AI assistant built with a controlled Retrieval-Augmented Generation (RAG) architecture.
It answers strictly based on uploaded documents and safely refuses when relevant information is not found.

The system is designed for real-world business use cases such as fintech, analytics, internal knowledge bases, compliance documentation, and marketing operations.

---

### 🚀 Features

- 📄 Document ingestion (PDF / DOCX / TXT)
- 🔍 Retrieval-based question answering over documents (RAG)
- 🧾 Answers with source citations
- 🚫 Controlled refusal outside document context (anti-hallucination)
- 💬 General-purpose LLM chat mode
- 📑 Document summarization (/summary)
- 🧠 Structured HTML message formatting for Telegram

---

### 🧩 Architecture

```
Document → Text Extraction → Embeddings → FAISS
                                      ↓
User → Query → Retrieval → RAG Gate → LLM → Answer / Refusal
```

Core Design Principles
- Strict RAG – Answers only based on retrieved context
- Citations-first – Each claim supported by document excerpts
- Fail-safe behavior – Honest refusal when no evidence is found

### 🛡️ Anti-Hallucination Controls

Multiple reliability layers are implemented:

1. Semantic retrieval (FAISS) – Only relevant fragments are retrieved.
2. Distance gate – Response generated only if vector similarity passes a threshold.
3. Overlap gate – Checks keyword intersection between query and retrieved context.
4. Strict prompting – The LLM must:
  1) Answer strictly from context
  2) Provide citations
  3) Refuse when insufficient data is available

---

### 🧪 Example Behavior

Valid Answer

Query:
/askfile How is fraud detection effectiveness measured?

Response:

Fraud detection effectiveness is measured not only by prevented losses, but also by its impact on user experience and conversion.
Citation: "Fraud detection effectiveness is measured not only by prevented losses, but also by its impact on user experience and conversion."

Safe Refusal

Query:
/askfile Why did life originate on Earth?

Response:

The current document database does not contain information relevant to this question.
I only answer based on uploaded materials.

---

### 📂 Supported Formats: PDF, DOCX, TXT

After ingestion, the bot indexes the document and enables /askfile and /summary.

---

### ⚙️ Configuration (.env)
```
TELEGRAM_TOKEN=...
OPENROUTER_API_KEY=...
HUGGINGFACEHUB_API_TOKEN=...
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
RAG_MIN_CONTEXT_CHARS=300
RAG_MAX_L2_DISTANCE=1.0
```
### ▶️ Local Setup

1) Requirements

- Python 3.11–3.12
- Telegram account

2) Installation
```
git clone https://github.com/LevMedianik/finpilot_bot
cd finpilot_bot
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

3) Run:
```
python bot.py
```

---

### 🐳 Docker Setup

Build image:
```
docker build --no-cache -t finpilot:latest .
```

Run container:
```
docker run --rm -it \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/faiss_index:/app/faiss_index" \
  finpilot:latest
```

---

### 🛠️ Tech Stack

- Python 3.12
- FastAPI
- LangChain
- FAISS
- HuggingFace Embeddings
- OpenRouter (LLM backend)
- PyMuPDF / python-docx
- Docker

---

### 🎯 Purpose

This project demonstrates a production-oriented, controlled RAG architecture suitable for business environments requiring reliability and transparency.

It serves as:

- A technical portfolio project
- A base architecture for enterprise knowledge assistants
- A scalable foundation for internal AI document agents

---

### 📌 Status

v1.0 – Stable demo
Focus: reliability, reproducibility, and safe behavior.

### 👤 Author

Lev Medianik
AI / ML Engineer

GitHub: https://github.com/LevMedianik

## RU: 🤖 FinPilot – AI-ассистент с контролируемым RAG по документам

FinPilot – Telegram-бот с Retrieval-Augmented Generation (RAG), который отвечает строго на основе загруженных документов и корректно отказывает, если информации нет в базе.
Проект ориентирован на бизнес-кейсы: финтех, маркетинг, аналитика, регламенты, внутренние базы знаний.

---

### 🚀 Возможности

- 📄 Загрузка документов (PDF / DOCX / TXT)
- 🔍 Поиск и ответы по содержимому документов (RAG)
- 🧾 Ответы с цитатами из источника
- 🚫 Контролируемый отказ вне контекста (без галлюцинаций)
- 🧠 Живое общение (LLM-чат)
- 📑 Краткое резюме документа (/summary)
- 💬 Корректное форматирование сообщений в Telegram (HTML)

---

### 🧩 Архитектура
```
Документ → Извлечение текста → Embeddings → FAISS
                                   ↓
Пользователь → Запрос → Retrieval → RAG-Gate → LLM → Ответ / Отказ
```

Ключевые принципы
- Strict RAG – ответы только по контексту
- Citations-first – каждый пункт подтверждён фразой из документа
- Fail-safe – если данных нет, бот честно сообщает об этом

---

### 🛡️ Контроль качества ответов (Anti-hallucination)

В проекте реализованы несколько уровней защиты:

1. Semantic retrieval (FAISS). Извлекаются только наиболее релевантные фрагменты документа.
2. Distance gate. Ответ формируется только если расстояние между запросом и контекстом ниже заданного порога.
3. Overlap gate. Проверяется наличие пересечений ключевых слов вопроса и найденного контекста.
4. Strict prompt. LLM обязан:
    1) отвечать только по контексту
    2) прикладывать цитаты
    3) отказывать при отсутствии данных

---

### 🧪 Примеры поведения

Корректный ответ
/askfile в чем измеряется эффективность антифрод-систем

Ответ:

Пункт: уровень предотвращённых потерь и влияние на пользовательский опыт.
Цитата: "Эффективность антифрода измеряется не только уровнем предотвращённых потерь, но и влиянием на пользовательский опыт и конверсию."

Корректный отказ
/askfile почему жизнь возникла на земле

Ответ:

В текущей базе документов нет информации для ответа на этот вопрос.
Я отвечаю только на основе загруженных материалов.

---

### 🧾 Команды бота
|Команда  	        |Описание|
|-------------------|--------|
|/start             |– запуск бота|
|/help              |– справка по командам|
|/askfile [вопрос]  |– вопрос по загруженному документу|
|/summary           |– краткое резюме документа|
|/reset             |– очистка текущего контекста файла для отправки нового|
|/syncdrive         |– подключить Google Диск и выбрать документ|

---

### 📂 Поддерживаемые форматы: PDF, DOCX, TXT

При загрузке файла бот сообщает: "Читаю документ..."
После индексации: "Документ прочитан. Используйте /askfile [вопрос] для быстрого поиска ответа или /summary для краткого пересказа документа."

---

### ⚙️ Конфигурация (.env)

TELEGRAM_TOKEN=...
OPENROUTER_API_KEY=...
HUGGINGFACEHUB_API_TOKEN=...

EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

RAG_MIN_CONTEXT_CHARS=300
RAG_MAX_L2_DISTANCE=1.0

SYSTEM_PROMPT=Ты – ассистент для ответов по документам. Отвечай только фактами из контекста.
SYSTEM_PROMPT_CHAT=Ты – полезный бизнес-ассистент. Не выдумывай факты.

---

### ▶️ Запуск локально
1) Требования

Python 3.11–3.12
Установлен Telegram

2) Клонирование проекта
```
git clone <https://github.com/LevMedianik?tab=repositories>
cd finpilot_bot
```
3) Виртуальное окружение

Windows (PowerShell / cmd)
```
python -m venv venv
venv\Scripts\activate
```

Linux / macOS
```
python3 -m venv venv
source venv/bin/activate
```
4) Установка зависимостей
```
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```
5) Настройка .env

Создайте файл .env в корне проекта:
```
TELEGRAM_TOKEN=...
OPENROUTER_API_KEY=...
HUGGINGFACEHUB_API_TOKEN=...

RAG_MIN_CONTEXT_CHARS=300
RAG_MAX_L2_DISTANCE=1.0
```
6) Запуск
```
python bot.py
```
7) Быстрый тест

В Telegram:

/start

начните общение или отправьте документ PDF/DOCX/TXT, бот ответит «Читаю документ...»

используйте /askfile <вопрос> или /summary

---

### 🐳 Запуск через Docker
1) Требования

Docker установлен и запущен

2) Сборка образа
```
docker build --no-cache -t finpilot:latest .
```
3) Запуск контейнера с .env
Linux / macOS / Git Bash
```
docker run --rm -it \
  --env-file .env \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/faiss_index:/app/faiss_index" \
  finpilot:latest
```
Windows PowerShell
```
docker run --rm -it `
  --env-file .env `
  -v "${PWD}\data:/app/data" `
  -v "${PWD}\faiss_index:/app/faiss_index" `
  finpilot:latest
```
4) Проверка

Точно так же, как локально:

/start

загрузка файла – «Читаю документ...»

/askfile ... или /summary

---

### 🛠️ Технологии

- Python 3.12
- Telegram Bot API
- OpenRouter (LLM)
- HuggingFace Embeddings
- FAISS
- LangChain
- PyMuPDF / python-docx

---

### 🎯 Назначение проекта

Проект создан как демонстрация контролируемого RAG-подхода для клиентов, команд и организаций, работающих с финтехом, аналитикой и маркетингом. Основная цель – показать практическую реализацию AI-ассистента, который отвечает строго по документам и корректно отказывает вне контекста.

Проект также используется как универсальное демонстрационное решение:
- для презентации заказчикам;
- для оценки технических навыков при откликах в компании и команды;
- как база для масштабирования в корпоративного ассистента, AI-агента по регламентам или внутренний knowledge-bot.

---

### 📌 Статус проекта

v1.0 – Stable demo
Фокус на корректности, воспроизводимости и отказе от галлюцинаций.

---

### 👤 Автор

Lev Medianik
AI / ML Engineer

GitHub: https://github.com/LevMedianik