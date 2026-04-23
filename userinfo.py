import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# Render Ayakta Tutma Sistemi
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

# --- 1. UI (DETAYLI ANALİZ + AVATAR ÖNİZLEME) ---
@bot.tree.command(name="ui", description="Kullanıcı istihbaratı (Gizli)")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        
        embed = discord.Embed(title=f"👤 {user.name} Bilgileri", color=0x2b2d31)
        embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=False)
        embed.add_field(name="📅 Hesap Açılış", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        
        member = interaction.guild.get_member(user.id)
        if member:
            embed.add_field(name="📥 Sunucuya Giriş", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
            roles = [r.mention for r in member.roles if r.name != "@everyone"]
            embed.add_field(name="🎭 Roller", value=", ".join(roles) or "Yok", inline=False)
        
        # Profil fotoğrafını büyük gösterir
        embed.set_image(url=user.display_avatar.with_size(1024).url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Kullanıcı bulunamadı.", ephemeral=True)

# --- 2. AVATAR (BÜYÜK BOY + LİNK) ---
@bot.tree.command(name="avatar", description="Profil fotoğrafını büyük boy indir (Gizli)")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        
        # 1024px en yüksek kalitedir
        avatar_url = user.display_avatar.with_size(1024).url
        
        embed = discord.Embed(title=f"🖼️ {user.name} Avatarı", color=0x2b2d31)
        embed.description = f"[Buraya tıklayarak tam boy indir]({avatar_url})"
        embed.set_image(url=avatar_url)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Avatar çekilemedi.", ephemeral=True)

# --- 3. BANNER (PROFİL AFİŞİ) ---
@bot.tree.command(name="banner", description="Afiş çal (Gizli)")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        full_user = await bot.fetch_user(int(clean_id))
        
        if full_user.banner:
            banner_url = full_user.banner.with_size(1024).url
            embed = discord.Embed(title=f"🎨 {full_user.name} Afişi", color=0x2b2d31)
            embed.description = f"[Tam boy indir]({banner_url})"
            embed.set_image(url=banner_url)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Bu kullanıcının afişi yok.", ephemeral=True)
    except:
        await interaction.followup.send("❌ Hata oluştu.", ephemeral=True)

# --- 4. SİL (SESSİZ TEMİZLİK) ---
@bot.tree.command(name="sil", description="Mesajları yok et (Gizli)")
async def sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"✅ {len(deleted)} mesaj temizlendi.", ephemeral=True)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
