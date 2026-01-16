import os
import discord
from discord.ext import commands
import google.generativeai as genai
import yt_dlp
import asyncio
from flask import Flask
from threading import Thread

# Настройка ключей
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Проверка в логах
print("--- ПРОВЕРКА КЛЮЧЕЙ ---")
print(f"DISCORD_TOKEN найден: {'ДА' if TOKEN else 'НЕТ'}")
print(f"GEMINI_KEY найден: {'ДА' if GEMINI_KEY else 'НЕТ'}")
print("-----------------------")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask('')
@app.route('/')
def home(): return "Макан на связи!"

def run_web(): app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ БОТ ЗАПУЩЕН: {bot.user.name}')

# КОМАНДА ДЛЯ ОБЩЕНИЯ
@bot.command(name="брат")
async def ask(ctx, *, question):
    try:
        prompt = f"Ты - MACAN. Отвечай не слижком много, если спрашивают что то позорное используй фразы: 0 мужского или много мужского, баба, иногда можешь вставлять отрывки треков макана в ответы, и изредка жалуйся что братья не помогли и ты 1 грустишь в армии. и еще своего добавляй чего то. Вопрос: {question}"
        response = model.generate_content(prompt)
        await ctx.send(response.text)
    except Exception as e:
        print(f"❌ ОШИБКА GEMINI: {e}")
        await ctx.send(f"Связь оборвалась, сука кабеля в армейке режут. (Ошибка: {str(e)[:40]})")

# КОМАНДА ДЛЯ МУЗЫКИ
@bot.command()
async def play(ctx, *, search):
    if not ctx.author.voice:
        return await ctx.send("Сначала в войс зайди, братик.")
    
    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect()

    await ctx.send(f"🔍 Ищу для тебя: **{search}**...")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            
            # Настройки для стабильного звука
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn',
            }
            
            vc.stop()
            vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))
            await ctx.send(f"🎶 Сейчас качает: **{title}**")
    except Exception as e:
        await ctx.send("Не удалось трек подтянуть, что-то с ссылкой.")
        print(f"Ошибка музыки: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Тишина в зале.")

keep_alive()
if TOKEN:
    bot.run(TOKEN)
