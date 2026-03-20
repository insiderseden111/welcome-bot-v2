import discord
from discord.ext import commands
import os
from supabase import create_client, Client
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

# --- Supabase Setup ---
load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def add_user_to_db(user_id):
    supabase.table("completed_users").upsert({"user_id": user_id}).execute()

def is_user_completed(user_id):
    response = supabase.table("completed_users").select("*").eq("user_id", user_id).execute()
    return len(response.data) > 0

# --- Bot Setup ---
TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_CHANNEL_ID = 1484206445128974479 

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class WelcomeView(discord.ui.View):
    def __init__(self, bot, user_id=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        # בדיקה אם המשתמש כבר סיים את התהליך בעבר
        stage = 4 if user_id and is_user_completed(user_id) else 1
        self.create_buttons(stage)

    def create_buttons(self, stage):
        self.clear_items()
        
        # כפתור 1: דיסקליימר
        btn1 = discord.ui.Button(label="🚨 דיסקליימר", style=discord.ButtonStyle.primary, custom_id="p_discl", row=0)
        btn1.callback = self.disclaimer_callback
        self.add_item(btn1)

        # כפתור 2: מה זה פה
        if stage >= 2:
            btn2 = discord.ui.Button(label="🧐 מה זה פה?", style=discord.ButtonStyle.primary, custom_id="p_what", row=1)
            btn2.callback = self.what_is_callback
            self.add_item(btn2)

        # כפתור 3: חשוב לדעת
        if stage >= 3:
            btn3 = discord.ui.Button(label="❗ חשוב לדעת", style=discord.ButtonStyle.primary, custom_id="p_important", row=2)
            btn3.callback = self.important_callback
            self.add_item(btn3)

        # כפתור 4: רמות יומיות
        if stage >= 4:
            btn4 = discord.ui.Button(label="📊 רמות יומיות ועדכונים", style=discord.ButtonStyle.primary, custom_id="p_levels", row=3)
            btn4.callback = self.levels_callback
            self.add_item(btn4)

    async def disclaimer_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🚨 דיסקליימר משפטי", color=discord.Color.blue(), description=(
            "**שלום לכולם 👋**\n\n"
            "התוכן בקהילה נוצר למטרות לימודיות בלבד.\n\n"
            "• **אין לראות בנאמר המלצה או ייעוץ להשקעה.**\n"
            "• כל פרסום אינו מהווה תחליף לייעוץ המתחשב בצרכים אישיים.\n"
            "• המפעילים אינם בעלי רישיון לייעוץ/שיווק השקעות ע\"פ חוק.\n"
            "• כל החלטת השקעה היא על אחריות המשתמש בלבד."
        ))
        
        if is_user_completed(interaction.user.id):
            self.create_buttons(stage=4)
            await interaction.response.edit_message(embed=embed, view=self)
            return

        # יצירת כפתור אישור זמני רק למי שטרם אישר
        confirm_view = discord.ui.View(timeout=None)
        confirm_btn = discord.ui.Button(label="הבנתי ואני מאשר ✅", style=discord.ButtonStyle.success)
        
        async def confirm(itn):
            admin_ch = self.bot.get_channel(ADMIN_CHANNEL_ID)
            if admin_ch: 
                await admin_ch.send(f"✅ המשתמש **{itn.user}** (ID: {itn.user.id}) אישר את הדיסקליימר.")
            
            self.create_buttons(stage=2)
            success_embed = discord.Embed(description="✅ אישרת את הדיסקליימר. כעת עברו ללחוץ על **מה זה פה?**", color=discord.Color.green())
            await itn.response.edit_message(embed=success_embed, view=self)
            
        confirm_btn.callback = confirm
        confirm_view.add_item(confirm_btn)
        await interaction.response.edit_message(embed=embed, view=confirm_view)

    async def what_is_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🧐 מה זה פה?", color=discord.Color.blue(), description=(
            "**ברוכים הבאים לקהילת INSIDERS!** 🇮🇱\n\n"
            "כאן תוכלו לשאול הכל על התמצאות בשרת הקהילה:\n"
            "• איפה מעלים ניתוחי עסקאות?\n"
            "• איפה מפרסמים מניות מעניינות?\n\n"
            "**לינק הסבר על הקהילה:**\n"
            "[לחצו כאן לצפייה בהסבר המלא](https://youtube.com/your-link-here)"
        ))
        stage = 4 if is_user_completed(interaction.user.id) else 3
        self.create_buttons(stage=stage)
        await interaction.response.edit_message(embed=embed, view=self)

    async def important_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="❗ חשוב לדעת - בטיחות", color=discord.Color.red(), description=(
            "⚠️ **לתשומת לבכם**\n\n"
            "אנחנו לעולם לא נפנה אליכם בפרטי ונציע לכם להשקיע ו/או שאנחנו נשקיע עבורכם.\n\n"
            "נוכלים פתחו בעבר משתמשים עם תמונות ושמות דומים לשלנו והציעו הצעות לחברים חדשים.\n\n"
            "לכן, אם פונים אליכם בפרטי עם הצעה - **מדובר במתחזה** ויש לדווח על המשתמש וההודעה מיד!"
        ))
        add_user_to_db(interaction.user.id) # שמירה לצמיתות בענן
        self.create_buttons(stage=4)
        await interaction.response.edit_message(embed=embed, view=self)

    async def levels_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📊 רמות יומיות ועדכונים", color=discord.Color.gold(), description=(
            "📈 **עדכונים שוטפים מהשוק**\n\n"
            "כאן יפורסמו רמות עבודה, ניתוחים טכניים ועדכונים חמים על מניות ומדדים בזמן אמת.\n\n"
            "**סיימתם את תהליך ההיכרות! כל הכפתורים פתוחים עבורכם כעת.**"
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
    try: await ctx.message.delete() # מחיקת ה-!setup למניעת כפילות
    except: pass

    image_url = "https://i.ibb.co/v4m86fP/robot-insiders.png" 
    embed = discord.Embed(title="ברוכים הבאים לקהילת INSIDERS! 🚀", color=discord.Color.blue())
    embed.set_image(url=image_url)
    
    # שליחת ההודעה הראשונית (בודק אוטומטית אם המשתמש כבר רשום ב-Supabase)
    await ctx.send(embed=embed, view=WelcomeView(bot, user_id=ctx.author.id))

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
