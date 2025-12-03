import discord

class Tournament:
    def __init__(self, bot):
        self.bot = bot
        self.players = []

    async def start(self, interaction: discord.Interaction):
        self.players = []
        await interaction.response.send_message(
            "🏆 Starting a new tournament! How many players will participate? (type a number)"
        )

        def check_number(m):
            return m.author == interaction.user and m.channel == interaction.channel and m.content.isdigit()

        try:
            msg = await self.bot.wait_for("message", check=check_number, timeout=30.0)
            num_players = int(msg.content)
        except:
            await interaction.followup.send("⏰ Time’s up or invalid number. Tournament cancelled.")
            return

        await interaction.followup.send(f"Great! {num_players} player(s). Please type each player's name one by one:")

        for i in range(num_players):
            def check_name(m):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                name_msg = await self.bot.wait_for("message", check=check_name, timeout=30.0)
            except:
                await interaction.followup.send("⏰ Time’s up. Tournament cancelled.")
                return

            self.players.append(name_msg.content.strip())
            await interaction.followup.send(f"Added player: {name_msg.content.strip()}")

        await interaction.followup.send(f"✅ Tournament setup complete! Players: {', '.join(self.players)}")


def setup(bot):
    tournament = Tournament(bot)

    @bot.tree.command(name="tournament", description="Start a new tournament")
    async def start_tournament(interaction: discord.Interaction):
        await tournament.start(interaction)
