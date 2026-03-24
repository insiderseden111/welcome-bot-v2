import discord
from discord.ext import commands
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Flask Server (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "I'm alive!"
def run(): app.run(host='0.0.0.0', port=8080)
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

# --- Bot Setup ---
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_USERNAME = "eden_insiders_49810" # שם המשתמש שלך למענה

intents = discord.Intents.all() # וודאי שכל ה-Intents דלוקים בפורטל המפתחים
bot = commands.Bot(command_prefix='!', intents=intents)

# --- 1. מערכת ניהול הודעות (DM System) ---

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # אם מישהו שולח הודעה לבוט בפרטי (DM)
    if message.guild is None and message.author.name != TARGET_USERNAME:
        target_admin = discord.utils.get(bot.users, name=TARGET_USERNAME)
        if target_admin:
            embed = discord.Embed(
                title="📥 הודעה חדשה ממשתמש",
                description=message.content,
                color=discord.Color.blue()
            )
            embed.set_author(name=f"{message.author.display_name} (@{message.author.name})", icon_url=message.author.display_avatar.url)
            embed.set_footer(text=f"לענות לו? תעתיקי: !reply {message.author.id} ")
            
            # שליחה אלייך בצירוף קבצים אם שלח
            files = []
            if message.attachments:
                for att in message.attachments:
                    files.append(await att.to_file())
            
            await target_admin.send(embed=embed, files=files)

    await bot.process_commands(message)

# --- 2. פקודת המענה שלך (Reply Command) ---

@bot.command()
async def reply(ctx, user_id: int, *, content: str = ""):
    if ctx.author.name != TARGET_USERNAME:
        return

    try:
        user = await bot.fetch_user(user_id)
        if user:
            embed = discord.Embed(
                title="💬 מענה מצוות INSIDERS",
                description=content if content else "צירפנו קובץ עבורך:",
                color=discord.Color.green()
            )
            embed.set_footer(text="תוכל להשיב להודעה זו כדי להמשיך בשיחה.")
            
            file_to_send = None
            if ctx.message.attachments:
                file_to_send = await ctx.message.attachments[0].to_file()

            await user.send(embed=embed, file=file_to_send)
            await ctx.send(f"✅ שלחת תשובה ל-{user.display_name}!")
    except Exception as e:
        await ctx.send(f"❌ שגיאה: {e}")

# --- 3. תהליך הקליטה (Welcome View) ---

class WelcomeView(discord.ui.View):
    def __init__(self, bot, stage=1):
        super().__init__(timeout=None)
        self.bot = bot
        self.stage = stage
        self.create_buttons()

    def create_buttons(self):
        self.clear_items()
        
        btn1 = discord.ui.Button(label="🚨 דיסקליימר", style=discord.ButtonStyle.primary, custom_id="onboard_discl", row=0)
        btn1.callback = self.disclaimer_callback
        self.add_item(btn1)

        if self.stage >= 2:
            btn2 = discord.ui.Button(label="🧐 מה זה פה?", style=discord.ButtonStyle.primary, custom_id="onboard_what", row=0)
            btn2.callback = self.what_is_callback
            self.add_item(btn2)

        if self.stage >= 3:
            btn3 = discord.ui.Button(label="❗ חשוב לדעת", style=discord.ButtonStyle.primary, custom_id="onboard_important", row=0)
            btn3.callback = self.important_callback
            self.add_item(btn3)

        if self.stage >= 4:
            btn4 = discord.ui.Button(label="📊 עדכוני רמות והטבות", style=discord.ButtonStyle.primary, custom_id="onboard_levels", row=0)
            btn4.callback = self.levels_callback
            self.add_item(btn4)

    async def disclaimer_callback(self, interaction: discord.Interaction):
        full_text = (
            "התוכן נוצר מתוך אהבה לשוק ההון והאמונה שכולנו צריכים לייצר ערך כלכלי.\n\n"
            "📍 **אין לראות בנאמר המלצה או ייעוץ לביצוע השקעה מכל סוג שהוא.**\n\n"
            "📍 המפעילים **אינם בעלי רישיון לייעוץ השקעות**.\n\n"
            "📍 כל השקעה שתבוצע היא על פי שיקול דעתכם הבלעדי."
        )
        embed = discord.Embed(title="🚨 דיסקליימר ותנאי שימוש", color=discord.Color.blue(), description=full_text)
        
        confirm_view = discord.ui.View(timeout=None)
        confirm_btn = discord.ui.Button(label="הבנתי ואני מאשר ✅", style=discord.ButtonStyle.success)
        
        async def confirm_action(itn: discord.Interaction):
            await itn.response.defer()
            self.stage = 2; self.create_buttons(); add_user_to_db(itn.user.id)
            log_c = discord.utils.get(itn.guild.channels, name="אישורי-דיסקליימר")
            if log_c: await log_c.send(f"✅ **{itn.user.name}** אישר את הדיסקליימר.")
            
            new_embed = discord.Embed(title="🧐 מה זה פה?", color=discord.Color.blue(), 
                                    description="ברוכים הבאים ל-INSIDERS!\n\n**סרטון הסבר:**\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ")
            await itn.edit_original_response(content="✅ אישרת את התנאים!", embed=new_embed, view=self)

        confirm_btn.callback = confirm_action
        confirm_view.add_item(confirm_btn)
        await interaction.response.edit_message(embed=embed, view=confirm_view)

    async def what_is_callback(self, itn):
        embed = discord.Embed(title="🧐 מה זה פה?", color=discord.Color.blue(), 
                            description="ברוכים הבאים ל-INSIDERS!\n\n**סרטון הסבר:**\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.stage = max(self.stage, 3); self.create_buttons()
        await itn.response.edit_message(content="מעולה! בוא נמשיך:", embed=embed, view=self)

    async def important_callback(self, itn):
        safety_text = (
            "📢 **לתשומת לבכם**\n\n🛑 אנחנו לעולם לא נפנה אליכם בפרטי ונציע לכם להשקיע עבורכם.\n\n"
            "⚠️ אם פונים אליכם בפרטי - **מדובר במתחזה!**\n\n📢 **ויש לדווח על המשתמש שפנה אליכם.**"
        )
        embed = discord.Embed(title="❗ חשוב לדעת - כללי בטיחות", color=discord.Color.red(), description=safety_text)
        self.stage = max(self.stage, 4); self.create_buttons()
        await itn.response.edit_message(content="בטיחות מעל הכל!", embed=embed, view=self)

    async def levels_callback(self, itn: discord.Interaction):
        levels_text = (
            "**🎁 סולם ההטבות שלכם:**\n"
            "🔹 **רמה 10:** תג **Insiders Active**.\n"
            "🔹 **רמה 15:** מפגש זום אישי (45 דק') עם מנטור.\n"
            "🔹 **רמה 20:** פתיחת גישה לערוץ ניתוחים מיוחד.\n"
            "🔹 **רמה 25:** פגישת זום אישית מורחבת (שעה שלמה).\n"
            "🔹 **רמה 30:** הנחה של 15% לכל הקורסים והסדנאות.\n"
            "🔹 **רמה 50:** כניסה לקבוצת ה-VIP של הנבחרת!\n\n"
            "**איך עולים?** משתפים גרפים, מעלים עסקאות ועוזרים לאחרים!"
        )
        embed = discord.Embed(title="📊 עדכוני רמות והטבות", color=discord.Color.blue(), description=levels_text)
        
        try:
            dm_embed = discord.Embed(
                title="ברוך הבא למשפחת INSIDERS! 🚀",
                description=f"היי {itn.user.display_name}, אנחנו שמחים שאתה איתנו!\nאנחנו כאן לכל שאלה, עזרה או התייעצות. **אתה יכול להשיב להודעה הזו בכל זמן!**",
                color=discord.Color.green()
            )
            await itn.user.send(embed=dm_embed)
            extra = "שלחנו לך הודעה בפרטי! 📥"
        except: extra = "סיימת את תהליך הקליטה!"

        await itn.response.edit_message(content=extra, embed=embed, view=self)

# --- 4. Main Commands ---

@bot.event
async def on_ready(): print(f'System: {bot.user} is online!')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    try: await ctx.message.delete() # מוחק את ה-!setup כדי לשמור על סדר
    except: pass
    
    embed = discord.Embed(title="ברוכים הבאים לקהילת INSIDERS! 🚀", color=discord.Color.blue())
    embed.set_image(url="https://i.ibb.co/v4m86fP/robot-insiders.png") 
    await ctx.send(embed=embed, view=WelcomeView(bot))

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
