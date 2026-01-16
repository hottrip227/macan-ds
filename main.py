import os
import discord
from discord.ext import commands
import google.generativeai as genai
import yt_dlp
from flask import Flask
from threading import Thread

# --- БЛОК ДИАГНОСТИКИ ---
TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

print("--- ПРОВЕРКА КЛЮЧЕЙ ---")
print(f"DISCORD_TOKEN найден: {'ДА' if TOKEN else 'НЕТ'}")
print(f"GEMINI_KEY найден: {'ДА' if GEMINI_KEY else 'НЕТ'}")
print("-----------------------")
# ------------------------

app = Flask('')
@app.route('/')
def home(): return "Макан на связи!"

def run_web(): app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

if not TOKEN:
    print("❌ ОШИБКА: Токен Дискорда не дошел до кода!")
    # Мы не выходим сразу, чтобы Flask успел запуститься и Render не падал
else:
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-pro')

    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready(): print(f'✅ БОТ ЗАПУЩЕН: {bot.user.name}')

    @bot.command()
    async def ask(ctx, *, question):
        try:
            response = model.generate_content(f"Ты - MACAN. Отвечай не слижком много, если спрашивают что то позорное используй фразы: 0 мужского или много мужского, баба, иногда можешь вставлять отрывки треков макана в ответы, и изредка жалуйся что братья не помогли и ты 1 грустишь в армии: {question}")
            await ctx.send(response.text)
        except: await ctx.send("Связь оборвалась, брат.")

    @bot.command()
    async def play(ctx, *, search):
        if not ctx.author.voice: return await ctx.send("Зайди в войс!")
        vc = await ctx.author.voice.channel.connect()
        with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            vc.play(discord.FFmpegPCMAudio(info['url']))
        await ctx.send(f"🎶 Качает: {info['title']}")

keep_alive()
if TOKEN:
    bot.run(TOKEN)
