import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask
from threading import Thread

# Render 7/24 Aktif Tutma
app = Flask('')
@app.route('/')
def home(): return "Bot Aktif!"
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
        print("✅ Komutlar Discord'a işlendi!")

bot = MyBot()

# --- 1. UI (İSTİHBARAT) ---
@bot.tree.command(name="ui", description="ID ile veya etiketle bilgi çek")
async def ui(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer()
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        
        embed = discord.Embed(title=f"👤 {user.name} Analizi", color=0x2b2d31)
        embed.add_field(name="🆔 ID", value=f"`{user.id}`", inline=False)
        embed.add_field(name="📅 Hesap Açılış", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        
        member = interaction.guild.get_member(user.id)
        if member:
            embed.add_field(name="📥 Sunucuya Giriş", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
            roles = [r.mention for r in member.roles if r.name != "@everyone"]
            embed.add_field(name="🎭 Roller", value=", ".join(roles) or "Yok", inline=False)
        
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.followup.send(embed=embed)
    except:
        await interaction.followup.send("❌ Kullanıcı bulunamadı veya ID hatalı.")

# --- 2. BANNER (AFİŞ ÇALICI) ---
@bot.tree.command(name="banner", description="Profil afişini gösterir")
async def banner(interaction: discord.Interaction, hedef: str = None):
    await interaction.response.defer()
    try:
        clean_id = hedef.replace("<@", "").replace("!", "").replace(">", "") if hedef else str(interaction.user.id)
        user = await bot.fetch_user(int(clean_id))
        
        if user.banner:
            await interaction.followup.send(f"🖼️ **{user.name}** afişi:\n{user.banner.url}")
        else:
            # Banner bazen sadece 'fetch_user' ile gelmez, 'User' objesini tam çekmek gerekir
            full_user = await bot.fetch_user(user.id)
            if full_user.banner:
                await interaction.followup.send(full_user.banner.url)
            else:
                await interaction.followup.send("❌ Bu kullanıcının afişi yok.")
    except:
        await interaction.followup.send("❌ Hata oluştu.")

# --- 3. SİL (TEMİZLİK) ---
@bot.tree.command(name="sil", description="Belirtilen miktarda mesajı siler")
@app_commands.describe(miktar="Kaç mesaj silinsin?")
async def sil(interaction: discord.Interaction, miktar: int):
    # Yetki kontrolü
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("❌ Mesajları yönetme yetkin yok!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"✅ {len(deleted)} mesaj temizlendi.", ephemeral=True)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))
