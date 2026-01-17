import discord
from discord.ext import commands
import os, requests, asyncio, random # Оставили только нужное
from flask import Flask
from threading import Thread

# 1. Веб-сервер для Render (оставляем, чтобы бот не спал)
app = Flask('')
@app.route('/')
def home(): return "Макан онлайн"
Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

# 2. Логика ИИ через Groq
def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}", "Content-Type": "application/json"}
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": "Ты репер MACAN. Отвечай кратко, так же ТЫ Должен ОЧЕЕЕЕНЬ ЧАСТО использовть такие фразы как БРАТ, братишка, 0 мужского или много мужского, 0 яиц,писаете сидя, череп:skull: и так же можешь использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей."}, {"role": "user", "content": user_text}]
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else "Ошибка связи"

# 3. Настройка бота
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Фотки должны лежать в корне рядом с main.py
MACAN_PHOTOS = ["1.png", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png"] 

@bot.event
async def on_ready():
    print(f" Брат Макан в сети как {bot.user}")

@bot.command(name="брат")
async def ask(ctx, *, question):
    # Сначала получаем ответ от ИИ
    response = get_ai_response(question)
    await ctx.send(response)
    
    if random.random() < 0.3:
        photo_name = random.choice(MACAN_PHOTOS)
        if os.path.exists(photo_name):
            with open(photo_name, 'rb') as f:
                await ctx.send(file=discord.File(f))

bot.run(os.getenv("DISCORD_TOKEN"))
