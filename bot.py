import os
import re
import html
import shutil
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from pdf_handler import (
    save_file,
    extract_text_from_file,
    index_text_with_faiss,
    query_index,
    summarize_pdf,
    call_openrouter,
)

from gdrive_handler import (
    start_flow,
    finish_flow,
    list_files,
    download_file,
)

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

BOT_NAME = os.getenv("BOT_NAME", "FinPilot")
BOT_TAGLINE = os.getenv("BOT_TAGLINE", "AI-ассистент по маркетингу, финтеху и бизнесу")

SYSTEM_PROMPT_CHAT = os.getenv(
    "SYSTEM_PROMPT_CHAT",
    "Ты – полезный бизнес-ассистент. Отвечай чётко и структурировано. "
    "Давай практические шаги, примеры, метрики. Без воды."
)

# --- Telegram output normalization: Markdown -> HTML (stable) ---

TG_MAX_LEN = 3900  # небольшой запас до лимита Telegram

def markdown_to_telegram_html(text: str) -> str:
    """
    Converts a subset of Markdown-like formatting from LLM into Telegram-safe HTML.
    - Escapes HTML
    - Converts headings (# / ###) to <b>
    - Converts **bold** to <b>
    - Converts *italic* to <i>
    - Converts `code` to <code>
    - Drops fenced code blocks ``` ```
    """
    if not text:
        return ""

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Drop fenced code blocks (often break formatting / too long)
    # Replace them with plain text content if you prefer; for now remove.
    import re
    text = re.sub(r"```.*?```", "", text, flags=re.S)

    # Escape HTML first
    text = html.escape(text)

    # Headings: ### Title -> <b>Title</b>
    text = re.sub(r"^#{1,6}\s*(.+)$", r"<b>\1</b>", text, flags=re.M)

    # Bold: **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    # Italic: *text*
    text = re.sub(r"(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)

    # Inline code: `text`
    text = re.sub(r"`(.*?)`", r"<code>\1</code>", text)

    # Убрать случайные остатки ###, если где-то не матчнулось
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)

    return text.strip()


async def send_html(update: Update, text: str):
    """
    Sends message(s) as Telegram HTML safely, splitting long outputs.
    """
    formatted = markdown_to_telegram_html(text)
    if not formatted:
        return

    # split by paragraphs first
    parts = []
    buf = ""
    for chunk in formatted.split("\n\n"):
        candidate = (buf + "\n\n" + chunk).strip() if buf else chunk.strip()
        if len(candidate) <= TG_MAX_LEN:
            buf = candidate
        else:
            if buf:
                parts.append(buf)
            # if single chunk too big, hard-split
            while len(chunk) > TG_MAX_LEN:
                parts.append(chunk[:TG_MAX_LEN])
                chunk = chunk[TG_MAX_LEN:]
            buf = chunk
    if buf:
        parts.append(buf)

    for p in parts:
        await update.message.reply_text(p, parse_mode="HTML")

