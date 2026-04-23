import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- RENDER AYAKTA TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "Sistemler Aktif!"
def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive(): Thread(target=run).start()

intents = discord.Intents.default()
intents.members = True        
intents.message_content = True 
intents.presences = True # Cihaz bilgisi için ŞART

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()

bot = MyBot()

# --- 1. PREMIUM UI (GELİŞMİŞ İSTİHBARAT) ---
@bot.tree.command(name="ui", description="Kullanıcı hakkında derinlemesine bilgi dök (Gizli)")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        member = interaction.guild.get_member(user.id)
        embed_color = member.color if member else 0x2b2d31

        embed = discord.Embed(title=f"🕵️ Kullanıcı Analizi: {user.name}", color=embed_color)
        embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=False)
        embed.add_field(name="📅 Hesap Yaşı", value=f"<t:{int(user.created_at.timestamp())}:R>", inline=True)
        
        if member:
            embed.add_field(name="📥 Sunucu Giriş", value=f"<t:{int(member.joined_at.timestamp())}:d>", inline=True)
            roles = [r.mention for r in member.roles if r.name != "@everyone"]
            embed.add_field(name=f"🎭 Roller ({len(roles)})", value=", ".join(roles[:10]) or "Yok", inline=False)
        
        embed.set_image(url=user.display_avatar.with_size(1024).url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except: await interaction.followup.send("❌ Hata.", ephemeral=True)

# --- 2. CİHAZ SORGULAMA ---
@bot.tree.command(name="cihaz", description="Bağlantı cihazını gör (Gizli)")
async def cihaz(interaction: discord.Interaction, hedef: discord.Member = None):
    user = hedef or interaction.user
    devices = []
    if str(user.desktop_status) != "offline": devices.append(f"💻 Bilgisayar ({user.desktop_status})")
    if str(user.mobile_status) != "offline": devices.append(f"📱 Telefon ({user.mobile_status})")
    if str(user.web_status) != "offline": devices.append(f"🌐 Tarayıcı ({user.web_status})")

    embed = discord.Embed(title=f"📡 Cihaz Durumu: {user.name}", color=0x2ecc71)
    embed.description = "\n".join(devices) if devices else "💤 Çevrimdışı veya bilgi gizli."
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 3. ROL BİLGİSİ ---
@bot.tree.command(name="rol-bilgi", description="Rol detaylarını ve üyelerini dök (Gizli)")
async def rolbilgi(interaction: discord.Interaction, rol: discord.Role):
    embed = discord.Embed(title=f"🎭 Rol: {rol.name}", color=rol.color)
    embed.add_field(name="🆔 ID", value=f"`{rol.id}`", inline=True)
    embed.add_field(name="👥 Üye", value=f"`{len(rol.members)}`", inline=True)
    members = ", ".join([m.name for m in rol.members[:15]])
    embed.add_field(name="👤 Bazı Üyeler", value=members or "Boş.", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 4. AVATAR (EN BÜYÜK BOY) ---
@bot.tree.command(name="avatar", description="Profil resmini indir (Gizli)")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
    u = await bot.fetch_user(int(c_id))
    url = u.display_avatar.with_size(1024).url
    embed = discord.Embed(title=f"🖼️ {u.name} Avatarı", color=0x2b2d31)
    embed.description = f"[Tam boy indir]({url})"
    embed.set_image(url=url)
    await interaction.followup.send(embed=embed, ephemeral=True)

# --- 5. BANNER (AFİŞ) ---
@bot.tree.command(name="banner", description="Profil afişini al (Gizli)")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
    u = await bot.fetch_user(int(c_id))
    if u.banner:
        url = u.banner.with_size(1024).url
        await interaction.followup.send(f"🎨 **Afiş:** {url}", ephemeral=True)
    else: await interaction.followup.send("❌ Afiş yok.", ephemeral=True)

# --- 6. SİL (TEMİZLİK) ---
@bot.tree.command(name="sil", description="Mesajları sessizce sil")
async def sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.
