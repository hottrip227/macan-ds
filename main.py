import os
import discord
from discord.ext import commands
import google.generativeai as genai
import yt_dlp
import asyncio
from flask import Flask
from threading import Thread

# --- БЛОК ДЛЯ RENDER (чтобы не засыпал) ---
app = Flask('')
@app.route('/')
def home():
    return "Макан на связи!"

def run_web():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_web)
    t.start()
# -----------------------------------------

# 1. ПРОВЕРКА КЛЮЧЕЙ
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

if not TOKEN or not GEMINI_KEY:
    print("❌ ОШИБКА: Проверь Environment Variables на Render!")
    exit(1)

# 2. НАСТРОЙКА ИИ
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

# 3. НАСТРОЙКА БОТА
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 4. КОМАНДЫ
@bot.event
async def on_ready():
    print(f'✅ БОТ ЗАПУЩЕН: {bot.user.name}')

@bot.command()
async def ask(ctx, *, question):
    try:
        response = model.generate_content(f"Ты - MACAN. Отвечай не слижком много, если спрашивают что то позорное используй фразы: 0 мужского или много мужского, баба, иногда можешь вставлять отрывки треков макана в ответы, и изредка жалуйся что братья не помогли и ты 1 грустишь в армии: {question}")
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send("Брат, чет связь сбоит с армии, повтори позже.")

@bot.command()
async def play(ctx, *, search):
    if not ctx.author.voice:
        return await ctx.send("Зайди в войс сначала, братик.")
    
    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect()

    await ctx.send(f"🔍 Ищу: {search}...")
    
    ydl_opts = {'format': 'bestaudio', 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        url = info['url']
        title = info['title']
        
    ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_opts))
    await ctx.send(f"🎶 Качает: **{title}**")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Тишина в зале.")

# 5. ЗАПУСК
if __name__ == "__main__":
    keep_alive() # Запускаем веб-сервер для Render
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
