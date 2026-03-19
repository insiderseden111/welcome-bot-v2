import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# טעינת המשתנים מקובץ ה-.env (עבור VS Code)
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# הגדרות הרשאות (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# יצירת מחלקת ה-View עבור הכפתורים
class WelcomeView(discord.ui.View):
    def __init__(self):
        # timeout=None בשילוב עם bot.add_view גורם לכפתורים לעבוד לנצח
        super().__init__(timeout=None)

    async def update_message(self, interaction, content, view=None):
        if view is None:
            view = self
        await interaction.response.edit_message(content=content, view=view)

    @discord.ui.button(label="דיסקליימר", style=discord.ButtonStyle.secondary, custom_id="persistent_view:disclaimer")
    async def disclaimer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**אהלן כולם** 👋\n\n"
            "התוכן נוצר מתוך אהבה לשוק ההון והאמונה שכולנו צריכים להשתמש בו למטרה שלשמה הוא נועד - לייצר ערך כלכלי.\n\n"
            "יחד עם זאת - מסחר בשוק ההון כרוך בסיכונים ולכן:\n\n"
            "• **אין לראות בנאמר בקבוצה המלצה או ייעוץ לביצוע השקעה מכל סוג שהוא.**\n\n"
            "כל פרסום מצד בעלי הקבוצה ו/או מנהליה אינו מהווה ייעוץ המתחשב בנתונים ובצרכים המיוחדים של אדם מסוים.\n\n"
            "הצטרפותך מהווה אישור לכך שידוע לך כי המפעילים אינם בעלי רישיון לייעוץ ו/או ניהול תיקי השקעות ע\"פ החוק.\n\n"
            "כל משתתפ/ת מסכימ/ה שלא לבצע השקעה הקשורה בפרסומים כאן, ואם החליט/ה לבצע - זו אחריותו/ה הבלעדית."
        )
        
        confirm_view = discord.ui.View()
        confirm_btn = discord.ui.Button(label="הבנתי", style=discord.ButtonStyle.secondary)
        
        async def confirm_callback(itn):
            await itn.response.edit_message(content="אישרת את הדיסקליימר. ברוך הבא לקהילה! ✅", view=self)

        confirm_btn.callback = confirm_callback
        confirm_view.add_item(confirm_btn)
        await interaction.response.edit_message(content=content, view=confirm_view)

    @discord.ui.button(label="מה זה פה?", style=discord.ButtonStyle.secondary, custom_id="persistent_view:what_is")
    async def what_is_this(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**מה זה פה?**\n"
            "כאן אנחנו מסבירים בקצרה על מהות הקהילה ואיך הכל עובד.\n\n"
            "צפו בסרטון ההסבר הבא מיוטיוב:\n"
            "https://www.youtube.com/watch?v=YOUR_VIDEO_ID" # <--- שמי כאן את הלינק שלך
        )
        await self.update_message(interaction, content)

    @discord.ui.button(label="חשוב לדעת", style=discord.ButtonStyle.secondary, custom_id="persistent_view:important")
    async def important_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**לתשומת לבכם** ❗\n\n"
            "אנחנו לעולם לא נפנה אליכם בפרטי ונציע לכם להשקיע עבורכם.\n\n"
            "אם פנו אליכם בפרטי עם הצעה כספית - **מדובר במתחזה** ויש לדווח על כך מיד! 📢"
        )
        temp_view = discord.ui.View()
        thanks_btn = discord.ui.Button(label="הבנתי תודה!", style=discord.ButtonStyle.secondary)
        
        async def thanks_callback(itn):
            await itn.response.edit_message(content="תודה על תשומת הלב. השתמשו בכפתורים כדי להמשיך.", view=self)
            
        thanks_btn.callback = thanks_callback
        temp_view.add_item(thanks_btn)
        await interaction.response.edit_message(content=content, view=temp_view)

    @discord.ui.button(label="רמות יומיות ועדכונים", style=discord.ButtonStyle.secondary, custom_id="persistent_view:levels")
    async def levels_updates(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = (
            "**רמות יומיות ועדכונים** 📈\n\n"
            "כאן יופיע פירוט על הרמות היומיות ועדכונים שוטפים מהשוק.\n"
            "(הטקסט יעודכן כאן בהמשך)"
        )
        await self.update_message(interaction, content)

# הגדרת הבוט
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    # רישום ה-View כך שיהיה פעיל תמיד, גם אחרי הפעלה מחדש
    bot.add_view(WelcomeView())
    print(f'הבוט {bot.user} עלה לאוויר ומחובר בהצלחה!')

@bot.command()
async def setup(ctx):
    # פקודה להצבת התפריט בערוץ
    welcome_msg = "ברוך הבא לקהילה שלנו! 🚀\nאנא קראו את המידע בכפתורים למטה כדי להתחיל."
    await ctx.send(welcome_msg, view=WelcomeView())

# הרצת הבוט
if TOKEN:
    bot.run(TOKEN)
else:
    print("שגיאה: לא נמצא טוקן בקובץ ה-.env או בהגדרות Render!")
