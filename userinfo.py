import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# Render için ayakta tutma sistemi
app = Flask('')
@app.route('/')
def home():
    return "Bot aktif!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot ayarları ve Yetkiler (Intents)
intents = discord.Intents.default()
intents.members = True        # Üye bilgilerini çekmek için şart!
intents.message_content = True 

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Komutları Discord'a kaydeder
        await self.tree.sync()
        print(f"Komutlar senkronize edildi: {self.user}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'✅ Giriş yapıldı: {bot.user}')

@bot.tree.command(name="ui", description="Kullanıcı bilgisini gösterir")
async def ui(interaction: discord.Interaction, üye: discord.Member = None):
    üye = üye or interaction.user
    
    embed = discord.Embed(title=f"👤 Kullanıcı Bilgisi: {üye.name}", color=discord.Color.blue())
    embed.add_field(name="🆔 ID", value=üye.id, inline=False)
    embed.add_field(name="📅 Katılma Tarihi", value=üye.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="🎭 Roller", value=", ".join([role.mention for role in üye.roles if role.name != "@everyone"]) or "Yok", inline=False)
    embed.set_thumbnail(url=üye.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="Avatarı gösterir")
async def avatar(interaction: discord.Interaction, üye: discord.Member = None):
    üye = üye or interaction.user
    await interaction.response.send_message(üye.display_avatar.url)

# Başlat
keep_alive()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
