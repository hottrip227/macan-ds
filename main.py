import discord
from discord.ext import commands
import os, requests, asyncio, yt_dlp, shutil
from flask import Flask
from threading import Thread
import static_ffmpeg

# 1. Веб-сервер для Render
app = Flask('')
@app.route('/')
def home(): return "Макан онлайн"
Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

# Установка кодеков
static_ffmpeg.add_paths()

# 2. Логика ИИ через Groq
def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": "Ты репер MACAN. Отвечай кратко, так же ТЫ Должен ОЧЕЕЕЕНЬ ЧАСТО использовть такие фразы как БРАТ, братишка, 0 мужского или много мужского, 0 яиц,писаете сидя, так же можешь использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей.."}, {"role": "user", "content": user_text}]
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else "Ошибка ИИ"



# 4. Бот
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.command(name="брат")
async def ask(ctx, *, question):
    await ctx.send(get_ai_response(question))

# --- ВСТАВЛЯЙ СЮДА ---
import random

MACAN_PHOTOS = [
    "1.png", 
    "2.png", 
    "3.png",
    "4.png",
    "5.png",
    "6.png",
    "7.png"
]

@bot.event
async def on_message(message):
    # Чтобы бот не отвечал сам себе
    if message.author == bot.user:
        return

    # Шанс 30%
    if random.random() < 0.3:
        photo_name = random.choice(MACAN_PHOTOS)
        
        # Проверяем, есть ли файл в корне
        if os.path.exists(photo_name):
            with open(photo_name, 'rb') as f:
                await message.channel.send(file=discord.File(f))
    
    # Чтобы команды (!брат) продолжали работать
    await bot.process_commands(message)

bot.run(os.getenv("DISCORD_TOKEN"))
