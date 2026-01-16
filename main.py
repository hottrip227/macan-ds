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

genai.configure(api_key=GEMINI_KEY, transport='rest') 
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
)


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

@bot.command(name="брат")
async def ask(ctx, *, question):
    try:
        # Убрал лимит в 40 символов для ошибки, чтобы мы видели ВСЁ
        prompt = f"Ты репер MACAN. Отвечай не слижком много, отвечай по пацански и иногда по понятиям, если спрашивают что то позорное то добавляй фразы: 0 мужского или много мужского, баба, писяешь сидя, женя про доту иногда можешь вставлять отрывки треков макана в ответы, можешь иногда использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей. Вопрос: {question}"
        response = model.generate_content(prompt)
        await ctx.send(response.text)
    except Exception as e:
        print(f"❌ ОШИБКА GEMINI: {e}")
        await ctx.send(f"Связь оборвалась, брат. (Полный текст: {str(e)})")

@bot.command()
async def play(ctx, *, search):
    if not ctx.author.voice:
        return await ctx.send("Сначала в войс зайди, родной.")
    
    vc = ctx.voice_client
    if not vc:
        vc = await ctx.author.voice.channel.connect()

    await ctx.send(f"🔍 Ищу для тебя: **{search}**...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            vc.stop()
            vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_opts))
            await ctx.send(f"🎶 Сейчас качает: **{title}**")
    except Exception as e:
        await ctx.send("Не удалось трек подтянуть.")
        print(f"Ошибка музыки: {e}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Тишина в зале.")

keep_alive()
if TOKEN:
    bot.run(TOKEN)
