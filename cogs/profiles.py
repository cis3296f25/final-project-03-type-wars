# cogs/profiles.py
import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio
from typing import Optional

LEADERBOARD_FILE = "leaderboard.json"
PROFILES_FILE = "profiles.json"


class Profiles(commands.Cog):
    """Profiles + wins tracking (TypeWars + total wins)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.leaderboard: dict[str, dict] = {}
        self.profiles: dict[str, dict] = {}
        self._load_leaderboard()
        self._load_profiles()

    # ---------- LOAD / SAVE HELPERS ----------

    def _load_leaderboard(self):
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, "r") as f:
                    self.leaderboard = json.load(f)
            except Exception:
                self.leaderboard = {}
        else:
            self.leaderboard = {}

    def _save_leaderboard(self):
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(self.leaderboard, f, indent=2)

    def _load_profiles(self):
        if os.path.exists(PROFILES_FILE):
            try:
                with open(PROFILES_FILE, "r") as f:
                    self.profiles = json.load(f)
            except Exception:
                self.profiles = {}
        else:
            self.profiles = {}

    def _save_profiles(self):
        with open(PROFILES_FILE, "w") as f:
            json.dump(self.profiles, f, indent=4)

    def _ensure_leader_entry(self, user_id: str):
        if user_id not in self.leaderboard:
            self.leaderboard[user_id] = {
                "single_best_time": None,
                "single_best_word": None,
                "multi_wins": 0,
            }

    # ---------- PUBLIC API FOR GAMES ----------

    async def record_typewars_result(
        self,
        winner: discord.Member,
        mode: str,
        duration: Optional[float] = None,
        word: Optional[str] = None,
    ):
        """
        Called by games when TypeWars ends.
        mode: "single" or "multi"
        duration & word used for single-player best-time tracking.
        """
        user_id = str(winner.id)
        self._ensure_leader_entry(user_id)
        entry = self.leaderboard[user_id]

        # Single-player: store best time + word
        if mode == "single" and duration is not None and word:
            if entry["single_best_time"] is None or duration < entry["single_best_time"]:
                entry["single_best_time"] = duration
                entry["single_best_word"] = word

        # Multiplayer: increment wins
        if mode == "multi":
            entry["multi_wins"] += 1

        self._save_leaderboard()

        # Also bump profile total wins, if they have a profile
        if user_id in self.profiles:
            self.profiles[user_id]["wins"] = self.profiles[user_id].get("wins", 0) + 1
            self._save_profiles()

    # ---------- SLASH COMMANDS: WINS + PROFILE MENU ----------

    @app_commands.command(name="wins", description="Check your TypeWars stats")
    async def wins_slash(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        entry = self.leaderboard.get(user_id)

        if not entry:
            await interaction.response.send_message(
                "❓ You haven't played TypeWars yet!", ephemeral=True
            )
            return

        lines = []
        if entry.get("single_best_time") is not None and entry.get("single_best_word"):
            lines.append(
                f"⏱️ Your fastest single-player time: "
                f"**{entry['single_best_time']}s** on the word **{entry['single_best_word']}**."
            )

        multi = entry.get("multi_wins", 0)
        lines.append(f"⌨️ You have **{multi}** multiplayer TypeWars win(s)!")

        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @app_commands.command(
        name="profile", description="Show profile commands and quick info"
    )
    async def profile_help(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        prof = self.profiles.get(user_id)
        wins = self.leaderboard.get(user_id, {}).get("multi_wins", 0)

        embed = discord.Embed(
            title="Profile Menu",
            description="Commands to manage your profile and view stats",
            color=0x95A5A6,
        )
        embed.add_field(name="/create", value="Create your profile", inline=False)
        embed.add_field(
            name="/edit", value="Edit your username, bio, or favorite game", inline=False
        )
        embed.add_field(
            name="/view", value="View your own profile or another user's", inline=False
        )
        embed.add_field(
            name="/delete", value="Delete your profile", inline=False
        )
        embed.add_field(
            name="/wins", value="View your TypeWars stats", inline=False
        )

        if prof:
            embed.add_field(
                name="Current Profile",
                value=(
                    f"Username: **{prof.get('username', 'N/A')}**\n"
                    f"Bio: {prof.get('bio', 'N/A')}\n"
                    f"Favorite Game: {prof.get('favgame', 'N/A')}\n"
                    f"Total Wins (all games): {prof.get('wins', 0)}\n"
                    f"TypeWars Multiplayer Wins: {wins}"
                ),
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ---------- SLASH COMMANDS: PROFILE CRUD ----------

    @app_commands.command(name="create", description="Create your profile")
    async def create_profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        if user_id in self.profiles:
            await interaction.response.send_message(
                "You already have a profile.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Let's create your profile in this channel. "
            "Reply with your **username**.",
            ephemeral=True,
        )

        def check(m: discord.Message):
            return (
                m.author == interaction.user
                and m.channel == interaction.channel
            )

        # Username
        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out. Profile creation cancelled.", ephemeral=True
            )
            return
        username = msg.content.strip()

        await interaction.followup.send("Now send a short **bio**.", ephemeral=True)
        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out. Profile creation cancelled.", ephemeral=True
            )
            return
        bio = msg.content.strip()

        await interaction.followup.send(
            "Finally, what's your **favorite game**?", ephemeral=True
        )
        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out. Profile creation cancelled.", ephemeral=True
            )
            return
        favgame = msg.content.strip()

        self.profiles[user_id] = {
            "username": username,
            "bio": bio,
            "favgame": favgame,
            "wins": 0,
        }
        self._save_profiles()

        await interaction.followup.send("✅ Profile saved!", ephemeral=True)

    @app_commands.command(name="edit", description="Edit your profile")
    async def edit_profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        if user_id not in self.profiles:
            await interaction.response.send_message(
                "You don't have a profile to edit.", ephemeral=True
            )
            return

        await interaction.response.send_message(
            "What do you want to edit? Type: `username`, `bio`, or `favgame`.",
            ephemeral=True,
        )

        def check(m: discord.Message):
            return (
                m.author == interaction.user
                and m.channel == interaction.channel
            )

        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out. Edit cancelled.", ephemeral=True
            )
            return

        choice = msg.content.strip().lower()

        if choice == "username":
            await self._edit_username(interaction, user_id, check)
        elif choice == "bio":
            await self._edit_bio(interaction, user_id, check)
        elif choice == "favgame":
            await self._edit_favgame(interaction, user_id, check)
        else:
            await interaction.followup.send(
                "That isn't a valid option.", ephemeral=True
            )

    async def _edit_username(self, interaction, user_id: str, check):
        await interaction.followup.send("Enter new username:", ephemeral=True)
        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out. Username not changed.", ephemeral=True
            )
            return
        new_username = msg.content.strip()
        self.profiles[user_id]["username"] = new_username
        self._save_profiles()
        await interaction.followup.send(
            f"Your new username `{new_username}` is saved.", ephemeral=True
        )

    async def _edit_bio(self, interaction, user_id: str, check):
        await interaction.followup.send("Enter new bio:", ephemeral=True)
        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out. Bio not changed.", ephemeral=True
            )
            return
        new_bio = msg.content.strip()
        self.profiles[user_id]["bio"] = new_bio
        self._save_profiles()
        await interaction.followup.send(
            "Your new bio is saved.", ephemeral=True
        )

    async def _edit_favgame(self, interaction, user_id: str, check):
        await interaction.followup.send("Enter new favorite game:", ephemeral=True)
        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out. Favorite game not changed.", ephemeral=True
            )
            return
        new_game = msg.content.strip()
        self.profiles[user_id]["favgame"] = new_game
        self._save_profiles()
        await interaction.followup.send(
            "Your new favorite game is saved.", ephemeral=True
        )

    @app_commands.command(name="delete", description="Delete your profile")
    async def delete_profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        if user_id not in self.profiles:
            await interaction.response.send_message(
                "You don't have a profile to delete.", ephemeral=True
            )
            return

        username = self.profiles[user_id].get("username", "this user")
        await interaction.response.send_message(
            f"Are you sure you want to delete **{username}**'s profile? (yes/no)",
            ephemeral=True,
        )

        def check(m: discord.Message):
            return (
                m.author == interaction.user
                and m.channel == interaction.channel
            )

        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out. Profile not deleted.", ephemeral=True
            )
            return

        if msg.content.strip().lower() in ("yes", "y"):
            del self.profiles[user_id]
            self._save_profiles()
            await interaction.followup.send(
                "Profile deleted.", ephemeral=True
            )
        else:
            await interaction.followup.send(
                "Profile was not deleted.", ephemeral=True
            )

    @app_commands.command(name="view", description="View your profile or another user's profile")
    async def view_profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        # Ask whether to show "mine" or another username
        await interaction.response.send_message(
            "Type `mine` to view your own profile, or type a username to view someone else's profile.",
            ephemeral=True,
        )

        def check(m: discord.Message):
            return (
                m.author == interaction.user
                and m.channel == interaction.channel
            )

        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timed out. View cancelled.", ephemeral=True
            )
            return

        content = msg.content.strip()

        if content.lower() == "mine":
            await self._view_profile_by_id(interaction, user_id)
        else:
            await self._view_profile_by_username(interaction, content)

    async def _view_profile_by_id(self, interaction: discord.Interaction, user_id: str):
        if user_id not in self.profiles:
            await interaction.followup.send(
                "You don't have a profile yet.", ephemeral=True
            )
            return

        profile = self.profiles[user_id]

        embed = discord.Embed(
            title=f"{profile.get('username', 'User')}'s Profile",
            color=0x3498DB,
        )
        embed.add_field(name="Bio", value=profile.get("bio", "N/A"), inline=False)
        embed.add_field(name="Favorite Game", value=profile.get("favgame", "N/A"), inline=False)
        embed.add_field(name="Total Wins", value=profile.get("wins", 0), inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    async def _view_profile_by_username(self, interaction: discord.Interaction, username: str):
        username_clean = username.strip().replace("@", "")
        target_id = None

        for uid, profile in self.profiles.items():
            if profile.get("username", "").lower() == username_clean.lower():
                target_id = uid
                break

        if target_id is None:
            await interaction.followup.send(
                "That user doesn't have a profile.", ephemeral=True
            )
        else:
            await self._view_profile_by_id(interaction, target_id)



async def setup(bot: commands.Bot):
    print("Loading Profiles cog...")
    await bot.add_cog(Profiles(bot))

############################################################################

# cogs/profiles.py
# import discord
# from discord.ext import commands
# from discord import app_commands
# import json
# import os
# import asyncio
# from typing import Optional

# LEADERBOARD_FILE = "leaderboard.json"
# PROFILES_FILE = "profiles.json"

# # Your guild ID (same as in bot-test.py)
# GUILD_ID = 1420829218882719848
# GUILD = discord.Object(id=GUILD_ID)


# class Profiles(commands.Cog):
#     """Profiles + wins tracking (TypeWars + total wins)."""

#     def __init__(self, bot: commands.Bot):
#         self.bot = bot
#         self.leaderboard: dict[str, dict] = {}
#         self.profiles: dict[str, dict] = {}
#         self._load_leaderboard()
#         self._load_profiles()

#     # ---------- LOAD / SAVE HELPERS ----------

#     def _load_leaderboard(self):
#         if os.path.exists(LEADERBOARD_FILE):
#             try:
#                 with open(LEADERBOARD_FILE, "r") as f:
#                     self.leaderboard = json.load(f)
#             except Exception:
#                 self.leaderboard = {}
#         else:
#             self.leaderboard = {}

#     def _save_leaderboard(self):
#         with open(LEADERBOARD_FILE, "w") as f:
#             json.dump(self.leaderboard, f, indent=2)

#     def _load_profiles(self):
#         if os.path.exists(PROFILES_FILE):
#             try:
#                 with open(PROFILES_FILE, "r") as f:
#                     self.profiles = json.load(f)
#             except Exception:
#                 self.profiles = {}
#         else:
#             self.profiles = {}

#     def _save_profiles(self):
#         with open(PROFILES_FILE, "w") as f:
#             json.dump(self.profiles, f, indent=4)

#     def _ensure_leader_entry(self, user_id: str):
#         if user_id not in self.leaderboard:
#             self.leaderboard[user_id] = {
#                 "single_best_time": None,
#                 "single_best_word": None,
#                 "multi_wins": 0,
#             }

#     # ---------- PUBLIC API FOR GAMES ----------

#     async def record_typewars_result(
#         self,
#         winner: discord.Member,
#         mode: str,
#         duration: Optional[float] = None,
#         word: Optional[str] = None,
#     ):
#         """
#         Called by games when TypeWars ends.
#         mode: "single" or "multi"
#         duration & word used for single-player best-time tracking.
#         """
#         user_id = str(winner.id)
#         self._ensure_leader_entry(user_id)
#         entry = self.leaderboard[user_id]