def detect_markdown(text: str) -> bool:
    patterns = [
        r"\*\*(.*?)\*\*",
        r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)",
        r"`.*?`",
        r"```.*?```",
        r"__.*?__",
        r"\[.*?\]\(.*?\)",
    ]
    return any(re.search(p, text) for p in patterns)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Здравствуйте! Я {BOT_NAME} – {BOT_TAGLINE}.\n\n"
        "Я могу:\n"
        "- Помочь с маркетингом, продуктом, финтех-идеями и аналитикой\n"
        "- Подсказать стратегии, гипотезы, метрики, тексты, план действий\n"
        "- Отвечать по загруженным документам (PDF/DOCX/TXT): /askfile\n"
        "- Делать краткое содержание документа: /summary\n\n"
        "Для справки: /help"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Команды:\n"
        "/start – Приветствие\n"
        "/help – Справка\n"
        "/askfile [вопрос] – Вопрос по загруженному файлу\n"
        "/summary – Краткое содержание загруженного файла\n"
        "/reset – Сбросить индекс\n"
        "/syncdrive – Подключить Google Диск и выбрать файл\n"
    )

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists("./faiss_index"):
        shutil.rmtree("./faiss_index")
        os.makedirs("./faiss_index", exist_ok=True)
        await update.message.reply_text("✅ Контекст (индекс) сброшен.")
    else:
        await update.message.reply_text("Контекст уже пуст.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = (update.message.text or "").strip()
    if not user_input:
        return

    await update.message.reply_text("🧠 Думаю...")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_CHAT},
        {"role": "user", "content": user_input},
    ]
    reply = call_openrouter(messages=messages, temperature=0.4)

    await send_html(update, reply)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        return

    fname = (doc.file_name or "").lower()
    if not (fname.endswith(".pdf") or fname.endswith(".docx") or fname.endswith(".txt")):
        await update.message.reply_text("Поддерживаются только PDF, DOCX, TXT.")
        return

    await update.message.reply_text("📖 Читаю документ...")

    file = await doc.get_file()
    file_bytes = await file.download_as_bytearray()

    path = save_file(file_bytes, doc.file_name)
    text = extract_text_from_file(path)
    index_text_with_faiss(text)

    await update.message.reply_text("Документ прочитан. Используйте /askfile [вопрос] для быстрого поиска ответа или /summary для краткого пересказа документа.")

async def askfile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_text("Пример: /askfile Какие выводы в документе по метрикам?")
        return

    await update.message.reply_text("🔍 Ищу ответ...")
    response = query_index(query)

    await send_html(update, response)

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Пересказываю текст...")
    result = summarize_pdf()

    await send_html(update, result)

# ---- Google Drive ----
pending_auth = {}

async def syncdrive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flow, auth_url = start_flow(update.effective_user.id)
    pending_auth[update.effective_user.id] = flow
    context.user_data["step"] = "awaiting_auth_code"
    await update.message.reply_text(f"Перейдите по ссылке и отправьте код:\n{auth_url}")

async def handle_drive_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = (update.message.text or "").strip()
    user_id = update.effective_user.id

    flow = pending_auth.pop(user_id, None)
    if not flow:
        await update.message.reply_text("Сначала выполните /syncdrive.")
        return

    service = finish_flow(flow, code)
    context.user_data["gdrive_service"] = service

    files = list_files(service)
    if not files:
        await update.message.reply_text("Файлы не найдены.")
        return

    msg = "📄 Найденные файлы:\n"
    for fid, fname in files:
        msg += f"{fname} – ID: `{fid}`\n"
    msg += "\nОтправьте ID файла."

    context.user_data["drive_files"] = dict(files)
    context.user_data["step"] = "awaiting_file_id"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_drive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = (update.message.text or "").strip()
    drive_files = context.user_data.get("drive_files", {})

    if file_id not in drive_files:
        await update.message.reply_text("ID не найден. Скопируйте ID из списка.")
        return

    service = context.user_data.get("gdrive_service")
    if not service:
        await update.message.reply_text("Сначала выполните /syncdrive.")
        return

    filename = drive_files[file_id]
    path = os.path.join("./data", filename)

    await update.message.reply_text("📖 Читаю документ...")

    download_file(service, file_id, path)

    text = extract_text_from_file(path)
    index_text_with_faiss(text)

    context.user_data["step"] = None
    await update.message.reply_text(f"Документ {filename} прочитан. Используйте /askfile [вопрос] для быстрого поиска ответа или /summary для краткого пересказа документа.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")
    if step == "awaiting_auth_code":
        await handle_drive_code(update, context)
    elif step == "awaiting_file_id":
        await handle_drive_file(update, context)
    else:
        await handle_message(update, context)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("askfile", askfile))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("syncdrive", syncdrive))

    app.add_handler(
        MessageHandler(
            filters.Document.MimeType("application/pdf")
            | filters.Document.MimeType("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            | filters.Document.MimeType("text/plain"),
            handle_document,
        )
    )

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print(f"{BOT_NAME} работает. Ждите сообщений в Telegram.")
    app.run_polling()
