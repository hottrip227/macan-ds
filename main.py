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
        "messages": [{"role": "system", "content": "Ты репер MACAN. Отвечай кратко, так же ТЫ Должен ОЧЕЕЕЕНЬ ЧАСТО использовть такие фразы как БРАТ, братишка, 0 мужского или много мужского, 0 яиц,ты писяешь сидя, так же можешь использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей."}, {"role": "user", "content": user_text}]
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else "Ошибка ИИ"

# 3. Настройки музыки (SoundCloud — без капчи)
ytdl = yt_dlp.YoutubeDL({'format': 'bestaudio/best', 'noplaylist': True, 'quiet': True})

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        # Поиск через scsearch
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"scsearch:{url}", download=not stream))
        if 'entries' in data: data = data['entries'][0]
        filename = data['url']
        exe = shutil.which("ffmpeg") or "ffmpeg"
        return cls(discord.FFmpegPCMAudio(filename, executable=exe, options='-vn -b:a 128k'), data=data)

# 4. Бот
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.command(name="брат")
async def ask(ctx, *, question):
    await ctx.send(get_ai_response(question))

@bot.command(name="плей")
async def play(ctx, *, search):
    if not ctx.author.voice:
        return await ctx.send("Зайди в войс сначала!")
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    try:
        await ctx.author.voice.channel.connect()
        await ctx.send("✅ Залетел по-новой.")
    except Exception as e:
        return await ctx.send(f"❌ Не могу зайти: {str(e)}")
    
    async with ctx.typing():
        try:
            # Исправленный вызов только с 2 аргументами
            player = await YTDLSource.from_url(search, loop=bot.loop)
            
            if ctx.voice_client.is_playing():
                ctx.voice_client.stop()
                
            ctx.voice_client.play(player)
            ctx.voice_client.source.volume = 0.8
            await ctx.send(f"🔊 Наваливаю: **{player.title}**")
        except Exception as e:
            await ctx.send(f"❌ Трабл: {str(e)[:50]}")

@bot.command(name="стоп")
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Зажигание выключено.")

bot.run(os.getenv("DISCORD_TOKEN"))
