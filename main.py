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

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class WelcomeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def update_message(self, interaction, content, view=None):
        if view is None: view = self
        await interaction.response.edit_message(content=content, view=view)

    # row=0 + Style.primary (כחול)
    @discord.ui.button(label="דיסקליימר", style=discord.ButtonStyle.primary, custom_id="p_disclaimer", row=0)
    async def disclaimer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        content = "**הבהרה משפטית:**\nהתוכן בקבוצה אינו מהווה ייעוץ השקעות. המסחר בשוק ההון כרוך בסיכון."
        confirm_view = discord.ui.View(timeout=60)
        confirm_btn = discord.ui.Button(label="הבנתי", style=discord.ButtonStyle.success)
        async def confirm_callback(itn):
            await itn.response.edit_message(content="✅ אישרת את הדיסקליימר. ברוכים הבאים!", view=self)
        confirm_btn.callback = confirm_callback
        confirm_view.add_item(confirm_btn)
        await interaction.response.edit_message(content=content, view=confirm_view)

    # row=1
    @discord.ui.button(label="מה זה פה?", style=discord.ButtonStyle.primary, custom_id="p_whatis", row=1)
    async def what_is_this(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_message(interaction, "**ברוכים הבאים ל-INSIDERS!**\nכאן לומדים לסחור נכון.")

    # row=2
    @discord.ui.button(label="חשוב לדעת", style=discord.ButtonStyle.primary, custom_id="p_important", row=2)
    async def important_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_message(interaction, "⚠️ **זהירות ממתחזים!** אנחנו לעולם לא נפנה אליכם בפרטי להצעות השקעה.")

    # row=3
    @discord.ui.button(label="רמות יומיות ועדכונים", style=discord.ButtonStyle.primary, custom_id="p_levels", row=3)
    async def levels_updates(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_message(interaction, "📈 כאן תקבלו עדכונים שוטפים על רמות עבודה בשוק.")

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    bot.add_view(WelcomeView())
    print(f'System: {bot.user} is online.')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    welcome_msg = "ברוכים הבאים לקהילת **INSIDERS**! 🚀\nאני הרובוט שלכם, לחצו על הכפתורים למטה כדי להתחיל."
    
    # הוספת התמונה של הרובוט להודעה
    file = discord.File("robot_insiders.png") # וודא שהקובץ נמצא בתיקייה הראשית ב-Render
    await ctx.send(content=welcome_msg, file=file, view=WelcomeView())

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
