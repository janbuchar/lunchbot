import asyncio
from io import StringIO
import os

from lxml.cssselect import CSSSelector
import lxml.etree
import slack
import requests


LUNCH_COMMANDS = ("obed", "oběd")
URLS = [*map(lambda p: f"https://www.menicka.cz/{p}.html", os.environ.get("PATHS", "").split(","))]


async def fetch_menus(rtm_client, web_client, channel):
    await rtm_client.typing(channel=channel)

    for url in URLS:
        result = ""

        response = requests.get(url)
        parser = lxml.etree.HTMLParser()
        tree = lxml.etree.parse(StringIO(response.text), parser)

        name = CSSSelector(".line1 h1")(tree)[0].text
        result += f"*{name}*\n"

        menu = CSSSelector(".menicka ul")(tree)[0]

        for child in CSSSelector("li .polozka")(menu):
            result += child.xpath("string()")
            result += "\n"

        await web_client.chat_postMessage(
            channel=channel,
            text=result
        )



@slack.RTMClient.run_on(event="message")
async def handle_message(**payload):
    web_client = payload['web_client']
    rtm_client = payload['rtm_client']
    text = payload["data"]["text"]
    channel = payload["data"]["channel"]

    if any(command in text.lower() for command in LUNCH_COMMANDS):
        await fetch_menus(rtm_client, web_client, channel)


async def main():
    slack_client = slack.RTMClient(token=os.environ["SLACK_TOKEN"], run_async=True)
    await slack_client.start()


if __name__ == "__main__":
    asyncio.run(main())