#         # Single-player: store best time + word
#         if mode == "single" and duration is not None and word:
#             if entry["single_best_time"] is None or duration < entry["single_best_time"]:
#                 entry["single_best_time"] = duration
#                 entry["single_best_word"] = word

#         # Multiplayer: increment wins
#         if mode == "multi":
#             entry["multi_wins"] += 1

#         self._save_leaderboard()

#         # Also bump profile total wins, if they have a profile
#         if user_id in self.profiles:
#             self.profiles[user_id]["wins"] = self.profiles[user_id].get("wins", 0) + 1
#             self._save_profiles()

#     # ---------- SLASH COMMANDS: WINS + PROFILE MENU ----------

#     @app_commands.command(name="wins", description="Check your TypeWars stats")
#     @app_commands.guilds(GUILD)
#     async def wins_slash(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)
#         entry = self.leaderboard.get(user_id)

#         if not entry:
#             await interaction.response.send_message(
#                 "❓ You haven't played TypeWars yet!", ephemeral=True
#             )
#             return

#         lines = []
#         if entry.get("single_best_time") is not None and entry.get("single_best_word"):
#             lines.append(
#                 f"⏱️ Your fastest single-player time: "
#                 f"**{entry['single_best_time']}s** on the word **{entry['single_best_word']}**."
#             )

