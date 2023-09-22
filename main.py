import discord
import json
import logging
from discord.ext import commands, tasks
import shlex
import random
import datetime
import asyncio
import time
from discord import ui
from discord import app_commands
from discord.ui import View, Button
from keep_alive import keep_alive
import os

# Initialize logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s')

# channel id for feedback
FEEDBACK_CHANNEL_ID = 1152534657456414810

# Load bot configuration from JSON
with open("config.json", "r") as config_file:
  config = json.load(config_file)

# Create bot instance
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())


# Load challenge data or return an empty data if file not found
def load_challenge_data():
  try:
    with open("challenge_data.txt", "r") as file:
      return json.load(file)
  except FileNotFoundError:
    logging.warning("Challenge data not found. Returning empty data.")
    return {}


# Save challenge data to a file
def save_challenge_data(data):
  with open("challenge_data.txt", "w") as file:
    json.dump(data, file)
  logging.info("Challenge data saved successfully.")


# Activities for bot presence
ACTIVITIES = [
    "Proving P = NP...", "Computing 6 x 9...", "Mining bitcoin...",
    "Dividing by 0...", "Initialising Skynet...", "[REDACTED]",
    "Downloading more RAM...", "Ordering 1s and 0s...",
    "Navigating neural network...", "Importing machine learning...",
    "Issuing Alice and Bob one-time pads...", "Mining bitcoin cash...",
    "Generating key material by trying to escape vim...",
    "for i in range(additional): Pylon()", "(creating unresolved tension...",
    "Symlinking emacs and vim to ed...", "Training branch predictor...",
    "Timing cache hits...", "Speculatively executing recipes...",
    "Adding LLM hallucinations...", "Cracking quantum encryption...",
    "Breaching mainframe...", "Accessing secret databases...",
    "Decompiling neural algorithms...", "Launching DDoS on Matrix...",
    "Rooting cyberspace...", "Bypassing firewall...",
    "Infiltrating digital fortress...", "Overriding security protocols...",
    "Decrypting alien communications...", "Running penetration tests...",
    "Compiling stealth trojans...", "Exploiting zero-day vulnerabilities...",
    "Activating VPN...", "Cloaking IP address...", "Hijacking satellite...",
    "Routing through proxies...", "Establishing darknet connection...",
    "Uploading virus to the Grid...", "Initializing worm propagation..."
]


# Task to change bot's activity every 30 minutes
@tasks.loop(minutes=30)
async def change_activity():
  activity = random.choice(ACTIVITIES)
  await bot.change_presence(activity=discord.Game(name=activity))
  logging.info(f"Activity set to: {activity}")


@bot.event
async def on_ready():
  logging.info(f'We have logged in as {bot.user}')
  try:
    synced = await bot.tree.sync()
    logging.info(f"Synced {len(synced)} command(s)...")
  except Exception as e:
    logging.error(f"Error syncing commands!: {e}")
  await change_activity.start()


#-------------------------------------------------------------- 

@bot.command()
async def start_challenge(ctx):
    # Send an ephemeral message to the user to start the challenge
    await ctx.send("Welcome to the challenge! Click ✅ to start.", ephemeral=True)

    # Add a reaction to the original message
    await ctx.send("Click ✅ to start.", ephemeral=True)
    start_message = await ctx.fetch_message(ctx.message.id)
    await start_message.add_reaction("✅")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == '✅' and reaction.message.id == start_message.id

    try:
        # Wait for the user to click the ✅ reaction
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)

        # Prompt for day
        await ctx.send("1. Enter the day:")
        day_response = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        # Prompt for challenge description
        await ctx.send("2. Enter the challenge description:")
        challenge_response = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        # Ask if the user wants to attach a file
        await ctx.send("Do you want to attach a file (yes/no)?")
        attach_file_response = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        attachments = []
        if attach_file_response.content.lower().strip() == 'yes':
            # Ask for the file attachment
            await ctx.send("Please attach the file you want to include:")
            file_message = await bot.wait_for('message', check=lambda message: message.author == ctx.author and message.attachments)

            # Add the attached files to the list
            for attachment in file_message.attachments:
                attachments.append(attachment.url)

        # Prompt for answer
        await ctx.send("3. Enter the answer:")
        answer_response = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        # Prompt for hints
        await ctx.send("4. Enter hints (optional):")
        hints_response = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

        response_message = f"Challenge data received:\nDay: {day_response.content}\nChallenge: {challenge_response.content}\nAnswer: {answer_response.content}\nHints: {hints_response.content}"
        
        if attachments:
            response_message += "\nAttachments:\n" + "\n".join(attachments)

        await ctx.send(response_message)

    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond!")
