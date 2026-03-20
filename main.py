import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Flask Server for Render ---
app = Flask('')
@app.route('/')
def home(): return "I'm alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Bot Setup ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_CHANNEL_ID = 1484206445128974479 

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# רשימה לשמירת המשתמשים שסיימו את התהליך (נשמר כל עוד הבוט רץ)
completed_users = set()

class WelcomeView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def get_user_stage(self, user_id):
        # אם המשתמש כבר סיים פעם אחת, הוא מקבל גישה להכל (שלב 4)
        if user_id in completed_users:
            return 4
        return 1

    def create_buttons(self, stage):
        self.clear_items()
        
        # כפתור 1 תמיד מופיע
        btn1 = discord.ui.Button(label="🚨 דיסקליימר", style=discord.ButtonStyle.primary, custom_id="p_discl", row=0)
        btn1.callback = self.disclaimer_callback
        self.add_item(btn1)

        # כפתור 2 מופיע אם המשתמש עבר את שלב 1 או סיים הכל
        if stage >= 2:
            btn2 = discord.ui.Button(label="🧐 מה זה פה?", style=discord.ButtonStyle.primary, custom_id="p_what", row=1)
            btn2.callback = self.what_is_callback
            self.add_item(btn2)

        if stage >= 3:
            btn3 = discord.ui.Button(label="❗ חשוב לדעת", style=discord.ButtonStyle.primary, custom_id="p_import", row=2)
            btn3.callback = self.important_callback
            self.add_item(btn3)

        if stage >= 4:
            btn4 = discord.ui.Button(label="📊 רמות יומיות ועדכונים", style=discord.ButtonStyle.primary, custom_id="p_levels", row=3)
            btn4.callback = self.levels_callback
            self.add_item(btn4)

    async def disclaimer_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🚨 דיסקליימר", color=discord.Color.blue(), description=(
            "**אהלן כולם 👋**\n\n"
            "התוכן נוצר מתוך אהבה לשוק ההון והאמונה שכולנו צריכים להשתמש בו למטרה שלשמה הוא נועד.\n\n"
            "• **אין לראות בנאמר המלצה או ייעוץ להשקעה.**\n"
            "• כל פרסום אינו מהווה תחליף לייעוץ המתחשב בצרכים אישיים.\n"
            "• המפעילים אינם בעלי רישיון לייעוץ/שיווק השקעות.\n"
            "• כל החלטת השקעה היא על אחריות המשתמש בלבד."
        ))
        
        # אם המשתמש כבר סיים בעבר, לא צריך כפתור אישור מיוחד
        if interaction.user.id in completed_users:
            await interaction.response.edit_message(embed=embed, view=self)
            return

        confirm_view = discord.ui.View(timeout=None)
        confirm_btn = discord.ui.Button(label="הבנתי ✅", style=discord.ButtonStyle.success)
        
        async def confirm(itn):
            admin_ch = self.bot.get_channel(ADMIN_CHANNEL_ID)
            if admin_ch: await admin_ch.send(f"✅ המשתמש **{itn.user}** אישר את הדיסקליימר.")
            
            # מעדכנים את התצוגה לשלב 2 עבור המשתמש הזה
            self.create_buttons(stage=2)
            await itn.response.edit_message(content="✅ אישרת! עכשיו ניתן להמשיך ל: **מה זה פה?**", embed=None, view=self)
            
        confirm_btn.callback = confirm
        confirm_view.add_item(confirm_btn)
        await interaction.response.edit_message(embed=embed, view=confirm_view)

    async def what_is_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🧐 מה זה פה?", color=discord.Color.blue(), description=(
            "**ברוכים הבאים לקהילת המסחר המובילה בישראל!** 🇮🇱\n\n"
            "זמנים לשאול כאן כל שאלה שיש לכם על התמצאות בשרת (איפה מעלים ניתוחים, מניות מעניינות ועוד).\n\n"
            "**לינק הסבר על הקהילה:**\n[לחצו כאן לצפייה](https://youtube.com/your-link-here)"
        ))
        stage = 4 if interaction.user.id in completed_users else 3
        self.create_buttons(stage=stage)
        await interaction.response.edit_message(embed=embed, view=self)

    async def important_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="❗ חשוב לדעת", color=discord.Color.red(), description=(
            "**לתשומת לבכם**\n\n"
            "אנחנו לעולם לא נפנה אליכם בפרטי ונציע לכם להשקיע עבורכם.\n\n"
            "אם פונים אליכם בפרטי עם הצעה - **מדובר במתחזה** ויש לדווח עליו מיד!"
        ))
        stage = 4 # בשלב הזה המשתמש מגיע לסוף
        completed_users.add(interaction.user.id) # שומרים שסיים הכל
        self.create_buttons(stage=stage)
        await interaction.response.edit_message(embed=embed, view=self)

    async def levels_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📊 רמות יומיות ועדכונים", color=discord.Color.green(), description=(
            "📈 **רמות יומיות ועדכונים שוטפים מהשוק**\n\n"
            "כאן יפורסמו רמות עבודה ועדכונים חמים בזמן אמת.\n\n"
            "**תהליך ההיכרות הסתיים. כל הכפתורים פתוחים עבורך כעת.**"
        ))
        self.create_buttons(stage=4)
        await interaction.response.edit_message(embed=embed, view=self)

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    bot.add_view(WelcomeView(bot))
    print(f'System: {bot.user} is online.')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    try: await ctx.message.delete()
    except: pass

    image_url = "https://i.ibb.co/v4m86fP/robot-insiders.png" 
    embed = discord.Embed(title="ברוכים הבאים לקהילת INSIDERS! 🚀", color=discord.Color.blue())
    embed.set_image(url=image_url)
    
    view = WelcomeView(bot)
    view.create_buttons(stage=1) # מתחילים משלב 1 לכולם בהודעה הראשונית
    await ctx.send(embed=embed, view=view)

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
