import discord
from discord import app_commands
from discord.ext import commands
import os # Bu satır şifreyi gizli dosyadan çekmek için şart

class MyBot(commands.Bot):
    def __init__(self):
       intents = discord.Intents.default()
       intents.members = True  # Üye bilgilerini (roller, tarihler) görmek için
       intents.presences = True # Durum bilgilerini görmek için
       intents.message_content = True # Mesaj içeriği için
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Komutları Discord'a tanımlar
        await self.tree.sync()
        print(f"✅ Sistem hazır: {self.user.name}")

bot = MyBot()

# --- 1. GİZLİ UI KOMUTU ---
@bot.tree.command(name="ui", description="Kullanıcı bilgilerini sadece sana özel gösterir")
async def ui(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"👤 Profil: {member.display_name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 2. GİZLİ AVATAR KOMUTU ---
@bot.tree.command(name="avatar", description="Avatarı sadece sana özel gösterir")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"🖼️ {member.name} - Avatar")
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed, ephemeral=True)

# --- 3. GİZLİ SİLME KOMUTU ---
@bot.tree.command(name="sil", description="Belirtilen miktar kadar mesajı siler")
@app_commands.checks.has_permissions(manage_messages=True)
async def sil(interaction: discord.Interaction, miktar: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=miktar)
    await interaction.followup.send(f"🧹 **{len(deleted)}** mesaj temizlendi.", ephemeral=True)

# --- 4. GİZLİ DM KOMUTU ---
@bot.tree.command(name="dm", description="Bir kullanıcıya özel mesaj atar")
@app_commands.checks.has_permissions(administrator=True)
async def dm(interaction: discord.Interaction, member: discord.Member, mesaj: str):
    try:
        await member.send(f"📩 **Sunucudan Mesaj:** {mesaj}")
        await interaction.response.send_message(f"✅ Mesaj iletildi.", ephemeral=True)
        print(f"MESAJ GÖNDERİLDİ: {member.name} -> {mesaj}")
    except:
        await interaction.response.send_message("❌ DM kapalı.", ephemeral=True)

# --- TOKEN ÇALIŞTIRICI ---
# Buraya sakın şifreni yazma! Render panelinden 'DISCORD_TOKEN' adıyla ekleyeceğiz.
bot.run(os.getenv('DISCORD_TOKEN'))
