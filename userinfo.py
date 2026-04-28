import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- RENDER CANLI TUTMA (ÖLÜMSÜZ MOD) ---
app = Flask('')

@app.route('/')
def home(): 
    return "İstihbarat İstasyonu Aktif!"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- BOT KURULUMU ---
intents = discord.Intents.default()
intents.members = True        
intents.message_content = True 
intents.presences = True 

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)
    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Sistemler Senkronize: {self.user}")

bot = MyBot()

# --- 1. UI (DERİN ANALİZ) ---
@bot.tree.command(name="ui", description="Kullanıcı kimliğini ve derin detaylarını dök (Gizli)")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        member = interaction.guild.get_member(user.id)
        embed = discord.Embed(title=f"🕵️ Kullanıcı Dosyası: {user.name}", color=member.color if member else 0x2b2d31)
        embed.add_field(name="🆔 Kimlik", value=f"`{user.id}`", inline=False)
        embed.add_field(name="📅 Kuruluş", value=f"<t:{int(user.created_at.timestamp())}:D>", inline=False)
        embed.set_image(url=user.display_avatar.with_size(1024).url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except: await interaction.followup.send("❌ Hata.", ephemeral=True)

# --- 2. ROL-BİLGİ (YENİ) ---
@bot.tree.command(name="rol-bilgi", description="Rolün detaylarını ve üyelerini gösterir (Gizli)")
async def rolbilgi(interaction: discord.Interaction, rol: discord.Role):
    embed = discord.Embed(title=f"🎭 Rol Analizi: {rol.name}", color=rol.color)
    embed.add_field(name="🆔 Rol ID", value=f"`{rol.id}`", inline=True)
    embed.add_field(name="👥 Üye Sayısı", value=f"`{len(rol.members)}`", inline=True)
    embed.add_field(name="🎨 Renk Kodu", value=f"`{rol.color}`", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 3. DM (HAYALET MESAJ) ---
@bot.tree.command(name="dm", description="ID ile bot üzerinden özel mesaj gönder (Gizli)")
async def dm(interaction: discord.Interaction, id: str, mesaj: str):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.guild_permissions.administrator: return
    try:
        user = await bot.fetch_user(int(id))
        await user.send(mesaj)
        await interaction.followup.send(f"✅ Mesaj iletildi: **{user.name}**", ephemeral=True)
    except: await interaction.followup.send("❌ DM kapalı.", ephemeral=True)

# --- 4. CİHAZ ---
@bot.tree.command(name="cihaz", description="Aktif cihazları gör (Gizli)")
async def cihaz(interaction: discord.Interaction, hedef: discord.Member = None):
    u = hedef or interaction.user
    d = []
    if str(u.desktop_status) != "offline": d.append("💻 PC")
    if str(u.mobile_status) != "offline": d.append("📱 Telefon")
    if str(u.web_status) != "offline": d.append("🌐 Tarayıcı")
    await interaction.response.send_message(f"📡 {u.name}: {' - '.join(d) or '💤 Çevrimdışı'}", ephemeral=True)

# --- 5. AVATAR & BANNER ---
@bot.tree.command(name="avatar", description="Profil fotoğrafını tam boy indir")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
    u = await bot.fetch_user(int(c_id))
    await interaction.followup.send(u.display_avatar.with_size(1024).url, ephemeral=True)

@bot.tree.command(name="banner", description="Profil afişini çal")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        u = await bot.fetch_user(int(c_id))
        full_u = await bot.fetch_user(u.id)
        if full_u.banner: await interaction.followup.send(full_u.banner.url, ephemeral=True)
        else: await interaction.followup.send("❌ Afiş yok.", ephemeral=True)
    except: await interaction.followup.send("❌ Hata.", ephemeral=True)

# --- 6. SİL ---
@bot.tree.command(name="sil", description="Mesajları yok et")
async def sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages: return
    await interaction.response.defer(ephemeral=True)
    await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"✅ {miktar} mesaj silindi.", ephemeral=True)

# --- BAŞLAT ---
if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('DISCORD_TOKEN'))
