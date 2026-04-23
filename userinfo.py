import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# Render'ın botu kapatmaması için Flask sistemi
app = Flask('')
@app.route('/')
def home(): return "Bot Aktif!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive(): Thread(target=run).start()

intents = discord.Intents.default()
intents.members = True        
intents.message_content = True 

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# --- AVATAR KOMUTU (GİZLİ) ---
@bot.tree.command(name="avatar", description="Profil fotoğrafını büyük boy al")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        avatar_url = user.display_avatar.with_size(1024).url
        embed = discord.Embed(title=f"🖼️ {user.name} Avatarı", color=0x2b2d31)
        embed.description = f"[Tam boy indir]({avatar_url})"
        embed.set_image(url=avatar_url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Avatar bulunamadı.", ephemeral=True)

# --- BANNER KOMUTU (GİZLİ) ---
@bot.tree.command(name="banner", description="Profil afişini al")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        if user.banner:
            banner_url = user.banner.with_size(1024).url
            await interaction.followup.send(f"🎨 **{user.name}** Afişi: {banner_url}", ephemeral=True)
        else:
            await interaction.followup.send("❌ Afiş yok.", ephemeral=True)
    except:
        await interaction.followup.send("❌ Hata.", ephemeral=True)

# --- UI KOMUTU (GİZLİ) ---
@bot.tree.command(name="ui", description="Kullanıcı bilgisi")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        embed = discord.Embed(title=f"👤 {user.name}", color=0x2b2d31)
        embed.add_field(name="ID", value=f"`{user.id}`")
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Hata.", ephemeral=True)

# --- SİL KOMUTU (GİZLİ) ---
@bot.tree.command(name="sil", description="Mesaj sil")
async def sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"✅ {len(deleted)} mesaj silindi.", ephemeral=True)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
