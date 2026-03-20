import discord
from discord.ext import commands
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Flask Server (Render Keep-Alive) ---
app = Flask('')
@app.route('/')
def home(): return "I'm alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Supabase Configuration ---
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def add_user_to_db(user_id):
    supabase.table("completed_users").upsert({"user_id": user_id}).execute()

def is_user_completed(user_id):
    try:
        response = supabase.table("completed_users").select("*").eq("user_id", user_id).execute()
        return len(response.data) > 0
    except:
        return False

# --- Bot Setup ---
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class WelcomeView(discord.ui.View):
    def __init__(self, bot, user_id=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.stage = 4 if user_id and is_user_completed(user_id) else 1
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        
        # שלב 1
        btn1 = discord.ui.Button(label="🚨 דיסקליימר משפטי", style=discord.ButtonStyle.primary, custom_id="p_discl", row=0)
        btn1.callback = self.disclaimer_callback
        self.add_item(btn1)

        # שלב 2
        if self.stage >= 2:
            btn2 = discord.ui.Button(label="🧐 מה זה פה?", style=discord.ButtonStyle.primary, custom_id="p_what", row=1)
            btn2.callback = self.what_is_callback
            self.add_item(btn2)

        # שלב 3
        if self.stage >= 3:
            btn3 = discord.ui.Button(label="❗ חשוב לדעת", style=discord.ButtonStyle.primary, custom_id="p_important", row=2)
            btn3.callback = self.important_callback
            self.add_item(btn3)

        # שלב 4 - שם מעודכן
        if self.stage >= 4:
            btn4 = discord.ui.Button(label="📊 עדכוני רמות והטבות", style=discord.ButtonStyle.primary, custom_id="p_levels", row=3)
            btn4.callback = self.levels_callback
            self.add_item(btn4)

    async def disclaimer_callback(self, interaction: discord.Interaction):
        full_text = (
            "התוכן נוצר מתוך אהבה לשוק ההון והאמונה שכולנו, בלי יוצא מהכלל, צריכים להשתמש בו למטרה שלשמה הוא נועד - להשקיע את הכסף שלנו כדי לייצר ערך כלכלי.\n\n"
            "יחד עם זאת - מסחר בשוק ההון כרוך בסיכונים ועשוי לגרום להפסד כספי משמעותי ולכן:\n\n"
            "📍 **אין לראות בנאמר בקבוצה / קהילה המלצה או ייעוץ לביצוע השקעה מכל סוג שהוא.**\n\n"
            "📍 כל פרסום באשר הוא בקבוצה / קהילה, לרבות בפוסטים ודיונים, מצד בעלי הקהילה ו/או מנהליה **אינו מהווה ייעוץ או שידול להשקעה**.\n\n"
            "📍 המפעילים **אינם בעלי רישיון לייעוץ השקעות** ואינם מספקים שירותי ייעוץ.\n\n"
            "📍 כל משתתפ/ת מסכימ/ה שלא לבצע השקעה הקשורה בפרסומים המופיעים כאן, ואם החליט/ה לבצע השקעה - הרי שביצע/ה אותה לפי שיקול דעתו/ה הבלעדי."
        )
        embed = discord.Embed(title="🚨 דיסקליימר משפטי ותנאי שימוש", color=discord.Color.blue(), description=full_text)
        
        if is_user_completed(interaction.user.id):
            await interaction.response.edit_message(embed=embed, view=self)
            return

        confirm_view = discord.ui.View(timeout=None)
        confirm_btn = discord.ui.Button(label="הבנתי ואני מאשר ✅", style=discord.ButtonStyle.success)
        
        async def confirm(itn):
            self.stage = 2
            self.update_buttons()
            new_embed = discord.Embed(
                title="🧐 מה זה פה?", 
                color=discord.Color.blue(),
                description="ברוכים הבאים ל-INSIDERS! כאן אנחנו לומדים, מנתחים וצומחים יחד.\n\n**צפו בסרטון ההסבר שלנו:**\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )
            # כאן מופיעה הודעת הטקסט שציינת
            await itn.response.edit_message(content="✅ אישרת את התנאים! כעת נפתח לך השלב הבא:", embed=new_embed, view=self)
            
        confirm_btn.callback = confirm
        confirm_view.add_item(confirm_btn)
        await interaction.response.edit_message(embed=embed, view=confirm_view)

    async def what_is_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🧐 מה זה פה?", 
            color=discord.Color.blue(), 
            description="ברוכים הבאים ל-INSIDERS! כאן אנחנו לומדים, מנתחים וצומחים יחד.\n\n**צפו בסרטון ההסבר שלנו:**\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        self.stage = max(self.stage, 3)
        self.update_buttons()
        # כאן ובהמשך - אין הודעת טקסט נוספת, רק עדכון הריבוע
        await interaction.response.edit_message(content=None, embed=embed, view=self)

    async def important_callback(self, interaction: discord.Interaction):
        safety_text = (
            "📢 **לתשומת לבכם**\n\n"
            "🛑 אנחנו לעולם לא נפנה אליכם בפרטי ונציע לכם להשקיע ו/או שאנחנו נשקיע עבורכם.\n\n"
            "👤 לצערנו קרו בעבר מקרים בהם נוכלים פתחו משתמשים עם תמונות ושמות דומים לשלנו והציעו כל מיני דברים לחברים חדשים.\n\n"
            "⚠️ לכן, אם פונים אליכם בפרטי עם הצעה - **מדובר במתחזה!**\n\n"
            "✅ יש לדווח מיד על המשתמש שפנה אליכם ועל ההודעה כדי שנוכל להסיר אותו מהשרת."
        )
        embed = discord.Embed(title="❗ חשוב לדעת - כללי בטיחות", color=discord.Color.red(), description=safety_text)
        add_user_to_db(interaction.user.id)
        self.stage = 4
        self.update_buttons()
        await interaction.response.edit_message(content=None, embed=embed, view=self)

    async def levels_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📊 עדכוני רמות והטבות", 
            color=discord.Color.gold(), 
            description="כאן מפורסמים ניתוחי שוק, רמות עבודה יומיות, הטבות ועדכונים בזמן אמת.\n\n**ברוכים הבאים לקהילה! 🚀**"
        )
        self.stage = 4
        self.update_buttons()
        await interaction.response.edit_message(content=None, embed=embed, view=self)

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
    await ctx.send(embed=embed, view=WelcomeView(bot, user_id=ctx.author.id))

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
