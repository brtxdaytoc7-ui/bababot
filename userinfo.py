import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- RENDER AYAKTA TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "Sistemler Online!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
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
        # Komutları Discord'a senkronize eder
        await self.tree.sync()

bot = MyBot()

# --- 1. PREMIUM UI ---
@bot.tree.command(name="ui", description="Kullanıcı istihbaratı (Gizli)")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        member = interaction.guild.get_member(user.id)
        
        embed = discord.Embed(title=f"🕵️ Analiz: {user.name}", color=0x2b2d31)
        embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=True)
        embed.add_field(name="📅 Kuruluş", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        
        if member:
            roles = [r.mention for r in member.roles if r.name != "@everyone"]
            embed.add_field(name=f"🎭 Roller ({len(roles)})", value=", ".join(roles[:10]) or "Yok", inline=False)
        
        embed.set_image(url=user.display_avatar.with_size(1024).url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Hata: {str(e)}", ephemeral=True)

# --- 2. CİHAZ ---
@bot.tree.command(name="cihaz", description="Bağlantı cihazını gör (Gizli)")
async def cihaz(interaction: discord.Interaction, hedef: discord.Member = None):
    user = hedef or interaction.user
    devices = []
    if str(user.desktop_status) != "offline": devices.append(f"💻 Bilgisayar")
    if str(user.mobile_status) != "offline": devices.append(f"📱 Telefon")
    if str(user.web_status) != "offline": devices.append(f"🌐 Tarayıcı")

    embed = discord.Embed(title=f"📡 Cihaz: {user.name}", color=0x2ecc71)
    embed.description = "\n".join(devices) if devices else "💤 Çevrimdışı veya gizli."
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 3. ROL BİLGİ ---
@bot.tree.command(name="rol-bilgi", description="Rol detayları (Gizli)")
async def rolbilgi(interaction: discord.Interaction, rol: discord.Role):
    embed = discord.Embed(title=f"🎭 Rol: {rol.name}", color=rol.color)
    embed.add_field(name="👥 Üye", value=f"`{len(rol.members)}`")
    members = ", ".join([m.name for m in rol.members[:15]])
    embed.add_field(name="👤 Üyeler", value=members or "Boş.", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 4. AVATAR ---
@bot.tree.command(name="avatar", description="Profil resmi (Gizli)")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        u = await bot.fetch_user(int(c_id))
        url = u.display_avatar.with_size(1024).url
        await interaction.followup.send(url, ephemeral=True)
    except:
        await interaction.followup.send("❌ Bulunamadı.", ephemeral=True)

# --- 5. BANNER ---
@bot.tree.command(name="banner", description="Afiş (Gizli)")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        u = await bot.fetch_user(int(c_id))
        # Banner çekmek için user objesini zorla güncelliyoruz
        full_user = await bot.fetch_user(u.id)
        if full_user.banner:
            await interaction.followup.send(full_user.banner.with_size(1024).url, ephemeral=True)
        else:
            await interaction.followup.send("❌ Afiş yok.", ephemeral=True)
    except:
        await interaction.followup.send("❌ Hata.", ephemeral=True)

# --- 6. SİL ---
@bot.tree.command(name="sil", description="Mesaj temizle")
async def sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"✅ {len(deleted)} mesaj temizlendi.", ephemeral=True)

# --- ÇALIŞTIR ---
if __name__ == "__main__":
    keep_alive()
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ HATA: DISCORD_TOKEN bulunamadı!")
