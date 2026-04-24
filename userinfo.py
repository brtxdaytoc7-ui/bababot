import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- RENDER AYAKTA TUTMA SİSTEMİ ---
app = Flask('')
@app.route('/')
def home(): return "Bot Aktif!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- BOT AYARLARI ---
intents = discord.Intents.default()
intents.members = True        
intents.message_content = True 
intents.presences = True 

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Komutlar senkronize edildi: {self.user}")

bot = MyBot()

# --- KOMUTLAR ---

@bot.tree.command(name="ui", description="Kullanıcı analizi (Gizli)")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        member = interaction.guild.get_member(user.id)
        embed = discord.Embed(title=f"🕵️ {user.name}", color=0x2b2d31)
        embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="📅 Hesap Yaşı", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        embed.set_image(url=user.display_avatar.with_size(1024).url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except: await interaction.followup.send("❌ Veri çekilemedi.", ephemeral=True)

@bot.tree.command(name="avatar", description="Avatarı indir (Gizli)")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        u = await bot.fetch_user(int(c_id))
        url = u.display_avatar.with_size(1024).url
        await interaction.followup.send(f"🖼️ {u.name} Avatarı: {url}", ephemeral=True)
    except: await interaction.followup.send("❌ Hata.", ephemeral=True)

@bot.tree.command(name="cihaz", description="Bağlantı cihazını gör (Gizli)")
async def cihaz(interaction: discord.Interaction, hedef: discord.Member = None):
    user = hedef or interaction.user
    devices = []
    if str(user.desktop_status) != "offline": devices.append("💻 Bilgisayar")
    if str(user.mobile_status) != "offline": devices.append("📱 Telefon")
    if str(user.web_status) != "offline": devices.append("🌐 Tarayıcı")
    
    msg = "\n".join(devices) if devices else "💤 Çevrimdışı veya gizli."
    await interaction.response.send_message(f"📡 **{user.name} cihaz durumu:**\n{msg}", ephemeral=True)

@bot.tree.command(name="sil", description="Mesaj temizle")
async def sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"✅ {len(deleted)} mesaj temizlendi.", ephemeral=True)

# --- BAŞLATMA ---
if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ TOKEN BULUNAMADI!")