#--------------->2<--------------------------------------
class FeedbackModal(discord.ui.Modal, title="Set a new Challenge"):
  challenge_day = discord.ui.TextInput(
    style=discord.TextStyle.short,
    label="Set Day",
    required=False,
    placeholder="Day of the challenge"
  )
  challenge_description = discord.ui.TextInput(
    style=discord.TextStyle.long,
    label="Set Description",
    required=False,
    placeholder="Description of the challenge!"
  )
  challenge_answer = discord.ui.TextInput(
    style=discord.TextStyle.short,
    label="Set Answer",
    required=False,
    placeholder="Answer of the challenge"
  )
  challenge_hint = discord.ui.TextInput(
    style=discord.TextStyle.short,
    label="Set Hints",
    required=False,
    placeholder="Hints of the challenge"
  )
  challenge_Attachments = discord.ui.TextInput(
    style=discord.TextStyle.short,
    label="Link Attachments",
    required=False,
    placeholder="Past link of the  Attachment (GitHub)"
  )
  
# async def on_submit(self,interaction: discord.Interaction):
#  async def on_error(self,interaction: discord.interaction):

#<--------


@bot.tree.command()
async def set_c(interaction: discord.Interaction):
  feedback_modal = FeedbackModal()
  await interaction.response.send_modal(feedback_modal)
  




#---------------------------------------------------------------
@bot.command()
async def setchallenge(ctx, *, args=None):
  try:
    # A series of checks to validate challenge setting
    if str(ctx.author.id) not in config["ctf_creators"]:
      await ctx.send("You don't have permission to set a challenge!")
      logging.warning(f"Unauthorized challenge attempt by {ctx.author}")
      return
    elif not isinstance(ctx.channel, discord.DMChannel):
      await ctx.send("Please use this command in DMs!")
      logging.warning(f"{ctx.author} tried to submit in a non-DM channel.")
      return

    if not args:
      await ctx.send(
          "Usage: `/setchallenge day=<day_number> desc=\"<description>\" answer=\"<answer>\" hints=\"<hints>\"`"
      )
      return

    args_list = shlex.split(args)
    args_dict = {}
    for item in args_list:
      if '=' in item:
        key, value = item.split('=', 1)
        args_dict[key] = value
      else:
        await ctx.send("Invalid argument format. Use key=value pairs.")
        return

    required_args = ['day', 'desc', 'answer', 'hints']
    if not all(key in args_dict for key in required_args):
      await ctx.send("You're missing some arguments!")
      return

    challenge_data = {
        'master_id': ctx.author.id,
        'day': args_dict['day'],
        'desc': args_dict['desc'],
        'answer': args_dict['answer'],
        'hints': args_dict['hints'],
        'leaderboard': {},
        'start_time': str(datetime.datetime.now())
    }
    save_challenge_data(challenge_data)

    formatted_message = (
        f"**Day-{challenge_data['day']} Challenge by {ctx.author.name}:**\n"
        f"`{challenge_data['desc']}`")
    challenge_channel = bot.get_channel(int(config["channel_id"]))
    await challenge_channel.send(formatted_message)
    await ctx.send("Challenge set successfully!")
    await release_hints()
    await end_challenge()

  except Exception as e:
    logging.error(f"Error occurred in setchallenge: {e}")
    await ctx.send(f"An error occurred: {e}")


async def display_leaderboard():
  challenge_data = load_challenge_data()
  position_emojis = ["🥇", "🥈", "🥉"]
  sorted_leaderboard = sorted(challenge_data['leaderboard'].items(),
                              key=lambda x: x[1])
  leaderboard_msg = "🏆 **The winners of today's CTF (Day-{day}) are:** 🏆\n"
  for i, (user_id, _) in enumerate(sorted_leaderboard[:3]):
    user = bot.get_user(int(user_id))
    leaderboard_msg += f"{position_emojis[i]} {user.name}\n"
  challenge_channel = bot.get_channel(int(config["channel_id"]))
  await challenge_channel.send(
      leaderboard_msg.format(day=challenge_data['day']))


