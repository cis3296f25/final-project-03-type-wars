# "Type Wars"

‘Type Wars’ would be a Discord bot designed to implement multiple typing-based games. There would be three modes, both can be played as a single player, or multiplayer. Game #1, the player/s is/are given a word and must spell it letter by letter between messages. Game #2, player/s is/are given a definition, length of said word, and must spell out what the word is. Game #3, player/s is/are given a word and must type it the fastest (this game mode would include longer words that are harder to spell off a whim).

<img width="1558" height="373" alt="image" src="https://github.com/user-attachments/assets/785e72d6-37e5-4a0a-9e2e-a77bab330089" />

Background

‘Type War’ should preferably be played on an empty channel, to avoid the spamming of messages in regularly used channels. There are two ways to activate the bot, depending on if one wants to play as a single player, or multiplayer.
As a single player, you can activate the bot with /tw. Different commands, like /tw list, will show what games can be played and their descriptions. Choosing /tw (1, 2 or 3) will activate the game in single player mode.
For multiplayer mode, player #1 must mention player #2 in a Discord message, as well as the command.
Ex. /tw @player#2 (1, 2, or 3)
Once the message is sent out, player #2 must accept the challenge before the game proceeds. If player #2 doesn’t respond within 1 minute, the bot will cancel the request.

Required Resources

Language: Python
API: discord.py
Creating a Bot account: https://discordpy.readthedocs.io/en/stable/discord.html
Discord Developer Portal: https://discord.com/developers/docs/intro

Testing

To run and test the TypeWars bot, make sure a few items are properly set up first:

- The python modules dotenv and discord are installed using:
  pip install dotenv
  pip install discord
- The .env file is correctly named, contains the correct token, contains no brackets/braces, and exists in the TYPE-WARS root directory alongside type-wars-bot.py and the rest of the code
- Your settings.json [Ctrl+Shift+P -> Open User Settings] contains the following lines right before the last brace:
  "python.terminal.activateEnvironment" : true,
  "python.terminal.useEnvFile" : true

Then, run the following command in the TYPE-WARS root directory:
py type-wars-bot.py

The bot should come online on Discord and respond to queries in the #testing channel!
