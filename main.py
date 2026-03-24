import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- Flask Server ---
app = Flask('')
@app.route('/')
def home(): return "Bot is running!"
def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Bot Config ---
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_USERNAME = "eden_insiders_49810" 
MAIN_BLUE = 0x0080e8 

intents = discord.Intents.all() 
bot = commands.Bot(command_prefix='!', intents=intents)

# --- 1. מערכת הודעות פרטיות (ללא שינוי) ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if message.guild is None and message.author.name != TARGET_USERNAME:
        target_admin = discord.utils.get(bot.users, name=TARGET_USERNAME)
        if target_admin:
            embed = discord.Embed(title="📥 הודעה חדשה", description=message.content, color=MAIN_BLUE)
            await target_admin.send(embed=embed)
    await bot.process_commands(message)

# --- 2. תהליך אונבורדינג זורם (Flow) ---
class OnboardingFlow(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.stage = 1

    async def update_stage(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # שלב 1: דיסקליימר
        if self.stage == 1:
            embed = discord.Embed(
                title="🚨 שלב 1: דיסקליימר ותנאי שימוש",
                description=(
                    "לפני שמתחילים, חשוב לנו שתדעו:\n"
                    "📍 אין לראות בנאמר המלצה או ייעוץ השקעות.\n"
                    "📍 המפעילים אינם בעלי רישיון לייעוץ.\n\n"
                    "**מוכנים להמשיך לסיור בקהילה?**"
                ),
                color=MAIN_BLUE
            )
            self.clear_items()
            btn = discord.ui.Button(label="כן, הבנתי ואני מאשר ✅", style=discord.ButtonStyle.success, custom_id="flow_1")
            btn.callback = self.next_step
            self.add_item(btn)

        # שלב 2: מה זה פה?
        elif self.stage == 2:
            embed = discord.Embed(
                title="🧐 שלב 2: מה זה פה בעצם?",
                description=(
                    "ברוכים הבאים ל-INSIDERS! המקום שלכם ללמוד ולהתפתח בשוק ההון.\n\n"
                    "📺 **צפו בסרטון ההסבר הקצר שלנו:**\n"
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ\n\n"
                    "**יאללה, שנעבור לכללי הבטיחות החשובים?**"
                ),
                color=MAIN_BLUE
            )
            self.clear_items()
            btn = discord.ui.Button(label="כן, חשוב לדעת! 🛡️", style=discord.ButtonStyle.primary, custom_id="flow_2")
            btn.callback = self.next_step
            self.add_item(btn)

        # שלב 3: בטיחות
        elif self.stage == 3:
            embed = discord.Embed(
                title="❗ שלב 3: בטיחות מעל הכל",
                description=(
                    "🛑 **שימו לב:** אנחנו לעולם לא נפנה אליכם בפרטי להשקעות.\n"
                    "⚠️ אם פנו אליכם - זה מתחזה! דווחו לנו מיד.\n\n"
                    "**נעבור לחלק המעניין? הטבות ורמות! 🎁**"
                ),
                color=discord.Color.red()
            )
            self.clear_items()
            btn = discord.ui.Button(label="ברור, תראה לי הטבות! 📊", style=discord.ButtonStyle.primary, custom_id="flow_3")
            btn.callback = self.next_step
            self.add_item(btn)

        # שלב 4: רמות (סוף)
        elif self.stage == 4:
            levels_text = (
                "🔹 **רמה 15:** מפגש זום אישי (45 דק').\n"
                "🔹 **רמה 30:** 15% הנחה לקורסים.\n"
                "🔹 **רמה 50:** כניסה ל-VIP!\n\n"
                "**זהו, סיימנו! עכשיו הכל פתוח בפניך.**"
            )
            embed = discord.Embed(title="📊 שלב אחרון: הטבות ורמות", description=levels_text, color=MAIN_BLUE)
            self.clear_items()
            # בסוף משאירים את הכפתורים פתוחים לניווט חופשי
            self.add_item(discord.ui.Button(label="דיסקליימר", style=discord.ButtonStyle.secondary, custom_id="nav_1"))
            self.add_item(discord.ui.Button(label="מה זה פה?", style=discord.ButtonStyle.secondary, custom_id="nav_2"))
            self.add_item(discord.ui.Button(label="בטיחות", style=discord.ButtonStyle.secondary, custom_id="nav_3"))
            self.add_item(discord.ui.Button(label="הטבות", style=discord.ButtonStyle.primary, custom_id="nav_4", disabled=True))

        # הוספת "שורת רווח" בתחתית כל Embed
        embed.set_footer(text="━━━━━━━━━━━━━━━━━━━━━━\nINSIDERS Community")
        
        await interaction.edit_original_response(embed=embed, view=self)

    async def next_step(self, interaction: discord.Interaction):
        self.stage += 1
        await self.update_stage(interaction)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    view = OnboardingFlow()
    # התחלה משלב 1
    embed = discord.Embed(title="ברוכים הבאים ל-INSIDERS! 🚀", description="בואו נתחיל בתהליך קצר שיכניס אתכם לעניינים.\n\n**לחצו על הכפתור למטה כדי להתחיל.**", color=MAIN_BLUE)
    embed.set_image(url="https://i.ibb.co/v4m86fP/robot-insiders.png")
    await ctx.send(embed=embed, view=view)

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
