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

# --- 1. GÜÇLENDİRİLMİŞ UI (DERİN İSTİHBARAT) ---
@bot.tree.command(name="ui", description="Kullanıcı hakkında derinlemesine istihbarat dök (Gizli)")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user_id = int(clean_id)
        user = await bot.fetch_user(user_id)
        member = interaction.guild.get_member(user_id)
        
        color = member.color if member else 0x2b2d31
        embed = discord.Embed(title=f"🔍 İstihbarat Dosyası: {user.name}", color=color)
        
        # Rozet Analizi
        flags = []
        f = user.public_flags
        if f.active_developer: flags.append("💻 Aktif Geliştirici")
        if f.early_supporter: flags.append("🏅 Erken Destekçi")
        if f.hypesquad_balance: flags.append("⚖️ Balance")
        if f.hypesquad_bravery: flags.append("🦁 Bravery")
        if f.hypesquad_brilliance: flags.append("💎 Brilliance")
        badge_text = " ".join(flags) if flags else "Yok"

        embed.add_field(name="👤 Kullanıcı", value=f"{user.mention}\n`{user.name}`", inline=True)
        embed.add_field(name="🆔 Kimlik", value=f"`{user.id}`", inline=True)
        embed.add_field(name="🎖️ Rozetler", value=badge_text, inline=True)
        
        embed.add_field(name="📅 Hesap Kuruluş", value=f"<t:{int(user.created_at.timestamp())}:D>\n(<t:{int(user.created_at.timestamp())}:R>)", inline=True)
        
        if member:
            embed.add_field(name="📥 Sunucu Giriş", value=f"<t:{int(member.joined_at.timestamp())}:D>\n(<t:{int(member.joined_at.timestamp())}:R>)", inline=True)
            perm = "🛡️ Yönetici" if member.guild_permissions.administrator else "👤 Üye"
            embed.add_field(name="🔑 Yetki", value=f"`{perm}`", inline=True)
            roles = [r.mention for r in member.roles if r.name != "@everyone"][::-1]
            if roles:
                embed.add_field(name=f"🎭 Roller ({len(roles)})", value=" ".join(roles[:10]), inline=False)

        embed.set_thumbnail(url=user.display_avatar.url)
        user_full = await bot.fetch_user(user.id)
        if user_full.banner: embed.set_image(url=user_full.banner.url)
        else: embed.set_image(url=user.display_avatar.with_size(1024).url)
        
        embed.set_footer(text="Sorgulama Gizli Modda Tamamlandı", icon_url=bot.user.display_avatar.url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except: await interaction.followup.send("❌ Hata: Kullanıcı bulunamadı.", ephemeral=True)

# --- 2. ROL-BİLGİ ---
@bot.tree.command(name="rol-bilgi", description="Rolün detaylarını ve üyelerini gösterir (Gizli)")
async def rolbilgi(interaction: discord.Interaction, rol: discord.Role):
    embed = discord.Embed(title=f"🎭 Rol Analizi: {rol.name}", color=rol.color)
    embed.add_field(name="🆔 Rol ID", value=f"`{rol.id}`", inline=True)
    embed.add_field(name="👥 Üye Sayısı", value=f"`{len(rol.members)}`", inline=True)
    embed.add_field(name="🎨 Renk Kodu", value=f"`{rol.color}`", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 3. DM ---
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
    try:
        c_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        u = await bot.fetch_user(int(c_id))
        await interaction.followup.send(u.display_avatar.with_size(1024).url, ephemeral=True)
    except: await interaction.followup.send("❌ Hata.", ephemeral=True)

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