#         multi = entry.get("multi_wins", 0)
#         lines.append(f"⌨️ You have **{multi}** multiplayer TypeWars win(s)!")

#         await interaction.response.send_message("\n".join(lines), ephemeral=True)

#     @app_commands.command(
#         name="profile", description="Show profile commands and quick info"
#     )
#     @app_commands.guilds(GUILD)
#     async def profile_help(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)
#         prof = self.profiles.get(user_id)
#         wins = self.leaderboard.get(user_id, {}).get("multi_wins", 0)

#         embed = discord.Embed(
#             title="Profile Menu",
#             description="Commands to manage your profile and view stats",
#             color=0x95A5A6,
#         )
#         embed.add_field(name="/create", value="Create your profile", inline=False)
#         embed.add_field(
#             name="/edit", value="Edit your username, bio, or favorite game", inline=False
#         )
#         embed.add_field(
#             name="/view", value="View your own profile or another user's", inline=False
#         )
#         embed.add_field(
#             name="/delete", value="Delete your profile", inline=False
#         )
#         embed.add_field(
#             name="/wins", value="View your TypeWars stats", inline=False
#         )

#         if prof:
#             embed.add_field(
#                 name="Current Profile",
#                 value=(
#                     f"Username: **{prof.get('username', 'N/A')}**\n"
#                     f"Bio: {prof.get('bio', 'N/A')}\n"
#                     f"Favorite Game: {prof.get('favgame', 'N/A')}\n"
#                     f"Total Wins (all games): {prof.get('wins', 0)}\n"
#                     f"TypeWars Multiplayer Wins: {wins}"
#                 ),
#                 inline=False,
#             )

