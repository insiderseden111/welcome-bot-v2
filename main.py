import discord
from discord.ext import commands
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- שרת Flask כדי למנוע מ-Render לכבות את הבוט ---
app = Flask('')
@app.route('/')
def home(): return "I'm alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- הגדרות Supabase ---
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

# --- הגדרות הבוט ---
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class WelcomeView(discord.ui.View):
    def __init__(self, bot, user_id=None):
        super().__init__(timeout=None)
        self.bot = bot
        # בודק אם המשתמש כבר סיים את התהליך בעבר
        self.stage = 4 if user_id and is_user_completed(user_id) else 1
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        
        # כפתור דיסקליימר תמיד מופיע ראשון
        btn1 = discord.ui.Button(label="🚨 דיסקליימר", style=discord.ButtonStyle.primary, custom_id="p_discl", row=0)
        btn1.callback = self.disclaimer_callback
        self.add_item(btn1)

        if self.stage >= 2:
            btn2 = discord.ui.Button(label="🧐 מה זה פה?", style=discord.ButtonStyle.primary, custom_id="p_what", row=1)
            btn2.callback = self.what_is_callback
            self.add_item(btn2)

        if self.stage >= 3:
            btn3 = discord.ui.Button(label="❗ חשוב לדעת", style=discord.ButtonStyle.primary, custom_id="p_important", row=2)
            btn3.callback = self.important_callback
            self.add_item(btn3)

        if self.stage >= 4:
            btn4 = discord.ui.Button(label="📊 רמות יומיות ועדכונים", style=discord.ButtonStyle.primary, custom_id="p_levels", row=3)
            btn4.callback = self.levels_callback
            self.add_item(btn4)

    async def disclaimer_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🚨 דיסקליימר משפטי", color=discord.Color.blue(), description=(
            "**ברוכים הבאים לקהילת INSIDERS 👋**\n\n"
            "התוכן נוצר למטרות לימודיות בלבד.\n"
            "• אין לראות בנאמר המלצה להשקעה.\n"
            "• כל החלטה היא על אחריות המשתמש בלבד."
        ))
        
        if is_user_completed(interaction.user.id):
            self.stage = 4
            self.update_buttons()
            await interaction.response.edit_message(embed=embed, view=self)
            return

        confirm_view = discord.ui.View(timeout=None)
        confirm_btn = discord.ui.Button(label="הבנתי ואני מאשר ✅", style=discord.ButtonStyle.success)
        
        async def confirm(itn):
            self.stage = 2
            self.update_buttons()
            await itn.response.edit_message(content="✅ אישרת! המשך לשלב הבא.", embed=None, view=self)
            
        confirm_btn.callback = confirm
        confirm_view.add_item(confirm_btn)
        await interaction.response.edit_message(embed=embed, view=confirm_view)

    async def what_is_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🧐 מה זה פה?", color=discord.Color.blue(), description="הסבר על התמצאות בשרת ועל הקהילה.")
        self.stage = max(self.stage, 3)
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def important_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="❗ חשוב לדעת", color=discord.Color.red(), description="אזהרת בטיחות לגבי מתחזים בפרטי.")
        add_user_to_db(interaction.user.id) # שמירת המשתמש במסד הנתונים
        self.stage = 4
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    async def levels_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📊 רמות יומיות", color=discord.Color.gold(), description="עדכוני שוק בזמן אמת.")
        self.stage = 4
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

@bot.event
async def on_ready():
    bot.add_view(WelcomeView(bot))
    print(f'System: {bot.user} is online.')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    # מוחק את הודעת ה-!setup שלך מיד כדי למנוע כפילויות
    try: await ctx.message.delete()
    except: pass
    
    image_url = "https://i.ibb.co/v4m86fP/robot-insiders.png" 
    embed = discord.Embed(title="ברוכים הבאים לקהילת INSIDERS! 🚀", color=discord.Color.blue())
    embed.set_image(url=image_url)
    await ctx.send(embed=embed, view=WelcomeView(bot, user_id=ctx.author.id))

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
