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
def get_ai_response(user_text):
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        return "Брат, ключи от OpenRouter потерял. Проверь настройки!"

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "google/gemini-flash-1.5-exp:free", # Бесплатная и мощная модель
        "messages": [
            {"role": "system", "content": "Ты репер MACAN. Отвечай кратко, по пацански и со сленгом, так же ТЫ Должен ОЧЕЕЕЕНЬ ЧАСТО использовть такие фразы как БРАТ, братишка, 0 мужского или много мужского, 0 яиц,писаете сидя, череп 💀 и так же можешь использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей. Вопрос:"},
            {"role": "user", "content": user_text}
        ]
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=15)
        if res.status_code == 200:
            result = res.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"Ошибка OpenRouter: {res.status_code} - {res.text}")
            return "Брат, связь с OpenRouter оборвалась, переспроси позже."
    except Exception as e:
        print(f"Сетевая ошибка: {e}")
        return "Брат, на районе интернет отключили за неуплату."

# 3. Настройка бота
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Фотки должны лежать в корне рядом с main.py
MACAN_PHOTOS = ["1.png", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png"] 

@bot.event
async def on_ready():
    print(f" Брат Макан в сети как {bot.user}")
    
@bot.command(name="брат")
async def ask(ctx, *, question):
    response = get_ai_response(question)
    await ctx.send(response)
    
    if random.random() < 0.3:
        photo_name = random.choice(MACAN_PHOTOS)
        if os.path.exists(photo_name):
            with open(photo_name, 'rb') as f:
                await ctx.send(file=discord.File(f))

bot.run(os.getenv("DISCORD_TOKEN"))
