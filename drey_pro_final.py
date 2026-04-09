import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("7017995495:AAG9C1QlXsVV6xM51CevHGWEWnZtdf5ABcE")

user_links = {}

qualities = {
    "144p": "worst",
    "360p": "18",
    "720p": "22",
    "1080p": "bestvideo+bestaudio",
    "MP3": "bestaudio"
}

async def start_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_links[update.message.chat_id] = url

    keyboard = [
        [InlineKeyboardButton("144p", callback_data="144p"),
         InlineKeyboardButton("360p", callback_data="360p")],
        [InlineKeyboardButton("720p", callback_data="720p"),
         InlineKeyboardButton("1080p", callback_data="1080p")],
        [InlineKeyboardButton("MP3 🎧", callback_data="MP3")]
    ]

    await update.message.reply_text(
        "📥 Elige la calidad:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    quality = query.data
    url = user_links.get(query.message.chat_id)

    await query.edit_message_text(f"⏳ Descargando en {quality}...")

    ydl_opts = {
        'format': qualities[quality],
        'outtmpl': '%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'downloader': 'aria2c',
        'downloader_args': ['-x', '16', '-k', '1M']
    }

    if quality == "MP3":
        ydl_opts.update({
            'format': 'bestaudio',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

            if quality == "MP3":
                file_name = file_name.rsplit(".", 1)[0] + ".mp3"

        if quality == "MP3":
            await query.message.reply_audio(audio=open(file_name, 'rb'))
        else:
            await query.message.reply_video(video=open(file_name, 'rb'))

        os.remove(file_name)

    except Exception as e:
        await query.message.reply_text(f"❌ Error:\n{e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start_download))
app.add_handler(CallbackQueryHandler(button_handler))

print("🔥 BOT PRO ACTIVO 🔥")
app.run_polling()
