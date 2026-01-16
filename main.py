import discord
from discord.ext import commands
import os, requests
from flask import Flask
from threading import Thread

# 1. Железобетонный веб-сервер для Render
app = Flask('')
@app.route('/')
def home(): return "Макан онлайн"
def run(): app.run(host='0.0.0.0', port=10000)
Thread(target=run, daemon=True).start()

# 2. Чистая функция Groq без лишних оберток
def get_ai_response(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    # Формируем запрос строго по инструкции Groq
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Ты репер MACAN. Отвечай не слижком много, отвечай по пацански и иногда по понятиям, если спрашивают что то позорное то добавляй фразы: 0 мужского или много мужского, баба, писяешь сидя, женя про доту иногда можешь вставлять отрывки треков макана в ответы, можешь иногда использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей. "},
            {"role": "user", "content": user_text}
        ]
    }
    res = requests.post(url, headers=headers, json=data)
    if res.status_code == 200:
        return res.json()['choices'][0]['message']['content']
    return f"Ошибка {res.status_code}: {res.text[:100]}"

# 3. Бот
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.command(name="брат")
async def ask(ctx, *, question):
    # Просто передаем текст, система сама сделает его "пацанским"
    answer = get_ai_response(question)
    await ctx.send(answer)

bot.run(os.getenv("DISCORD_TOKEN"))
