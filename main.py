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
    api_key = os.getenv('GEMINI_API_KEY')
    # Если ключа нет в настройках Render, бот сразу скажет об этом в логах
    if not api_key:
        print("ОШИБКА: GEMINI_API_KEY не найден в переменных окружения!")
        return "Брат, ключи от машины потерял (API key не настроен)."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": f"Ты репер MACAN. Отвечай кратко, так же ТЫ Должен ОЧЕЕЕЕНЬ ЧАСТО использовть такие фразы как БРАТ, братишка, 0 мужского или много мужского, 0 яиц,писаете сидя, череп :skull: и так же можешь использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей {user_text}"}]}]
    }

    try:
        res = requests.post(url, headers=headers, json=data)
        if res.status_code == 200:
            result = res.json()
            # Достаем текст из ответа Gemini
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"Ошибка Gemini API: {res.status_code} - {res.text}")
            return "Брат, чет связь барахлит, переспроси позже."
    except Exception as e:
        print(f"Ошибка сети: {e}")
        return "Брат, на районе вышки связи упали."

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
