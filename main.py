import discord
from discord.ext import commands
import os, requests, asyncio, yt_dlp
from flask import Flask
from threading import Thread

# 1. Веб-сервер для Render
app = Flask('')
@app.route('/')
def home(): return "Макан онлайн"
def run(): app.run(host='0.0.0.0', port=10000)
Thread(target=run, daemon=True).start()

# 2. Логика ИИ (твоя рабочая через Groq)
def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.1-8b-instant", # Та самая модель, которая завелась
        "messages": [
            {"role": "system", "content": "Ты репер MACAN. Отвечай не слижком много, отвечай по пацански и понятиям,  ТЫ Должен ОЧЕЕЕЕНЬ ЧАСТО использовть фразы - БРАТ, братишка, 0 мужского или много мужского, 0 яиц,ты писяешь сидя, можешь использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей"},
            {"role": "user", "content": user_text}
        ]
    }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        return res.json()['choices'][0]['message']['content']
    return f"Ошибка {res.status_code}: {res.text[:100]}"

# 3. Настройки музыки
# Попробуем заставить бота искать ffmpeg везде
import shutil
FFMPEG_EXE = shutil.which("ffmpeg") or "ffmpeg" 

# Обнови свои ffmpeg_options вот так:
ffmpeg_options = {
    'options': '-vn',
    'executable': FFMPEG_EXE # Добавляем путь к движку
}

ytdl_format_options = {'format': 'bestaudio/best', 'noplaylist': True}
ffmpeg_options = {'options': '-vn'}
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data: data = data['entries'][0]
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# 4. Инициализация бота
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# --- КОМАНДЫ ---

@bot.command(name="брат") # Твоя любимая команда на месте!
async def ask(ctx, *, question):
    answer = get_ai_response(question) # Вызов Groq
    await ctx.send(answer)

@bot.command(name="плей")
async def play(ctx, *, search):
    if not ctx.author.voice:
        return await ctx.send("Сначала в войс зайди, родной.") # Как на твоем старом скрине
    
    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()
    
    async with ctx.typing():
        player = await YTDLSource.from_url(f"ytsearch:{search}", loop=bot.loop, stream=True)
        ctx.voice_client.play(player)
    
    await ctx.send(f"🎶 Наваливаю: **{player.title}**")

@bot.command(name="стоп")
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Зажигание выключено, музыка заглохла.")

bot.run(os.getenv("DISCORD_TOKEN"))