#         await interaction.response.send_message(embed=embed, ephemeral=True)

#     # ---------- SLASH COMMANDS: PROFILE CRUD ----------

#     @app_commands.command(name="create", description="Create your profile")
#     @app_commands.guilds(GUILD)
#     async def create_profile(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)

#         if user_id in self.profiles:
#             await interaction.response.send_message(
#                 "You already have a profile.", ephemeral=True
#             )
#             return

#         await interaction.response.send_message(
#             "Let's create your profile in this channel.\n"
#             "Reply with your **username**.",
#             ephemeral=True,
#         )

#         def check(m: discord.Message):
#             return (
#                 m.author == interaction.user
#                 and m.channel == interaction.channel
#             )

#         # Username
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Profile creation cancelled.", ephemeral=True
#             )
#             return
#         username = msg.content.strip()

#         await interaction.followup.send("Now send a short **bio**.", ephemeral=True)
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Profile creation cancelled.", ephemeral=True
#             )
#             return
#         bio = msg.content.strip()

#         await interaction.followup.send(
#             "Finally, what's your **favorite game**?", ephemeral=True
#         )
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Profile creation cancelled.", ephemeral=True
#             )
#             return
#         favgame = msg.content.strip()

#         self.profiles[user_id] = {
#             "username": username,
#             "bio": bio,
#             "favgame": favgame,
#             "wins": 0,
#         }
#         self._save_profiles()