async def end_challenge():
  challenge_data = load_challenge_data()
  if "start_time" in challenge_data:
    start_time = datetime.datetime.fromisoformat(challenge_data["start_time"])
    elapsed_time = datetime.datetime.now() - start_time
    remaining_time = 86400 - elapsed_time.total_seconds()

    # 24 hours minus elapsed time
    if remaining_time > 0:
      await asyncio.sleep(remaining_time)
  else:
    await asyncio.sleep(86400)

  challenge_channel = bot.get_channel(int(config["channel_id"]))
  await challenge_channel.send(
      f"Day-{challenge_data['day']} Challenge has finished!")
  logging.info(f"Day-{challenge_data['day']}challenge has been finished...")
  await challenge_channel.send(
      f"The answer for Day-{challenge_data['day']} was: ||`{challenge_data['answer']}`||"
  )

  # reset challenge data
  save_challenge_data({})


#----------------------------------------------------

#---------------------------------------------------


@bot.tree.command(name="submit", description="Used to Submit flag.")
@app_commands.describe(flag="Enter your flag here.")
async def submit(interaction: discord.Interaction, flag: str):
  challenge_data = load_challenge_data()

  # Check if challenge is active
  if not challenge_data:
    await interaction.response.send_message(
        "There's no active challenge right now!", ephemeral=True)
    return
  if 'answer' in challenge_data:
    if str(interaction.user.id) in challenge_data['leaderboard']:
      await interaction.response.send_message(
          "You've already submitted the correct answer!", ephemeral=True)
      return
  # Check if answer matches
  if 'answer' in challenge_data and challenge_data['answer'] == flag:
    if str(interaction.user.id) not in challenge_data['leaderboard']:
      challenge_data['leaderboard'][str(
          interaction.user.id)] = datetime.datetime.utcnow().strftime(
              '%Y-%m-%d %H:%M:%S')
      save_challenge_data(challenge_data)

      # Notify the challenge creator
      master = bot.get_user(challenge_data['master_id'])
      if master:
        await master.send(f"{interaction.user.name} just solved the challenge!"
                          )

      # Check for "First Blood"
      if len(challenge_data['leaderboard']) == 1:
        challenge_channel = bot.get_channel(int(config["channel_id"]))
        await challenge_channel.send(
            f"🚩 First Blood! {interaction.user.mention} just stormed today's challenge and captured the flag in record time! The challenge stands defeated! Let the games intensify! 💥🔥🎉"
        )
        await interaction.response.send_message(
            "Congratulations for topping the leaderboard!", ephemeral=True)

      # Display leaderboard if 3 users have submitted
      if len(challenge_data['leaderboard']) == 3:
        await display_leaderboard()

      elif len(challenge_data['leaderboard']) > 3:
        await interaction.response.send_message(
            f"Correct answer! You're in position {len(challenge_data['leaderboard'])}. Try harder next time to get on the leaderboard."
        )

    else:
      await interaction.response.send_message("You've already submitted!",
                                              ephemeral=True)

  else:
    await interaction.response.send_message("Wrong answer! Try again.",
                                            ephemeral=True)


@bot.command()
async def shutdown(ctx):
  if str(ctx.author.id) not in config[
      "ctf_creators"]:  # Checking if the user is allowd to do the action or not.
    await ctx.send("You don't have permission to shutdown the challenge!")
    logging.warning(f"Unauthorized challenge shutdown attempt by {ctx.author}")
    return

  challenge_data = load_challenge_data()
  if not challenge_data:
    await ctx.send("No active challenge to shut down.")
    return
  position_emojis = ["🥇", "🥈", "🥉"]
  challenge_channel = bot.get_channel(int(config["channel_id"]))
  # Print leaderboard
  if challenge_data['leaderboard']:
    await display_leaderboard()
  else:
    await challenge_channel.send("No one has solved the challenge yet.")
  # Print the correct answer
  await challenge_channel.send(
      f"Correct answer for Day-{challenge_data['day']} was: `{challenge_data['answer']}`"
  )

  # Reset challenge data
  save_challenge_data({})
  await challenge_channel.send(
      "Challenge has been shut down and leaderboard has been printed.")


