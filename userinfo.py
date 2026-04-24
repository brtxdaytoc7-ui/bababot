import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- RENDER CANLI TUTMA ---
app = Flask('')
@app.route('/')
def home(): return "Sistem Aktif!"

def run():
    app.run(host='0.0.0.0', port=10000)

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
        print(f"✅ Tüm komutlar yüklendi: {self.user}")

bot = MyBot()

# --- 1. PREMİUM UI (GELİŞMİŞ ANALİZ) ---
@bot.tree.command(name="ui", description="Kullanıcı hakkında derinlemesine bilgi dök (Gizli)")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        member = interaction.guild.get_member(user.id)
        
        color = member.color if member else 0x2b2d31
        embed = discord.Embed(title=f"🕵️ Kullanıcı Dosyası: {user.name}", color=color)
        
        embed.add_field(name="🆔 Kimlik", value=f"`{user.id}`", inline=False)
        embed.add_field(name="📅 Hesap Kuruluş", value=f"<t:{int(user.created_at.timestamp())}:D> (<t:{int(user.created_at.timestamp())}:R>)", inline=False)
        
        if member:
            embed.add_field(name="📥 Sunucu Giriş", value=f"<t:{int(member.joined_at.timestamp())}:f>", inline=True)
            roles = [r.mention for r in member.roles if r.name != "@everyone"]
            embed.add_field(name=f"🎭 Roller ({len(roles)})", value=" ".join(roles[:10]) if roles else "Yok", inline=False)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_image(url=user.display_avatar.with_size(1024).url)
        embed.set_footer(text="Sorgulama Gizli Tamamlandı", icon_url=bot.user.display_avatar.url)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Kullanıcı bulunamadı veya ID hatalı.", ephemeral=True)

# --- 2. CİHAZ BİLGİSİ ---
@bot.tree.command(name="cihaz", description="Kullanıcının hangi cihazdan bağlı olduğunu gör (Gizli)")
async def cihaz(interaction: discord.Interaction, hedef: discord.Member = None):
    user = hedef or interaction.user
    devices = []
    if str(user.desktop_status) != "offline": devices.append("💻 Bilgisayar")
    if str(user.mobile_status) != "offline": devices.append("📱 Telefon")
    if str(user.web_status) != "offline": devices.append("🌐 Tarayıcı")
    
    status_text = "\n".join(devices) if devices else "💤 Çevrimdışı veya Gizli Mod"
    embed = discord.Embed(title=f"📡 Cihaz Durumu: {user.name}", description=status_text, color=0x2ecc71)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 3. AVATAR (FULL HD) ---
@bot.tree.command(name="avatar", description="Profil fotoğrafını tam boy indir (Gizli)")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        url = user.display_avatar.with_size(1024).url
        embed = discord.Embed(title=f"🖼️ {user.name} Avatarı", color=0x2b2d31)
        embed.description = f"[Orijinal Görseli İndir]({url})"
        embed.set_image(url=url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Hata.", ephemeral=True)

# --- 4. BANNER (AFİŞ) ---
@bot.tree.command(name="banner", description="Profil afişini çal (Gizli)")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        full_user = await bot.fetch_user(user.id)
        if full_user.banner:
            url = full_user.banner.with_size(1024).url
            embed = discord.Embed(title=f"🎨 {full_user.name} Afişi", color=0x2b2d31)
            embed.set_image(url=url)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Kullanıcının afişi yok.", ephemeral=True)
    except:
        await interaction.followup.send("❌ Veri çekilemedi.", ephemeral=True)

# --- 5. ROL SORGULAMA ---
@bot.tree.command(name="rol-bilgi", description="Rolün detaylarını ve üyelerini gösterir (Gizli)")
async def rolbilgi(interaction: discord.Interaction, rol: discord.Role):
    embed = discord.Embed(title=f"🎭 Rol Analizi: {rol.name}", color=rol.color)
    embed.add_field(name="🆔 ID", value=f"`{rol.id}`", inline=True)
    embed.add_field(name="👥 Üye Sayısı", value=f"`{len(rol.members)}`", inline=True)
    members = ", ".join([m.name for m in rol.members[:15]])
    embed.add_field(name="👤 Üyeler", value=members or "Boş", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 6. SİL (TEMİZLİK) ---
@bot.tree.command(name="sil", description="Belirtilen miktarda mesajı yok et")
async def sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"✅ {len(deleted)} mesaj temizlendi.", ephemeral=True)

# --- ÇALIŞTIR ---
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