#         await interaction.followup.send("✅ Profile saved!", ephemeral=True)

#     @app_commands.command(name="edit", description="Edit your profile")
#     @app_commands.guilds(GUILD)
#     async def edit_profile(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)

#         if user_id not in self.profiles:
#             await interaction.response.send_message(
#                 "You don't have a profile to edit.", ephemeral=True
#             )
#             return

#         await interaction.response.send_message(
#             "What do you want to edit? Type: `username`, `bio`, or `favgame`.",
#             ephemeral=True,
#         )

#         def check(m: discord.Message):
#             return (
#                 m.author == interaction.user
#                 and m.channel == interaction.channel
#             )

#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Edit cancelled.", ephemeral=True
#             )
#             return

#         choice = msg.content.strip().lower()

#         if choice == "username":
#             await self._edit_username(interaction, user_id, check)
#         elif choice == "bio":
#             await self._edit_bio(interaction, user_id, check)
#         elif choice == "favgame":
#             await self._edit_favgame(interaction, user_id, check)
#         else:
#             await interaction.followup.send(
#                 "That isn't a valid option.", ephemeral=True
#             )

#     async def _edit_username(self, interaction, user_id: str, check):
#         await interaction.followup.send("Enter new username:", ephemeral=True)
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Username not changed.", ephemeral=True
#             )
#             return
#         new_username = msg.content.strip()
#         self.profiles[user_id]["username"] = new_username
#         self._save_profiles()
#         await interaction.followup.send(
#             f"Your new username `{new_username}` is saved.", ephemeral=True
#         )

#     async def _edit_bio(self, interaction, user_id: str, check):
#         await interaction.followup.send("Enter new bio:", ephemeral=True)
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Bio not changed.", ephemeral=True
#             )
#             return
#         new_bio = msg.content.strip()
#         self.profiles[user_id]["bio"] = new_bio
#         self._save_profiles()
#         await interaction.followup.send(
#             "Your new bio is saved.", ephemeral=True
#         )

#     async def _edit_favgame(self, interaction, user_id: str, check):
#         await interaction.followup.send("Enter new favorite game:", ephemeral=True)
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Favorite game not changed.", ephemeral=True
#             )
#             return
#         new_game = msg.content.strip()
#         self.profiles[user_id]["favgame"] = new_game
#         self._save_profiles()
#         await interaction.followup.send(
#             "Your new favorite game is saved.", ephemeral=True
#         )

