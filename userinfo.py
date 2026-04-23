import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread
from datetime import datetime

# Render için ayakta tutma sistemi (7/24 Kesintisiz)
app = Flask('')
@app.route('/')
def home():
    return "Bot aktif!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot Yetkileri (Intents)
intents = discord.Intents.default()
intents.members = True        
intents.message_content = True 

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ Komutlar senkronize edildi: {self.user}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'🚀 {bot.user} olarak giriş yapıldı!')

# --- YENİ SUNUCU DIŞI DESTEKLİ UI KOMUTU ---
@bot.tree.command(name="ui", description="Kullanıcı bilgisini gösterir (ID ile sunucu dışı dahil)")
@app_commands.describe(hedef="Etiketle veya sadece ID yapıştır")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer()
    
    try:
        # Eğer bir şey yazılmadıysa komutu kullanan kişiyi al
        if hedef is None:
            user = interaction.user
        else:
            # Hedefte etiket varsa ID'yi ayıkla, yoksa direkt ID olarak kullan
            clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "")
            user = await bot.fetch_user(int(clean_id))
        
        embed = discord.Embed(title=f"👤 Kullanıcı: {user.name}", color=discord.Color.blue())
        embed.add_field(name="🆔 ID", value=user.id, inline=False)
        embed.add_field(name="📅 Hesap Açılış", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        
        # Sunucuda olup olmadığını kontrol et
        member = interaction.guild.get_member(user.id)
        if member:
            embed.add_field(name="📅 Katılma Tarihi", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
            roles = [role.mention for role in member.roles if role.name != "@everyone"]
            embed.add_field(name="🎭 Roller", value=", ".join(roles) or "Yok", inline=False)
            embed.set_footer(text="Bu kullanıcı şu an bu sunucuda.")
        else:
            embed.set_footer(text="Bu kullanıcı sunucuda değil, Discord genelinden bulundu.")

        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.followup.send(embed=embed)

    except:
        await interaction.followup.send("❌ Hata: Geçerli bir ID girmelisin veya kullanıcı bulunamadı.")

# --- YENİ SUNUCU DIŞI DESTEKLİ AVATAR KOMUTU ---
@bot.tree.command(name="avatar", description="Avatarı gösterir (ID ile sunucu dışı dahil)")
@app_commands.describe(hedef="Etiketle veya sadece ID yapıştır")
async def avatar(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer()
    try:
        if hedef is None:
            user = interaction.user
        else:
            clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "")
            user = await bot.fetch_user(int(clean_id))
        
        await interaction.followup.send(user.display_avatar.url)
    except:
        await interaction.followup.send("❌ Hata: Kullanıcı bulunamadı.")

# Başlat
keep_alive()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
