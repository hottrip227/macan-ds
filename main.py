import discord
from discord.ext import commands
import os
import requests
from flask import Flask
from threading import Thread

# Настройки
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# Простейший веб-сервер для Render
app = Flask('')
@app.route('/')
def home(): return "Макан на связи!"

def run_web(): app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# Логика ИИ (пробуем версию v1beta с моделью gemini-pro - она самая живучая)
def get_ai_response(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
    payload = {"contents": [{"parts": [{"text": text}]}]}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Ошибка API: {response.status_code}. Брат, походу ключ реально устал."
    except Exception as e:
        return f"Траблы со связью: {e}"

# Настройка бота
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ БОТ ЗАПУЩЕН: {bot.user.name}')

@bot.command(name="брат")
async def ask(ctx, *, question):
    prompt = "Ты репер MACAN. Отвечай не слижком много, отвечай по пацански и иногда по понятиям, если спрашивают что то позорное то добавляй фразы: 0 мужского или много мужского, баба, писяешь сидя, женя про доту иногда можешь вставлять отрывки треков макана в ответы, можешь иногда использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей. Вопрос: "
    reply = get_ai_response(prompt + question)
    await ctx.send(reply)

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