#     @app_commands.command(name="delete", description="Delete your profile")
#     @app_commands.guilds(GUILD)
#     async def delete_profile(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)

#         if user_id not in self.profiles:
#             await interaction.response.send_message(
#                 "You don't have a profile to delete.", ephemeral=True
#             )
#             return

#         username = self.profiles[user_id].get("username", "this user")
#         await interaction.response.send_message(
#             f"Are you sure you want to delete **{username}**'s profile? (yes/no)",
#             ephemeral=True,
#         )

#         def check(m: discord.Message):
#             return (
#                 m.author == interaction.user
#                 and m.channel == interaction.channel
#             )

#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Profile not deleted.", ephemeral=True
#             )
#             return

#         if msg.content.strip().lower() in ("yes", "y"):
#             del self.profiles[user_id]
#             self._save_profiles()
#             await interaction.followup.send(
#                 "Profile deleted.", ephemeral=True
#             )
#         else:
#             await interaction.followup.send(
#                 "Profile was not deleted.", ephemeral=True
#             )


# async def setup(bot: commands.Bot):
#     print("Loading Profiles cog...")
#     await bot.add_cog(Profiles(bot))

######################################################################################

# # cogs/profiles.py
# import discord
# from discord.ext import commands
# import json
# import os
# import asyncio

# LEADERBOARD_FILE = "leaderboard.json"
# PROFILES_FILE = "profiles.json"

# GUILD_ID = 1420829218882719848
# GUILD = discord.Object(id=GUILD_ID)


# class Profiles(commands.Cog):
#     """Profiles + wins tracking (TypeWars + total wins)."""

#     def __init__(self, bot):
#         self.bot = bot
#         self.leaderboard = {}  # user_id -> {single_best_time, single_best_word, multi_wins}
#         self.profiles = {}     # user_id -> {username, bio, favgame, wins}
#         self._load_leaderboard()
#         self._load_profiles()

#     # ---------- LOAD / SAVE HELPERS ----------

#     def _load_leaderboard(self):
#         if os.path.exists(LEADERBOARD_FILE):
#             try:
#                 with open(LEADERBOARD_FILE, "r") as f:
#                     self.leaderboard = json.load(f)
#             except Exception:
#                 self.leaderboard = {}
#         else:
#             self.leaderboard = {}

#     def _save_leaderboard(self):
#         with open(LEADERBOARD_FILE, "w") as f:
#             json.dump(self.leaderboard, f, indent=2)

#     def _load_profiles(self):
#         if os.path.exists(PROFILES_FILE):
#             try:
#                 with open(PROFILES_FILE, "r") as f:
#                     self.profiles = json.load(f)
#             except Exception:
#                 self.profiles = {}
#         else:
#             self.profiles = {}

#     def _save_profiles(self):
#         with open(PROFILES_FILE, "w") as f:
#             json.dump(self.profiles, f, indent=4)

#     def _ensure_leader_entry(self, user_id):
#         if user_id not in self.leaderboard:
#             self.leaderboard[user_id] = {
#                 "single_best_time": None,
#                 "single_best_word": None,
#                 "multi_wins": 0,
#             }

#     # ---------- PUBLIC API FOR GAMES ----------

#     async def record_typewars_result(self, winner, mode, duration=None, word=None):
#         """
#         Called by games when TypeWars ends.
#         mode: "single" or "multi"
#         duration & word used for single-player best-time tracking.
#         """
#         user_id = str(winner.id)
#         self._ensure_leader_entry(user_id)
#         entry = self.leaderboard[user_id]

#         # Single-player: store best time + word
#         if mode == "single" and duration is not None and word:
#             if entry["single_best_time"] is None or duration < entry["single_best_time"]:
#                 entry["single_best_time"] = duration
#                 entry["single_best_word"] = word

