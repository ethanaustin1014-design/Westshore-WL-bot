import discord
from discord import app_commands
from discord.ext import commands

# ---------------- CONFIGURATION ----------------
# Roles to give to the target user upon whitelist
ROLE_IDS_TO_ADD = [
    1563610471934984244,
    1563610472211554487
]

# Roles allowed to execute the /whitelist command
ALLOWED_STAFF_ROLE_IDS = [
    1563610472312213597,
    1563610472329257080,
    1563633264810262741
]
# -----------------------------------------------

intents = discord.Intents.default()
intents.members = True  # Required to edit member roles and nicknames

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    try:
        # Syncs slash commands globally across all servers the bot is in
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="whitelist", description="Whitelist a user, change their nickname, and assign roles.")
@app_commands.describe(
    target="The member to whitelist",
    rp_name="The Roleplay Name to set as their nickname"
)
async def whitelist(interaction: discord.Interaction, target: discord.Member, rp_name: str):
    # Check if the user executing the command has at least one required staff role
    user_role_ids = [role.id for role in interaction.user.roles]
    has_permission = any(role_id in user_role_ids for role_id in ALLOWED_STAFF_ROLE_IDS)

    if not has_permission:
        await interaction.response.send_message(
            "❌ You do not have permission to use this command.",
            ephemeral=True
        )
        return

    # Defer response in case updating nick/roles takes a second
    await interaction.response.defer(ephemeral=False)

    try:
        # 1. Update target's nickname
        await target.edit(nick=rp_name)

        # 2. Fetch and assign the specified roles
        roles_to_assign = []
        for role_id in ROLE_IDS_TO_ADD:
            role = interaction.guild.get_role(role_id)
            if role:
                roles_to_assign.append(role)

        if roles_to_assign:
            await target.add_roles(*roles_to_assign)

        # 3. Send confirmation message
        await interaction.followup.send(
            f"✅ **{target.mention}** has been whitelisted!\n"
            f"• **RP Name:** `{rp_name}`\n"
            f"• **Roles Added:** {', '.join([r.mention for r in roles_to_assign])}"
        )

    except discord.Forbidden:
        await interaction.followup.send(
            "⚠️ **Error:** I don't have permission to modify this user's nickname or assign these roles. "
            "Please ensure my bot role is placed higher than the target user and the roles being assigned in your Server Settings."
        )
    except Exception as e:
        await interaction.followup.send(f"⚠️ An unexpected error occurred: {e}")

# Replace with your actual bot token
bot.run("MTU2MzkxOTExNjI3MDU2NzUxNg.GGm5np._tLZOemotHhgaIyI9sXwLJ39i147hBklswYfTI")