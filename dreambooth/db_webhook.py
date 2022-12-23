from typing import Union
from enum import Enum
import hashlib


class DreamboothWebhookTarget(Enum):
    UNKNOWN = 1
    DISCORD = 2


def test_webhook(url: str) -> str:
    if len(url) <= 0:
        return "Invalid webhook url."

    target = __detect_webhook_target(url)
    if target == DreamboothWebhookTarget.DISCORD:
        return __test_discord(url)

    return "Unsupported target."


def send_training_update(
    url: str,
    image,
    model_name: str,
    prompt: str,
    training_step: Union[str, int],
    global_step: Union[str, int],
):
    target = __detect_webhook_target(url)
    if target == DreamboothWebhookTarget.DISCORD:
        __send_discord_training_update(url, image, model_name, prompt, training_step, global_step)


def is_valid_notification_target(url: str) -> bool:
    return __detect_webhook_target(url) != DreamboothWebhookTarget.UNKNOWN


def __detect_webhook_target(url: str) -> DreamboothWebhookTarget:
    if url.startswith("https://discord.com/api/webhooks/"):
        return DreamboothWebhookTarget.DISCORD
    return DreamboothWebhookTarget.UNKNOWN


def __test_discord(url: str) -> str:
    import discord_webhook

    discord = discord_webhook.DiscordWebhook(url, username="Dreambooth")
    discord.set_content("This is a test message from the A1111 Dreambooth Extension.")

    response = discord.execute()
    if response.ok:
        return "Test successful."

    return "Test failed."


def __send_discord_training_update(
    url: str,
    image,
    model_name: str,
    prompt: str,
    training_step: Union[str, int],
    global_step: Union[str, int],
):
    import discord_webhook

    discord = discord_webhook.DiscordWebhook(url, username="Dreambooth")
    out = discord_webhook.DiscordEmbed(color="C70039")

    out.set_author(name=model_name, icon_url="https://avatars.githubusercontent.com/u/1633844")
    out.set_timestamp()

    out.add_embed_field(name="Prompt", value=prompt, inline=False)
    out.add_embed_field(name="Session Step", value=training_step)
    out.add_embed_field(name="Global Step", value=global_step)

    attachment_bytes = image.tobytes()
    attachment_id = hashlib.sha1(attachment_bytes).hexdigest()
    attachment_name = f"{attachment_id}.png"

    discord.add_file(file=attachment_bytes, filename=attachment_name)
    out.set_image(f"attachment://{attachment_name}")

    discord.add_embed(out)
    discord.execute()