#         # Multiplayer: increment wins
#         if mode == "multi":
#             entry["multi_wins"] += 1

#         self._save_leaderboard()

#         # Also bump profile total wins, if they have a profile
#         if user_id in self.profiles:
#             current_wins = self.profiles[user_id].get("wins", 0)
#             self.profiles[user_id]["wins"] = current_wins + 1
#             self._save_profiles()

#     # ---------- SLASH COMMANDS: WINS + PROFILE MENU ----------

#     @discord.app_commands.command(name="wins", description="Check your TypeWars stats")
#     @discord.app_commands.guilds(GUILD)
#     async def wins_slash(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)
#         entry = self.leaderboard.get(user_id)

#         if not entry:
#             await interaction.response.send_message(
#                 "❓ You haven't played TypeWars yet!", ephemeral=True
#             )
#             return

#         lines = []
#         if entry.get("single_best_time") is not None and entry.get("single_best_word"):
#             lines.append(
#                 "⏱️ Your fastest single-player time: **{0}s** on the word **{1}**.".format(
#                     entry["single_best_time"], entry["single_best_word"]
#                 )
#             )

#         multi = entry.get("multi_wins", 0)
#         lines.append("⌨️ You have **{0}** multiplayer TypeWars win(s)!".format(multi))

#         await interaction.response.send_message("\n".join(lines), ephemeral=True)

#     @discord.app_commands.command(
#         name="profile", description="Show profile commands and quick info"
#     )
#     @discord.app_commands.guilds(GUILD)
#     async def profile_help(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)
#         prof = self.profiles.get(user_id)
#         wins = self.leaderboard.get(user_id, {}).get("multi_wins", 0)

#         embed = discord.Embed(
#             title="Profile Menu",
#             description="Commands to manage your profile and view stats",
#             color=0x95A5A6,
#         )
#         embed.add_field(name="/create", value="Create your profile", inline=False)
#         embed.add_field(
#             name="/edit", value="Edit your username, bio, or favorite game", inline=False
#         )
#         embed.add_field(
#             name="/view", value="View your own profile or another user's", inline=False
#         )
#         embed.add_field(name="/delete", value="Delete your profile", inline=False)
#         embed.add_field(name="/wins", value="View your TypeWars stats", inline=False)

#         if prof:
#             embed.add_field(
#                 name="Current Profile",
#                 value=(
#                     "Username: **{0}**\nBio: {1}\nFavorite Game: {2}\n"
#                     "Total Wins (all games): {3}\nTypeWars Multiplayer Wins: {4}"
#                 ).format(
#                     prof.get("username", "N/A"),
#                     prof.get("bio", "N/A"),
#                     prof.get("favgame", "N/A"),
#                     prof.get("wins", 0),
#                     wins,
#                 ),
#                 inline=False,
#             )

#         await interaction.response.send_message(embed=embed, ephemeral=True)

#     # ---------- SLASH COMMANDS: PROFILE CRUD ----------

#     @discord.app_commands.command(name="create", description="Create your profile")
#     @discord.app_commands.guilds(GUILD)
#     async def create_profile(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)

#         if user_id in self.profiles:
#             await interaction.response.send_message(
#                 "You already have a profile.", ephemeral=True
#             )
#             return

#         await interaction.response.send_message(
#             "Let's create your profile in this channel.\n"
#             "Reply with your **username**.",
#             ephemeral=True,
#         )

#         def check(m):
#             return m.author == interaction.user and m.channel == interaction.channel

#         # Username
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Profile creation cancelled.", ephemeral=True
#             )
#             return
#         username = msg.content.strip()

#         await interaction.followup.send("Now send a short **bio**.", ephemeral=True)
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Profile creation cancelled.", ephemeral=True
#             )
#             return
#         bio = msg.content.strip()

#         await interaction.followup.send(
#             "Finally, what's your **favorite game**?", ephemeral=True
#         )
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Profile creation cancelled.", ephemeral=True
#             )
#             return
#         favgame = msg.content.strip()

