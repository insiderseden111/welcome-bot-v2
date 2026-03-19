import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# טעינת המשתנים מקובץ ה-.env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# הגדרות הרשאות
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # התפריט יישאר פעיל תמיד

    async def update_message(self, interaction, content, view=None):
        if view is None:
            view = self
        await interaction.response.edit_message(content=content, view=view)

    @discord.ui.button(label="דיסקליימר", style=discord.ButtonStyle.secondary)
    async def disclaimer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**אהלן כולם** 👋\n\n"
            "התוכן נוצר מתוך אהבה לשוק ההון והאמונה שכולנו, בלי יוצא מהכלל, צריכים להשתמש בו למטרה שלשמה הוא נועד - להשקיע את הכסף שלנו כדי לייצר ערך כלכלי.\n\n"
            "יחד עם זאת - מסחר בשוק ההון כרוך בסיכונים ועשוי לגרום להפסד כספי משמעותי ולכן:\n\n"
            "• **אין לראות בנאמר בקבוצה / קהילה המלצה או ייעוץ לביצוע השקעה מכל סוג שהוא.**\n\n"
            "כל פרסום באשר הוא בקבוצה / קהילה, לרבות בפוסטים, דיונים, תגובות, לייבים, פודקאסטים וכדומה, מצד בעלי הקבוצה / קהילה ו/או מנהליה ו/או חבריה אינו מהווה ייעוץ או שידול להשקעה באשר היא, ואינו מתיימר להוות תחליף לייעוץ ו/או שיווק ו/או ניהול תיקי השקעות המתחשבים בנתונים ובצרכים המיוחדים של אדם מסוים.\n\n"
            "הצטרפותך מהווה אישור לכך שידוע לך כי החברה ו/או נציגיה המפעילים את הקבוצה / קהילה - אינם בעלי רישיון לייעוץ ו/או שיווק ו/או ניהול תיקי השקעות ואינם מספקים שירותי ייעוץ ו/או שיווק השקעות כהגדרתם בחוק הסדרת העיסוק בייעוץ השקעות, שיווק השקעות וניהול תיקי השקעות, תשנ\"ה - 1995.\n\n"
            "כל משתתפ/ת מסכימ/ה בזאת שלא לבצע כל השקעה הקשורה בפרסומים המופיעים בקבוצה / קהילה ואם החליט/ה לבצע השקעה, הרי ביצע/ה אותה לפי שיקול דעתו/ה הבלעדי."
        )
        
        # יצירת תצוגה זמנית עם כפתור "הבנתי"
        confirm_view = discord.ui.View()
        confirm_btn = discord.ui.Button(label="הבנתי", style=discord.ButtonStyle.secondary)
        
        async def confirm_callback(itn):
            # מנטרל את כפתור הדיסקליימר המקורי
            button.disabled = True
            await itn.response.edit_message(content="אישרת את הדיסקליימר. ברוך הבא לקהילה! ✅", view=self)

        confirm_btn.callback = confirm_callback
        confirm_view.add_item(confirm_btn)
        
        await interaction.response.edit_message(content=content, view=confirm_view)

    @discord.ui.button(label="מה זה פה?", style=discord.ButtonStyle.secondary)
    async def what_is_this(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**מה זה פה?**\n"
            "כאן אנחנו מסבירים בקצרה על מהות הקהילה ואיך הכל עובד.\n\n"
            "צפו בסרטון ההסבר הבא מיוטיוב:\n"
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # החליפי בקישור האמיתי שלך
        )
        await self.update_message(interaction, content)

    @discord.ui.button(label="חשוב לדעת", style=discord.ButtonStyle.secondary)
    async def important_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**לתשומת לבכם** ❗\n\n"
            "אנחנו לעולם לא נפנה אליכם בפרטי ונציע לכם להשקיע ו/או שאנחנו נשקיע עבורכם.\n\n"
            "לצערנו קרו בעבר מקרים בהם נוכלים פתחו משתמשים עם תמונות ושמות דומים לשלנו והציעו כל מיני דברים לחברים חדשים.\n\n"
            "לכן, אם פונים אליכם בפרטי עם הצעה - **מדובר במתחזה** ויש לדווח על המשתמש שפנה אליכם ועל ההודעה 📢"
        )
        
        temp_view = discord.ui.View()
        thanks_btn = discord.ui.Button(label="הבנתי תודה!", style=discord.ButtonStyle.secondary)
        
        async def thanks_callback(itn):
            await itn.response.edit_message(content="תודה על תשומת הלב. השתמשו בכפתורים כדי להמשיך.", view=self)
            
        thanks_btn.callback = thanks_callback
        temp_view.add_item(thanks_btn)
        
        await interaction.response.edit_message(content=content, view=temp_view)

    @discord.ui.button(label="רמות יומיות ועדכונים", style=discord.ButtonStyle.secondary)
    async def levels_updates(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**רמות יומיות ועדכונים** 📈\n\n"
            "כאן יופיע פירוט על הרמות היומיות שלנו ועדכונים שוטפים מהשוק.\n"
            "(הטקסט המלא יעודכן בקרוב...)"
        )
        await self.update_message(interaction, content)

@bot.command()
async def setup(ctx):
    # פקודה להצבת התפריט בערוץ
    welcome_msg = "ברוך הבא לקהילה שלנו! 🚀\nאנא קראו את המידע בכפתורים למטה כדי להתחיל."
    await ctx.send(welcome_msg, view=WelcomeView())

@bot.event
async def on_ready():
    print(f'הבוט {bot.user} עלה לאוויר ומחובר בהצלחה!')

# הרצת הבוט עם הטוקן מה-.env
if TOKEN:
    bot.run(TOKEN)
else:
    print("שגיאה: לא נמצא טוקן בקובץ ה-.env!")