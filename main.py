import discord
from discord.ext import commands
import os
import requests
from flask import Flask
from threading import Thread

# Настройки
TOKEN = os.getenv("DISCORD_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN") # Твой новый ключ от Hugging Face

# Веб-сервер для Render
app = Flask('')
@app.route('/')
def home(): return "Макан на связи!"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=10000))
    t.daemon = True
    t.start()
    
def get_ai_response(text):
    # Меняем модель на более стабильную Llama-3
    api_url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{text}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
        "parameters": {"max_new_tokens": 250, "temperature": 0.7}
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            res_json = response.json()
            # У Llama немного другой формат ответа, вытаскиваем чистый текст
            full_text = res_json[0]['generated_text']
            return full_text.split("<|start_header_id|>assistant<|end_header_id|>\n\n")[-1].strip()
        else:
            return f"Брат, даже Llama выдала {response.status_code}. Проверь ключ HF_TOKEN в Render."
    except Exception as e:
        return f"Траблы со связью: {e}"

# Бот
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ МАКАН В ЗДАНИИ: {bot.user.name}')

@bot.command(name="брат")
async def ask(ctx, *, question):
    prompt = "Ты - репер MACAN. Отвечай не слижком много, отвечай по пацански и иногда по понятиям, если спрашивают что то позорное то добавляй фразы: 0 мужского или много мужского, баба, писяешь сидя, женя про доту иногда можешь вставлять отрывки треков макана в ответы, можешь иногда использовать матерные слова. и изредка жалуйся что братки не помогли и ты один грустишь в армии без друзей. Вопрос:, на русском языке. "
    reply = get_ai_response(prompt + question)
    await ctx.send(reply)

if __name__ == "__main__":
    keep_alive()
    bot.run(TOKEN)
