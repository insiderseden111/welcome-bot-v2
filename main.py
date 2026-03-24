import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- Flask Server ---
app = Flask('')
@app.route('/')
def home(): return "Insidie is Live!"
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

# --- 1. מערכת הודעות פרטיות (EDEN System) ---
@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if message.guild is None and message.author.name != TARGET_USERNAME:
        target_admin = discord.utils.get(bot.users, name=TARGET_USERNAME)
        if target_admin:
            embed = discord.Embed(title="📥 הודעה חדשה ממשתמש", description=message.content, color=MAIN_BLUE)
            embed.set_author(name=f"{message.author.display_name}", icon_url=message.author.display_avatar.url)
            embed.set_footer(text=f"לענות לו? העתיקי: !reply {message.author.id} [תוכן]")
            await target_admin.send(embed=embed)
            await message.author.send("ההודעה שלך התקבלה בצוות INSIDERS, נחזור אליך בהקדם! 📩")
    await bot.process_commands(message)

@bot.command()
async def reply(ctx, user_id: int, *, content: str = ""):
    if ctx.author.name != TARGET_USERNAME: return
    try:
        user = await bot.fetch_user(user_id)
        if user:
            embed = discord.Embed(title="💬 מענה מצוות INSIDERS", description=content, color=0x004daa)
            await user.send(embed=embed)
            await ctx.send(f"✅ נשלח ל-{user.display_name}!")
    except Exception as e: await ctx.send(f"❌ שגיאה: {e}")

# --- 2. תהליך אונבורדינג מלווה ---
class OnboardingFlow(discord.ui.View):
    def __init__(self, stage=0):
        super().__init__(timeout=None)
        self.stage = stage
        self.create_buttons()

    def create_buttons(self):
        self.clear_items()
        if self.stage == 0:
            btn = discord.ui.Button(label="נצא לסיור קצר? 🚀", style=discord.ButtonStyle.primary, custom_id="start_flow")
            btn.callback = self.process_next
            self.add_item(btn)
        elif self.stage == 1:
            btn = discord.ui.Button(label="כן, הבנתי ואני מאשר ✅", style=discord.ButtonStyle.success, custom_id="f_1")
            btn.callback = self.process_next
            self.add_item(btn)
        elif self.stage == 2:
            btn = discord.ui.Button(label="חשוב מאוד, בוא נמשיך 🛡️", style=discord.ButtonStyle.primary, custom_id="f_2")
            btn.callback = self.process_next
            self.add_item(btn)
        elif self.stage == 3:
            btn = discord.ui.Button(label="ברור! מה ההטבות? 🎁", style=discord.ButtonStyle.primary, custom_id="f_3")
            btn.callback = self.process_next
            self.add_item(btn)
        elif self.stage == 4:
            self.add_item(discord.ui.Button(label="🚨 דיסקליימר", style=discord.ButtonStyle.secondary, custom_id="n_1"))
            self.add_item(discord.ui.Button(label="🧐 מה זה פה?", style=discord.ButtonStyle.secondary, custom_id="n_2"))
            self.add_item(discord.ui.Button(label="🛡️ בטיחות", style=discord.ButtonStyle.secondary, custom_id="n_3"))
            self.add_item(discord.ui.Button(label="📊 הטבות", style=discord.ButtonStyle.primary, custom_id="n_4", disabled=True))

    async def update_view(self, interaction: discord.Interaction):
        spacer = "\n\u200b\n"
        
        if self.stage == 1:
            embed = discord.Embed(
                title="🚨 שלב 1: מתחילים בבטוח",
                description=f"היי! אני כאן כדי ללוות אותך בכניסה לקהילה.\nלפני הכל, חשוב שתאשר את הדיסקליימר שלנו:\n\n📍 אין לראות בנאמר המלצה או ייעוץ.\n📍 המפעילים אינם בעלי רישיון לייעוץ השקעות.{spacer}**אחרי שנאשר, נוכל להתקדם לסיור קצר. מוכן?**",
                color=MAIN_BLUE
            )
        elif self.stage == 2:
            embed = discord.Embed(
                title="🧐 שלב 2: מה מחכה לך כאן?",
                description=f"מעולה! ב-INSIDERS אנחנו משלבים ידע, ניתוחים וקהילה תומכת.\n\nצירפנו לך סרטון קצר שמסביר איך להפיק את המקסימום מהשרת:\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ{spacer}**יאללה, שנראה איך שומרים עליך ממתחזים?**",
                color=MAIN_BLUE
            )
        elif self.stage == 3:
            embed = discord.Embed(
                title="🛡️ שלב 3: בטיחות בקהילה",
                description=f"חשוב לנו שתדע: הצוות שלנו **לעולם לא יפנה אליך בפרטי** כדי להציע השקעות.\n\n⚠️ אם מישהו פנה אליך - זה כנראה מתחזה.\n📢 תמיד אפשר לדווח לנו בפרטי של הבוט.{spacer}**מוכן לחלק הכי שווה? רמות והטבות!**",
                color=discord.Color.red()
            )
        elif self.stage == 4:
            # כאן כל ההטבות המלאות כפי שהופיעו בתמונה
            levels = (
                "**🎁 סולם ההטבות המלא שלנו:**\n"
                "🔹 **רמה 10:** תג **Insiders Active**.\n"
                "🔹 **רמה 15:** מפגש זום אישי (45 דק') עם מנטור.\n"
                "🔹 **רמה 20:** פתיחת גישה לערוץ ניתוחים מיוחד.\n"
                "🔹 **רמה 25:** פגישת זום אישית מורחבת (שעה שלמה).\n"
                "🔹 **רמה 30:** הנחה של 15% לכל הקורסים והסדנאות.\n"
                "🔹 **רמה 50:** כניסה לקבוצת ה-VIP של הנבחרת!\n\n"
            )
            embed = discord.Embed(title="📊 שלב אחרון: רמות והטבות", description=f"{levels}{spacer}**סיימנו! שלחנו לך הודעה אישית בפרטי. מוזמן להתחיל לצבור נקודות!**", color=MAIN_BLUE)
            try:
                dm_text = f"**ברוך הבא למשפחת INSIDERS!** 🚀\nהיי {interaction.user.display_name}, איזה כיף שסיימת את תהליך הקליטה!\n\nרצינו שתדע שאנחנו ממש שמחים שאתה איתנו בקהילה. המטרה שלנו היא לצמוח יחד, ואנחנו כאן לכל שאלה, עזרה או התייעצות שתצטרך. אל תתבייש לפנות אלינו!\n\nצא לדרך, תהיה פעיל, ותתחיל לכבוש את היעדים שלך."
                await interaction.user.send(embed=discord.Embed(description=dm_text, color=MAIN_BLUE))
            except: pass

        self.create_buttons()
        embed.set_footer(text="━━━━━━━━━━━━━━━━━━━━━━\nINSIDERS Community")
        await interaction.edit_original_response(embed=embed, view=self)

    async def process_next(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.stage += 1
        await self.update_view(interaction)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    try: await ctx.message.delete()
    except: pass
    embed = discord.Embed(
        title="ברוכים הבאים ל-INSIDERS! 🚀", 
        description="שמחים לראות אותך כאן! אני אלווה אותך בצעדים הראשונים כדי שתוכל להתחיל להפיק ערך מהקהילה כבר עכשיו.\n\n**נצא לסיור קצר?**", 
        color=MAIN_BLUE
    )
    embed.set_image(url="https://i.ibb.co/v4m86fP/robot-insiders.png")
    await ctx.send(embed=embed, view=OnboardingFlow(stage=0))

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
