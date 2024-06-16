import discord
from discord.ui import Modal, InputText
from database import insert_alert, count_alerts_for_guild

class PriceAlertModal(Modal):
    def __init__(self, game_id: str, game_title: str):
        super().__init__(title="Set Price Alert")
        self.game_id = game_id 
        self.game_title = game_title
        self.target_price = InputText(
            label="Target Price",
            placeholder="Enter a target price",
            style=discord.InputTextStyle.short
        )
        self.add_item(self.target_price)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild_id
        channel_id = interaction.channel_id
        try:
            target_price = float(self.target_price.value)
        except ValueError:
            await interaction.response.send_message(
                "The target price must be a number. Please try again.",
                ephemeral=True
            )
            return
        
        alert_count = await count_alerts_for_guild(guild_id)
        if alert_count >= 10:
            await interaction.response.send_message(
                "This guild has reached the limit of 10 alerts.", 
                ephemeral=True
            )
        
        else:    
            # Insert data into the database with game_id
            response = await insert_alert(
                user_id, 
                guild_id, 
                channel_id, 
                target_price, 
                self.game_id,
                self.game_title
            )
            
            if response.data:
                await interaction.response.send_message(
                    f"Alert set successfully for {self.game_title} target price: {target_price}", 
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"Failed to set alert. Please try again.", 
                    ephemeral=True
                )