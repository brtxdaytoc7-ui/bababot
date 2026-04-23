import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# Render Ayakta Tutma
app = Flask('')
@app.route('/')
def home(): return "Bot aktif!"
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

# --- GELİŞMİŞ UI (Sunucu Dışı + ID Destekli) ---
@bot.tree.command(name="ui", description="Kullanıcı istihbaratı")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer()
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        
        embed = discord.Embed(title=f"🔍 İstihbarat: {user.name}", color=0x2f3136) # Dark mode gri
        embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=False)
        embed.add_field(name="📅 Hesap Açılış", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        
        member = interaction.guild.get_member(user.id)
        if member:
            embed.add_field(name="📥 Katılma", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
            roles = [r.mention for r in member.roles if r.name != "@everyone"]
            embed.add_field(name="🎭 Roller", value=", ".join(roles) or "Yok", inline=False)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        if user.banner: embed.set_image(url=user.banner.url)
        
        await interaction.followup.send(embed=embed)
    except:
        await interaction.followup.send("❌ Kullanıcı bulunamadı.")

# --- BANNER ÇALICI ---
@bot.tree.command(name="banner", description="Birinin profil afişini çalarsın")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer()
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id)) # fetch_user banner çekmek için şart
        
        # Banner çekmek için ayrı bir istek gerekebiliyor
        full_user = await bot.fetch_user(user.id)
        
        if full_user.banner:
            await interaction.followup.send(f"🖼️ **{full_user.name}** kullanıcısının afişi:\n{full_user.banner.url}")
        else:
            await interaction.followup.send("❌ Bu kullanıcının afişi yok (veya bot göremiyor).")
    except Exception as e:
        await interaction.followup.send(f"❌ Hata: {e}")

# --- MESAJ TEMİZLEYİCİ (Gizli Operasyon) ---
@bot.tree.command(name="sil", description="Ortalığı temizler")
@app_commands.checks.has_permissions(manage_messages=True)
async def sil(interaction: discord.Interaction, miktar: int):
    await interaction.response.send_message(f"🧹 {miktar} mesaj yok ediliyor...", ephemeral=True)
    await interaction.channel.purge(limit=miktar)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
