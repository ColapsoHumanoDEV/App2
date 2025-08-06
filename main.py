import discord
from discord.ext import commands
import os
import json
import time

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="+", intents=intents)

XP_FILE = "levels/xp_data.json"
COOLDOWN_TIME = 45 * 60  # 45 minutos

if not os.path.exists("levels"):
    os.makedirs("levels")

if not os.path.exists(XP_FILE):
    with open(XP_FILE, "w") as f:
        json.dump({}, f)


def load_xp_data():
    with open(XP_FILE, "r") as f:
        return json.load(f)


def save_xp_data(data):
    with open(XP_FILE, "w") as f:
        json.dump(data, f)


@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} está online!")


@bot.command()
async def xp(ctx):
    user_id = str(ctx.author.id)
    data = load_xp_data()
    now = time.time()

    if user_id not in data:
        data[user_id] = {
            "xp": 0,
            "last_used": 0,
            "meta": 100
        }

    user = data[user_id]
    time_since_last = now - user["last_used"]

    if time_since_last >= COOLDOWN_TIME:
        user["xp"] += 50
        user["last_used"] = now

        if user["xp"] >= user["meta"]:
            user["meta"] *= 2
            await ctx.send(embed=discord.Embed(
                title="🎉 Parabéns!",
                description=f"{ctx.author.mention} atingiu a meta de XP!\nNova meta: **{user['meta']} XP**\nContinue ativo!",
                color=discord.Color.green()
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title="✅ XP Adicionado",
                description=f"{ctx.author.mention} agora tem **{user['xp']} XP** de **{user['meta']} XP** da meta.",
                color=discord.Color.blue()
            ))

        save_xp_data(data)
    else:
        tempo_restante = int((COOLDOWN_TIME - time_since_last) // 60)
        await ctx.send(embed=discord.Embed(
            title="⏳ Aguarde!",
            description=f"{ctx.author.mention}, você poderá ganhar mais XP em **{tempo_restante} minutos**.",
            color=discord.Color.red()
        ))


@bot.command()
async def level(ctx):
    user_id = str(ctx.author.id)
    data = load_xp_data()

    if user_id not in data:
        await ctx.send(f"{ctx.author.mention}, você ainda não tem XP. Use `+xp` para começar.")
        return

    user = data[user_id]
    embed = discord.Embed(
        title="📊 Seu Progresso de XP",
        description=f"""
👤 Usuário: {ctx.author.mention}
⭐ XP Atual: **{user['xp']}**
🎯 Meta: **{user['meta']} XP**
""",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)


# Rodar com token da variável de ambiente
bot.run(os.getenv("TOKEN"))