async def release_hints():
  challenge_data = load_challenge_data(
  )  # Loading the json file for the start_time object
  if "start_time" in challenge_data:
    start_time = datetime.datetime.fromisoformat(challenge_data["start_time"])
    elapsed_time = datetime.datetime.now() - start_time
    remaining_time = 21600 - elapsed_time.total_seconds(
    )  # 6 hours minus elapsed time
    if remaining_time > 0:
      await asyncio.sleep(remaining_time)
  else:
    await asyncio.sleep(21600)
  if not challenge_data.get('hints_revealed',
                            False) and not challenge_data['leaderboard']:
    challenge_channel = bot.get_channel(int(config["channel_id"]))
    await challenge_channel.send(
        f"Hint for Day-{challenge_data['day']}: `{challenge_data['hints']}`")
    challenge_data['hints_revealed'] = True
    save_challenge_data(challenge_data)


@bot.tree.command(name="ping", description="Check if the bot is alive or not.")
async def _ping(interaction: discord.Interaction):
  message = await interaction.response.send_message("Pong!")


@bot.command(pass_context=True)
async def ping(ctx):
  """ Pong! """
  before = time.monotonic()
  message = await ctx.send("Pong!")
  ping = (time.monotonic() - before) * 1000
  await message.edit(content=f"Pong!  `{int(ping)}ms`")
  print(f'Ping {int(ping)}ms')


@bot.tree.command(name="feedback",
                  description="Submit feedback, bugs, or suggestions.")
@app_commands.describe(feedback="Your feedback, suggestion, or bug report.")
async def _feedback(interaction: discord.Interaction, feedback: str):
  """Handles the feedback interaction."""

  # Fetch the feedback channel
  feedback_channel = bot.get_channel(FEEDBACK_CHANNEL_ID)

  # Check if feedback_channel is not None and is of type TextChannel
  if feedback_channel and isinstance(feedback_channel, discord.TextChannel):
    embed = discord.Embed(title="New Feedback!",
                          description=feedback,
                          color=0x00ff00)
    embed.set_author(name=interaction.user.name,
                     icon_url=interaction.user.avatar.url)

    # Send the feedback to the feedback channel
    await feedback_channel.send(embed=embed)
    await interaction.response.send_message(
        "Thank you for your feedback!, Join Official bot server to check the status of your feedback here: https://discord.gg/NB6aXA9gsE",
        ephemeral=True)
  else:
    logging.warning(
        f"Feedback channel with ID {FEEDBACK_CHANNEL_ID} not found or not of type TextChannel!"
    )
    await interaction.response.send_message(
        "Failed to send feedback. [Contact Creator](https://discordapp.com/users/1057228474152140842)"
    )


# Overriding default discord help messsage for our very own embeded one.
bot.remove_command('help')


# Custom help command
@bot.command(name='help', aliases=['h', 'commands'])
async def help_command(ctx):
  embed = discord.Embed(title="Help",
                        description="List of available commands",
                        color=0x55a7f7)

  # For regular users
  regular_commands = """
    `/submit <flag>`: Submit the CTF flag.
    `/ping : Checks the latency in ms`
    """
  embed.add_field(name="Regular Commands",
                  value=regular_commands,
                  inline=False)

  # For admins
  #--------------
  #@bot.tree.command(name="/setchallenge", description="Set up a CTF challenge.")
  #-----------
  if str(ctx.author.id) in config["ctf_creators"]:
    admin_commands = """
        `/setchallenge ...`: Set up a CTF challenge.
        `/shutdown`: Shut down the active CTF challenge.
        """
    embed.add_field(name="Admin Commands", value=admin_commands, inline=False)

  await ctx.send(embed=embed)


keep_alive()
try:
  bot.run(config["token"])
except discord.errors.HTTPException:
  logging.error("Being Rate Limited!")
  os.system("kill 1")
  os.system("python restart.py")
