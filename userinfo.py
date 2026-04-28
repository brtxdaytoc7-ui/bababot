import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# --- RENDER CANLI TUTMA (GÜÇLENDİRİLMİŞ) ---
app = Flask('')

@app.route('/')
def home(): 
    return "İstihbarat İstasyonu Aktif!"

def run():
    # Render'ın atadığı portu otomatik bulur, hata payını sıfırlar.
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True # Bot kapandığında temizlenmesi için
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

# --- 1. PREMİUM UI (DERİN ANALİZ) ---
@bot.tree.command(name="ui", description="Kullanıcı kimliğini ve derin detaylarını dök (Gizli)")
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
        embed.set_footer(text="Sorgulama Gizli Modda Tamamlandı", icon_url=bot.user.display_avatar.url)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Hata: Kullanıcı bulunamadı.", ephemeral=True)

# --- 2. DM (HAYALET MESAJ) ---
@bot.tree.command(name="dm", description="ID kullanarak bot üzerinden özel mesaj gönder (Gizli)")
@app_commands.describe(id="Mesaj gidecek kişinin ID'si", mesaj="Mesaj içeriği")
async def dm(interaction: discord.Interaction, id: str, mesaj: str):
    await interaction.response.defer(ephemeral=True)
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send("❌ Yetkiniz yetersiz.", ephemeral=True)
        return
    try:
        user = await bot.fetch_user(int(id))
        await user.send(mesaj)
        await interaction.followup.send(f"✅ Mesaj başarıyla iletildi: **{user.name}**", ephemeral=True)
    except:
        await interaction.followup.send("❌ Mesaj iletilemedi (DM kapalı olabilir).", ephemeral=True)

# --- 3. CİHAZ BİLGİSİ ---
@bot.tree.command(name="cihaz", description="Kullanıcının aktif cihazlarını gör (Gizli)")
async def cihaz(interaction: discord.Interaction, hedef: discord.Member = None):
    user = hedef or interaction.user
    devices = []
    if str(user.desktop_status) != "offline": devices.append("💻 Bilgisayar")
    if str(user.mobile_status) != "offline": devices.append("📱 Telefon")
    if str(user.web_status) != "offline": devices.append("🌐 Tarayıcı")
    
    status_text = "\n".join(devices) if devices else "💤 Çevrimdışı veya Gizli"
    embed = discord.Embed(title=f"📡 Cihaz Durumu: {user.name}", description=status_text, color=0x2ecc71)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 4. AVATAR & BANNER ---
@bot.tree.command(name="avatar", description="Profil resmini tam boy gösterir")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        u = await bot.fetch_user(int(c_id))
        await interaction.followup.send(u.display_avatar.with_size(1024).url, ephemeral=True)
    except: await interaction.followup.send("❌ Hata.", ephemeral=True)

@bot.tree.command(name="banner", description="Profil afişini gösterir")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        u = await bot.fetch_user(int(c_id))
        full_u = await bot.fetch_user(u.id)
        if full_u.banner: await interaction.followup.send(full_u.banner.url, ephemeral=True)
        else: await interaction.followup.send("❌ Afiş yok.", ephemeral=True)
    except: await interaction.followup.send("❌ Veri çekilemedi.", ephemeral=True)

# --- 5. SİL (TEMİZLİK) ---
@bot.tree.command(name="sil", description="Mesajları arkanda iz bırakmadan yok et")
async def sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages: return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"✅ {len(deleted)} mesaj temizlendi.", ephemeral=True)

# --- BAŞLAT ---
if __name__ == "__main__":
    keep_alive() # Önce web sunucusunu uyandır
    bot.run(os.getenv('DISCORD_TOKEN'))
