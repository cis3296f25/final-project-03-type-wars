from ast import Delete
from discord import app_commands, interactions, user
from discord.ext.commands import bot
from dotenv import load_dotenv
import discord

#DictStorage
profiles = {}

if os.path.exists("profiles.json"):
    with open("profiles.json", "r") as f:
        profiles = json.load(f)

#save function for profiles to json file
def saveProfiles():
    with open("profiles.json", "w") as f:
        json.dump(profiles, f, indent=4)


#Profile Feature
#ProfileManager
@bot.command(name="create", description="Create your profile", guild=GUILD_ID)
async def create(ctx):
	userID = str(ctx.author.id)
	#check if ID user exists already, if not say profile already exists and close func/command
	if userID in profiles:
		await ctx.send("User already has a profile")
	else:
		await ctx.send("Enter Username")
		response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
		#check the response and why it isn't working
		username = response.content
		#check to see if username already exists, print try again
		await ctx.send(f"Your username {username} is Saved")
		
		await ctx.send("Enter Bio")
		response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
		bio = response.content
		await ctx.send(f"Your Bio {bio} is Saved")
		
		await ctx.send("Enter Favorite Game")
		response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
		favgame = response.content
		await ctx.send(f"Your Favorite Game {favgame} is Saved")
		
		profiles[userID] = {"username": username, "bio": bio, "favgame": favgame}
		saveProfiles()
		await ctx.send("Profile Saved")

@bot.command(name="edit", description="Edit your profile", guild=GUILD_ID)
async def edit(ctx):
	#get ID
	userID = str(ctx.author.id)
	#check if profile exists
	if userID not in profiles:
		await ctx.send("User does not have a profile to edit")
	#ask user what they want to edit, parse it
	else:
		await ctx.send(f"What do you want to edit in your profile? Type: username, bio, OR fav game")
		response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
		#use if/else to call funcs
		choice = response.content.lower()
		if choice == "username":
			await EditUsername(ctx, userID)
		elif choice == "bio":
			await EditBio(ctx, userID)
		elif choice == "favgame":
			await EditFavGame(ctx, userID)
		else:
			await ctx.send("This is an invalid option")

async def EditUsername(ctx, userID):
	await ctx.send("Enter New Username")
	response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	newUsername = response.content
	profiles[userID]["username"] = newUsername
	saveProfiles()
	await ctx.send("Your New Username {newUsername} is Saved")

async def EditBio(ctx, userID):
	await ctx.send("Enter New Bio")
	response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	newBio = response.content
	profiles[userID]["bio"] = newBio
	saveProfiles()
	await ctx.send("Your New Bio {newBio} is Saved")

async def EditFavGame(ctx, userID):
	await ctx.send("Enter New Favorite Game")
	response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	newGame = response.content
	profiles[userID]["favgame"] = newGame
	saveProfiles()
	await ctx.send("Your New Favorite Game {newGame} is Saved")

@bot.command(name="delete", description="Delete your entire profile", guild=GUILD_ID)
async def delete(ctx):
	userID = str(ctx.author.id)
	#check if user profile exists, try and use if/else from profile func

	if userID not in profiles:
			await ctx.send("User does not have a profile to delete")
	else:
		username = profiles[userID].get("username")
		await ctx.send(f"Are you sure you want to delete this, {username}, entire profile?  yes/no")
		response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
		if response.content.lower() in ["yes", "y"]:
			del profiles[userID]
			saveProfiles()
			await ctx.send("This profile has been deleted")
		elif response.content.lower() in ["no", "n"]:
			await ctx.send(f"{username}’s profile was not deleted")

@bot.command(name="view", description="View your profile", guild=GUILD_ID)
async def view(ctx):
	userID = str(ctx.author.id)
	await ctx.send("Do you want to view your profile OR another user? type: mine OR (username)")
	response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)

	user = response.content.strip()
	if user.lower() == "mine":
		print("calling view profile")
		await ViewProfile(ctx, userID)
		return
	elif user != "mine":
		username = response.content.strip()
		print("calling view other prof")
		await ViewOtherProf(ctx, username)
		return
	#else:
		#await ctx.send("That is an invalid username")
	#call the funcs, use right arguements/parameters



async def ViewProfile(ctx, userID):
	print("in profile")
	if userID not in profiles:
		await ctx.send("You don't have a profile yet!")
		return
	profile = profiles[userID]

	embed = discord.Embed(title=f"{profile['username']}’s Profile")
	embed.add_field(name="Bio: ", value=profile["bio"], inline=False)
	embed.add_field(name="Favorite Game: ", value=profile["favgame"], inline=False)
	#embed.add_field(name = "Stats: ", value = profile["stats"])

	await ctx.send(embed=embed)

async def ViewOtherProf(ctx, username):
    #see how to see other users profile from username
	userID = None
	username = username.strip().replace("@", "")

	for IDs, profile in profiles.items():
		if profile["username"].lower() == username:
			userID = IDs
			break
	#if not in the profiles list, say user does not have a profile
	if userID is None:
		await ctx.send("This user does not have a profile")
	else:
		await ViewProfile(ctx, userID)

#CommandMenu
@bot.command(name="profile", description="View Commands to Manage Profiles", guild=GUILD_ID)
async def profile(ctx):
	userID = str(ctx.author.id)

	embed = discord.Embed(title="Profile Help Menu",  description="Commands to manage your profile")
	embed.add_field(name="/create", value="Create your profile", inline=False)
	embed.add_field(name="/edit", value="Edit your username, bio, or favorite game", inline=False)
	embed.add_field(name="/view", value="View our own profile or other users", inline=False)
	embed.add_field(name="/delete", value="Delete your profile", inline=False)

    
	await ctx.send(embed=embed)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)