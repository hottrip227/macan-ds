import discord
from discord.ext import commands
import os
import requests
from flask import Flask
from threading import Thread

# Настройки
TOKEN = os.getenv("DISCORD_TOKEN")
GROQ_KEY = os.getenv("GROQ_API_KEY")

# Веб-сервер для Render
app = Flask('')
@app.route('/')
def home(): return "Макан на связи!"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=10000))
    t.daemon = True
    t.start()

# Логика ИИ через Groq (Llama-3 — самая стабильная)
def get_ai_response(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Ты репер MACAN. Отвечай не слижком много, отвечай по пацански и иногда по понятиям, если спрашивают что то позорное то добавляй фразы: 0 мужского или много мужского, баба, писяешь сидя, женя про доту иногда можешь вставлять отрывки треков макана в ответы, можешь иногда использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей, отвечай на русском языке."},
            {"role": "user", "content": text}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Брат, даже Groq выдал {response.status_code}. Проверь ключ."
    except Exception as e:
        return f"Траблы: {e}"

# Бот
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ МАКАН В ЗДАНИИ: {bot.user.name}')

@bot.command(name="брат")
async def ask(ctx, *, question):
    reply = get_ai_response(question)
    await ctx.send(reply)

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
