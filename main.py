import discord
from discord.ext import commands
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- Flask Server ---
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
supabase = create_client(url, key) if url and key else None

def add_user_to_db(user_id):
    if supabase:
        try:
            supabase.table("completed_users").upsert({"user_id": str(user_id)}).execute()
        except Exception as e:
            print(f"Database Log Error: {e}")

# --- Bot Setup ---
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True 
bot = commands.Bot(command_prefix='!', intents=intents)

class WelcomeView(discord.ui.View):
    def __init__(self, bot, stage=1):
        super().__init__(timeout=None)
        self.bot = bot
        self.stage = stage
        self.update_buttons()

    def update_buttons(self):
        self.clear_items()
        
        # כפתור 1 - דיסקליימר (תמיד בשורה 0)
        btn1 = discord.ui.Button(label="🚨 דיסקליימר", style=discord.ButtonStyle.primary, custom_id="p_discl", row=0)
        btn1.callback = self.disclaimer_callback
        self.add_item(btn1)

        # כפתור 2 - מה זה פה?
        if self.stage >= 2:
            btn2 = discord.ui.Button(label="🧐 מה זה פה?", style=discord.ButtonStyle.primary, custom_id="p_what", row=0)
            btn2.callback = self.what_is_callback
            self.add_item(btn2)

        # כפתור 3 - חשוב לדעת
        if self.stage >= 3:
            btn3 = discord.ui.Button(label="❗ חשוב לדעת", style=discord.ButtonStyle.primary, custom_id="p_important", row=0)
            btn3.callback = self.important_callback
            self.add_item(btn3)

        # כפתור 4 - עדכוני רמות
        if self.stage >= 4:
            btn4 = discord.ui.Button(label="📊 עדכוני רמות והטבות", style=discord.ButtonStyle.primary, custom_id="p_levels", row=0)
            btn4.callback = self.levels_callback
            self.add_item(btn4)

    async def disclaimer_callback(self, interaction: discord.Interaction):
        full_text = (
            "התוכן נוצר מתוך אהבה לשוק ההון והאמונה שכולנו צריכים לייצר ערך כלכלי.\n\n"
            "📍 **אין לראות בנאמר המלצה או ייעוץ לביצוע השקעה מכל סוג שהוא.**\n\n"
            "📍 המפעילים **אינם בעלי רישיון לייעוץ השקעות**.\n\n"
            "📍 כל השקעה שתבוצע היא על פי שיקול דעתכם הבלעדי."
        )
        embed = discord.Embed(title="🚨 דיסקליימר ותנאי שימוש", color=discord.Color.blue(), description=full_text)
        
        confirm_view = discord.ui.View(timeout=None)
        confirm_btn = discord.ui.Button(label="הבנתי ואני מאשר ✅", style=discord.ButtonStyle.success)
        
        async def confirm(itn: discord.Interaction):
            # שימוש ב-defer כדי למנוע קריסה בזמן עדכון ה-DB
            await itn.response.defer(ephemeral=True)
            
            self.stage = 2
            self.update_buttons()
            add_user_to_db(itn.user.id)
            
            # שליחת לוג לערוץ (שם מעודכן לפי התמונה שלך)
            log_channel = discord.utils.get(itn.guild.channels, name="אישורי-דיסקליימר")
            if log_channel:
                await log_channel.send(f"המשתמש **{itn.user.name}** (ID: {itn.user.id}) אישר את הדיסקליימר. ✅")
            
            new_embed = discord.Embed(title="🧐 מה זה פה?", color=discord.Color.blue(), 
                                    description="ברוכים הבאים ל-INSIDERS! כאן אנחנו לומדים וצומחים יחד.\n\n**סרטון הסבר:**\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ")
            
            # עדכון ההודעה המקורית עם הכפתורים החדשים בשורה
            await itn.edit_original_response(content="✅ אישרת את התנאים!", embed=new_embed, view=self)
            
        confirm_btn.callback = confirm
        confirm_view.add_item(confirm_btn)
        await interaction.response.edit_message(embed=embed, view=confirm_view)

    async def what_is_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🧐 מה זה פה?", color=discord.Color.blue(), 
                            description="ברוכים הבאים ל-INSIDERS! כאן אנחנו לומדים וצומחים יחד.\n\n**סרטון הסבר:**\nhttps://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.stage = max(self.stage, 3)
        self.update_buttons()
        await interaction.response.edit_message(content=None, embed=embed, view=self)

    async def important_callback(self, interaction: discord.Interaction):
        safety_text = (
            "📢 **לתשומת לבכם**\n\n"
            "🛑 אנחנו לעולם לא נפנה אליכם בפרטי ונציע לכם להשקיע עבורכם.\n\n"
            "⚠️ אם פונים אליכם בפרטי - **מדובר במתחזה!**\n\n"
            "📢 **ויש לדווח על המשתמש שפנה אליכם ועל ההודעה.**"
        )
        embed = discord.Embed(title="❗ חשוב לדעת - כללי בטיחות", color=discord.Color.red(), description=safety_text)
        self.stage = max(self.stage, 4)
        self.update_buttons()
        await interaction.response.edit_message(content=None, embed=embed, view=self)

    async def levels_callback(self, interaction: discord.Interaction):
        levels_text = (
            "בקהילה שלנו, ככל שאתם פעילים יותר – אתם עולים רמות וזוכים בהטבות בלעדיות!\n\n"
            "🔹 **רמה 10:** תג **Insiders Active**.\n"
            "🔹 **רמה 15:** מפגש זום אישי (45 דק').\n"
            "🔹 **רמה 30:** הנחה קבועה של 15%.\n"
            "🔹 **רמה 50:** כניסה לקבוצת ה-VIP!\n\n"
            "**איך עולים רמה?** פשוט משתפים גרפים ועוזרים לאחרים!"
        )
        embed = discord.Embed(title="📊 עדכוני רמות והטבות", color=discord.Color.blue(), description=levels_text)
        await interaction.response.edit_message(content=None, embed=embed, view=self)

@bot.event
async def on_ready():
    print(f'System: {bot.user} is online.')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(title="ברוכים הבאים לקהילת INSIDERS! 🚀", color=discord.Color.blue())
    embed.set_image(url="https://i.ibb.co/v4m86fP/robot-insiders.png") 
    await ctx.send(embed=embed, view=WelcomeView(bot))

if TOKEN:
    keep_alive()
    bot.run(TOKEN)