#         self.profiles[user_id] = {
#             "username": username,
#             "bio": bio,
#             "favgame": favgame,
#             "wins": 0,
#         }
#         self._save_profiles()

#         await interaction.followup.send("✅ Profile saved!", ephemeral=True)

#     @discord.app_commands.command(name="edit", description="Edit your profile")
#     @discord.app_commands.guilds(GUILD)
#     async def edit_profile(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)

#         if user_id not in self.profiles:
#             await interaction.response.send_message(
#                 "You don't have a profile to edit.", ephemeral=True
#             )
#             return

#         await interaction.response.send_message(
#             "What do you want to edit? Type: `username`, `bio`, or `favgame`.",
#             ephemeral=True,
#         )

#         def check(m):
#             return m.author == interaction.user and m.channel == interaction.channel

#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Edit cancelled.", ephemeral=True
#             )
#             return

#         choice = msg.content.strip().lower()

#         if choice == "username":
#             await self._edit_username(interaction, user_id, check)
#         elif choice == "bio":
#             await self._edit_bio(interaction, user_id, check)
#         elif choice == "favgame":
#             await self._edit_favgame(interaction, user_id, check)
#         else:
#             await interaction.followup.send(
#                 "That isn't a valid option.", ephemeral=True
#             )

#     async def _edit_username(self, interaction, user_id, check):
#         await interaction.followup.send("Enter new username:", ephemeral=True)
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Username not changed.", ephemeral=True
#             )
#             return
#         new_username = msg.content.strip()
#         self.profiles[user_id]["username"] = new_username
#         self._save_profiles()
#         await interaction.followup.send(
#             "Your new username `{0}` is saved.".format(new_username), ephemeral=True
#         )

#     async def _edit_bio(self, interaction, user_id, check):
#         await interaction.followup.send("Enter new bio:", ephemeral=True)
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Bio not changed.", ephemeral=True
#             )
#             return
#         new_bio = msg.content.strip()
#         self.profiles[user_id]["bio"] = new_bio
#         self._save_profiles()
#         await interaction.followup.send(
#             "Your new bio is saved.", ephemeral=True
#         )

#     async def _edit_favgame(self, interaction, user_id, check):
#         await interaction.followup.send("Enter new favorite game:", ephemeral=True)
#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Favorite game not changed.", ephemeral=True
#             )
#             return
#         new_game = msg.content.strip()
#         self.profiles[user_id]["favgame"] = new_game
#         self._save_profiles()
#         await interaction.followup.send(
#             "Your new favorite game is saved.", ephemeral=True
#         )

#     @discord.app_commands.command(name="delete", description="Delete your profile")
#     @discord.app_commands.guilds(GUILD)
#     async def delete_profile(self, interaction: discord.Interaction):
#         user_id = str(interaction.user.id)

#         if user_id not in self.profiles:
#             await interaction.response.send_message(
#                 "You don't have a profile to delete.", ephemeral=True
#             )
#             return

#         username = self.profiles[user_id].get("username", "this user")
#         await interaction.response.send_message(
#             "Are you sure you want to delete **{0}**'s profile? (yes/no)".format(
#                 username
#             ),
#             ephemeral=True,
#         )

#         def check(m):
#             return m.author == interaction.user and m.channel == interaction.channel

#         try:
#             msg = await self.bot.wait_for("message", timeout=60, check=check)
#         except asyncio.TimeoutError:
#             await interaction.followup.send(
#                 "Timed out. Profile not deleted.", ephemeral=True
#             )
#             return

#         if msg.content.strip().lower() in ("yes", "y"):
#             del self.profiles[user_id]
#             self._save_profiles()
#             await interaction.followup.send(
#                 "Profile deleted.", ephemeral=True
#             )
#         else:
#             await interaction.followup.send(
#                 "Profile was not deleted.", ephemeral=True
#             )


# async def setup(bot):
#     print("Loading Profiles cog...")
#     await bot.add_cog(Profiles(bot))
