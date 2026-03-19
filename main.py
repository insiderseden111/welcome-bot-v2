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

# ה-ID של ערוץ דיווחי המנהלים שלך
ADMIN_CHANNEL_ID = 1484206445128974479 

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class WelcomeView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def update_message(self, interaction, content, view=None):
        if view is None: view = self
        await interaction.response.edit_message(content=content, view=view)

    @discord.ui.button(label="🚨 דיסקליימר", style=discord.ButtonStyle.primary, custom_id="p_disclaimer", row=0)
    async def disclaimer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**אהלן כולם 👋**\n\n"
            "התוכן נוצר מתוך אהבה לשוק ההון והאמונה שכולנו, בלי יוצא מהכלל, צריכים להשתמש בו למטרה שלשמה הוא נועד - להשקיע את הכסף שלנו כדי לייצר ערך כלכלי.\n\n"
            "יחד עם זאת - מסחר בשוק ההון כרוך בסיכונים ועשוי לגרום להפסד כספי משמעותי ולכן:\n\n"
            "• **אין לראות בנאמר בקבוצה / קהילה המלצה או ייעוץ לביצוע השקעה מכל סוג שהוא.**\n\n"
            "• כל פרסום באשר הוא בקבוצה / קהילה, לרבות בפוסטים, דיונים, תגובות, לייבים, פודקאסטים וכדומה, מצד בעלי הקבוצה / קהילה ו/או מנהליה ו/או חבריה אינו מהווה ייעוץ או שידול להשקעה באשר היא, ואינו מתיימר להוות תחליף לייעוץ ו/או שיווק ו/או ניהול תיקי השקעות המתחשבים בנתונים ובצרכים המיוחדים של אדם מסוים.\n\n"
            "• הצטרפותך מהווה אישור לכך שידוע לך כי החברה ו/או נציגיה המפעילים את הקבוצה / קהילה - אינם בעלי רישיון לייעוץ ו/או שיווק ו/או ניהול תיקי השקעות ואינם מספקים שירותי ייעוץ ו/או שיווק השקעות כהגדרתם בחוק.\n\n"
            "• כל משתתפ/ת מסכימ/ה בזאת שלא לבצע כל השקעה הקשורה בפרסומים המופיעים בקבוצה / קהילה ואם החליט/ה לבצע השקעה, הרי ביצע/ה אותה לפי שיקול דעתו/ה הבלעדי."
        )
        confirm_view = discord.ui.View(timeout=None)
        confirm_btn = discord.ui.Button(label="הבנתי ✅", style=discord.ButtonStyle.success, custom_id="p_confirm_disclaimer")
        
        async def confirm_callback(itn):
            admin_channel = self.bot.get_channel(ADMIN_CHANNEL_ID)
            if admin_channel:
                await admin_channel.send(f"✅ המשתמש **{itn.user}** (ID: {itn.user.id}) אישר את הדיסקליימר.")
            await itn.response.edit_message(content="אישרת את הדיסקליימר. ברוך הבא לקהילה! ✅", view=self)

        confirm_btn.callback = confirm_callback
        confirm_view.add_item(confirm_btn)
        await interaction.response.edit_message(content=content, view=confirm_view)

    @discord.ui.button(label="🧐 מה זה פה?", style=discord.ButtonStyle.primary, custom_id="p_whatis", row=1)
    async def what_is_this(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**ברוכים הבאים לקהילת המסחר המובילה בישראל!** 🇮🇱\n\n"
            "זמנים לשאול כאן כל שאלה שיש לכם על התמצאות בשרת הקהילה שלנו (איפה מעלים ניתוחים של עסקאות, איפה מפרסמים מניות מעניינות ועוד).\n\n"
            "**לינק הסבר על הקהילה:**\n"
            "https://youtube.com/your-link-here"
        )
        await self.update_message(interaction, content)

    @discord.ui.button(label="❗ חשוב לדעת", style=discord.ButtonStyle.primary, custom_id="p_important", row=2)
    async def important_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "⚠️ **לתשומת לבכם**\n\n"
            "אנחנו לעולם לא נפנה אליכם בפרטי ונציע לכם להשקיע ו/או שאנחנו נשקיע עבורכם.\n\n"
            "לצערנו קרו בעבר מקרים בהם נוכלים פתחו משתמשים עם תמונות ושמות דומים לשלנו. "
            "אם פונים אליכם בפרטי עם הצעה - **מדובר במתחזה** ויש לדווח עליו מיד!"
        )
        await self.update_message(interaction, content)

    @discord.ui.button(label="📊 רמות יומיות ועדכונים", style=discord.ButtonStyle.primary, custom_id="p_levels", row=3)
    async def levels_updates(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "📈 **רמות יומיות ועדכונים שוטפים מהשוק**\n\n"
            "כאן יפורסמו רמות עבודה, ניתוחים טכניים ועדכונים חמים על מניות ומדדים בזמן אמת."
        )
        await self.update_message(interaction, content)

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    bot.add_view(WelcomeView(bot))
    print(f'System: {bot.user} is online.')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    # מחיקת הודעת ה-!setup של המשתמש כדי למנוע כפילות בערוץ
    try:
        await ctx.message.delete()
    except:
        pass

    image_url = "https://i.ibb.co/v4m86fP/robot-insiders.png" 
    
    embed = discord.Embed(
        title="ברוכים הבאים לקהילת INSIDERS! 🚀",
        color=discord.Color.blue()
    )
    embed.set_image(url=image_url)
    
    await ctx.send(embed=embed, view=WelcomeView(bot))

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
