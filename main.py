import discord
from discord.ext import commands
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Flask Server (Render Fix) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Supabase ---
load_dotenv()
url = os.getenv("SUPABASE_URL") 
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key) if url and key else None

def add_user_to_db(user_id):
    if supabase:
        try:
            supabase.table("completed_users").upsert({"user_id": str(user_id)}).execute()
        except Exception as e: print(f"DB Error: {e}")

# --- Bot Config ---
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_USERNAME = "eden_insiders_49810" 
MAIN_BLUE = 0x0080e8 

intents = discord.Intents.all() 
bot = commands.Bot(command_prefix='!', intents=intents)

# --- 1. מערכת הודעות פרטיות ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if message.guild is None and message.author.name != TARGET_USERNAME:
        target_admin = discord.utils.get(bot.users, name=TARGET_USERNAME)
        if target_admin:
            embed = discord.Embed(title="📥 הודעה חדשה ממשתמש", description=message.content, color=MAIN_BLUE)
            embed.set_author(name=f"{message.author.display_name}", icon_url=message.author.display_avatar.url)
            embed.set_footer(text=f"לענות לו? !reply {message.author.id} ")
            files = [await att.to_file() for att in message.attachments]
            await target_admin.send(embed=embed, files=files)
    await bot.process_commands(message)

@bot.command()
async def reply(ctx, user_id: int, *, content: str = ""):
    if ctx.author.name != TARGET_USERNAME: return
    try:
        user = await bot.fetch_user(user_id)
        if user:
            embed = discord.Embed(title="💬 מענה מצוות INSIDERS", description=content, color=0x004daa)
            file = await ctx.message.attachments[0].to_file() if ctx.message.attachments else None
            await user.send(embed=embed, file=file)
            await ctx.send(f"✅ נשלח ל-{user.display_name}!")
    except Exception as e: await ctx.send(f"❌ שגיאה: {e}")

# --- 2. תהליך הקליטה (Welcome View) ---
class WelcomeView(discord.ui.View):
    def __init__(self, bot, stage=1):
        super().__init__(timeout=None)
        self.bot, self.stage = bot, stage
        self.create_buttons()

    def create_buttons(self):
        self.clear_items()
        # הוספת custom_id חדש לגמרי כדי לרענן את המערכת
        btn1 = discord.ui.Button(label="🚨 דיסקליימר", style=discord.ButtonStyle.primary, custom_id="v4_discl", row=0)
        btn1.callback = self.disclaimer_callback
        self.add_item(btn1)
        if self.stage >= 2:
            btn2 = discord.ui.Button(label="🧐 מה זה פה?", style=discord.ButtonStyle.primary, custom_id="v4_what", row=0)
            btn2.callback = self.what_is_callback
            self.add_item(btn2)
        if self.stage >= 3:
            btn3 = discord.ui.Button(label="❗ חשוב לדעת", style=discord.ButtonStyle.primary, custom_id="v4_imp", row=0)
            btn3.callback = self.important_callback
            self.add_item(btn3)
        if self.stage >= 4:
            btn4 = discord.ui.Button(label="📊 עדכוני רמות והטבות", style=discord.ButtonStyle.primary, custom_id="v4_lev", row=0)
            btn4.callback = self.levels_callback
            self.add_item(btn4)

    async def disclaimer_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True) # מונע את השגיאה האדומה
        full_text = "📍 **אין לראות בנאמר המלצה או ייעוץ.**\n📍 המפעילים **אינם בעלי רישיון לייעוץ השקעות**."
        embed = discord.Embed(title="🚨 דיסקליימר ותנאי שימוש", color=MAIN_BLUE, description=full_text)
        confirm_view = discord.ui.View(timeout=None)
        btn = discord.ui.Button(label="הבנתי ואני מאשר ✅", style=discord.ButtonStyle.success, custom_id="v4_confirm")
        async def confirm_action(itn):
            await itn.response.defer()
            self.stage = 2; self.create_buttons(); add_user_to_db(itn.user.id)
            await itn.edit_original_response(content="✅ אישרת את התנאים!", view=self)
        btn.callback = confirm_action
        confirm_view.add_item(btn)
        await interaction.followup.edit_message(message_id=interaction.message.id, embed=embed, view=confirm_view)

    async def what_is_callback(self, itn):
        await itn.response.defer()
        embed = discord.Embed(title="🧐 מה זה פה?", color=MAIN_BLUE, description="ברוכים הבאים ל-INSIDERS!\n\n**סרטון הסבר:**\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.stage = max(self.stage, 3); self.create_buttons()
        await itn.edit_original_response(content="מעולה! בוא נמשיך:", embed=embed, view=self)

    async def important_callback(self, itn):
        await itn.response.defer()
        txt = "🛑 אנחנו לעולם לא נפנה אליכם בפרטי.\n⚠️ אם פונים - **מדובר במתחזה!**"
        embed = discord.Embed(title="❗ חשוב לדעת", color=discord.Color.red(), description=txt)
        self.stage = max(self.stage, 4); self.create_buttons()
        await itn.edit_original_response(content="בטיחות מעל הכל!", embed=embed, view=self)

    async def levels_callback(self, itn):
        await itn.response.defer() # השורה הקריטית שמונעת את השגיאה בכפתור האחרון
        levels_text = (
            "**🎁 סולם ההטבות שלכם:**\n"
            "🔹 **רמה 10:** תג **Insiders Active**.\n"
            "🔹 **רמה 15:** מפגש זום אישי (45 דק').\n"
            "🔹 **רמה 20:** גישה לערוץ ניתוחים.\n"
            "🔹 **רמה 25:** פגישת זום מורחבת (שעה).\n"
            "🔹 **רמה 30:** הנחה של 15% לקורסים.\n"
            "🔹 **רמה 50:** כניסה ל-VIP!"
        )
        embed = discord.Embed(title="📊 עדכוני רמות והטבות", color=MAIN_BLUE, description=levels_text)
        try:
            await itn.user.send(embed=discord.Embed(title="ברוך הבא! 🚀", description="שמחים שאתה כאן. מוזמן להשיב להודעה זו בכל שאלה.", color=MAIN_BLUE))
        except: pass
        await itn.edit_original_response(content="סיימת את תהליך הקליטה! 📥", embed=embed, view=self)

@bot.event
async def on_ready(): print(f'System: {bot.user} is online!')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(title="ברוכים הבאים לקהילת INSIDERS! 🚀", color=MAIN_BLUE)
    embed.set_image(url="https://i.ibb.co/v4m86fP/robot-insiders.png") 
    await ctx.send(embed=embed, view=WelcomeView(bot))

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
