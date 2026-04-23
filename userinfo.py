import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread
import datetime

# --- RENDER AYAKTA TUTMA SİSTEMİ ---
app = Flask('')
@app.route('/')
def home(): return "Bot Aktif ve İstihbarat Topluyor!"
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
        print(f"✅ Sistemler Senkronize Edildi: {bot.user}")

bot = MyBot()

# --- 1. PREMIUM UI (GELİŞMİŞ İSTİHBARAT) ---
@bot.tree.command(name="ui", description="Kullanıcı hakkında derinlemesine bilgi dök (Gizli)")
@app_commands.describe(hedef="ID veya Etiket")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        
        member = interaction.guild.get_member(user.id)
        embed_color = member.color if member else 0x2b2d31

        embed = discord.Embed(title=f"🕵️ Kullanıcı Analizi: {user.name}", color=embed_color)
        
        # Temel Bilgiler
        embed.add_field(name="📌 Kimlik", 
                        value=f"**Ad:** {user.name}\n"
                              f"**ID:** `{user.id}`\n"
                              f"**Tip:** {'🤖 Bot' if user.bot else '👤 İnsan'}", inline=False)

        # Zamanlama
        hesap_yasi = (discord.utils.utcnow() - user.created_at).days
        embed.add_field(name="📅 Takvim", 
                        value=f"**Oluşturulma:** <t:{int(user.created_at.timestamp())}:D>\n"
                              f"**Yaş:** `{hesap_yasi}` Gün", inline=True)
        
        if member:
            embed.add_field(name="📥 Sunucu Durumu", 
                            value=f"**Giriş:** <t:{int(member.joined_at.timestamp())}:D>\n"
                                  f"**Nickname:** {member.display_name}", inline=True)
            
            roles = [r.mention for r in member.roles if r.name != "@everyone"]
            embed.add_field(name=f"🎭 Roller ({len(roles)})", value=", ".join(roles[:10]) or "Yok", inline=False)
        else:
            embed.add_field(name="🌐 Durum", value="Bu kullanıcı sunucuda değil.", inline=True)

        # Görsel: Avatarı büyük göster
        embed.set_image(url=user.display_avatar.with_size(1024).url)
        embed.set_footer(text="Sorgulama Başarıyla Tamamlandı • Gizli Mod")

        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Kullanıcı verisi çekilemedi. ID'yi kontrol et.", ephemeral=True)

# --- 2. AVATAR (FULL HD + LİNK) ---
@bot.tree.command(name="avatar", description="Profil fotoğrafını cam gibi indir (Gizli)")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        avatar_url = user.display_avatar.with_size(1024).url
        
        embed = discord.Embed(title=f"🖼️ {user.name} Avatarı", color=0x2b2d31)
        embed.description = f"🔗 [Orijinal Dosyayı İndir]({avatar_url})"
        embed.set_image(url=avatar_url)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        await interaction.followup.send("❌ Avatar bulunamadı.", ephemeral=True)

# --- 3. BANNER (PROFİL AFİŞİ ÇALICI) ---
@bot.tree.command(name="banner", description="Profil afişini çal (Gizli)")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer(ephemeral=True)
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        
        if user.banner:
            banner_url = user.banner.with_size(1024).url
            embed = discord.Embed(title=f"🎨 {user.name} Afişi", color=0x2b2d31)
            embed.description = f"🔗 [Afişi İndir]({banner_url})"
            embed.set_image(url=banner_url)
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send("❌ Bu kullanıcının afişi yok.", ephemeral=True)
    except:
        await interaction.followup.send("❌ Afiş çekilemedi.", ephemeral=True)

# --- 4. SİL (HAYALET TEMİZLİK) ---
@bot.tree.command(name="sil", description="Mesajları arkanda iz bırakmadan sil")
async def sil(interaction: discord.Interaction, miktar: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Yetkin yok!", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"✅ {len(deleted)} mesaj yok edildi. Kimse ruhu duymadı.", ephemeral=True)

# --- BOTU BAŞLAT ---
keep_alive()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
