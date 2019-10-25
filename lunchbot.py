from io import StringIO
import os

from lxml.cssselect import CSSSelector
import lxml.etree
import slack
import requests


LUNCH_COMMANDS = ("obed", "oběd")
URLS = [*map(lambda p: f"https://www.menicka.cz/{p}.html", os.environ.get("PATHS", "").split(","))]


def fetch_menus(slack_client, channel):
    result = ""

    for url in URLS:
        response = requests.get(url)
        parser = lxml.etree.HTMLParser()
        tree = lxml.etree.parse(StringIO(response.text), parser)

        name = CSSSelector(".line1 h1")(tree)[0].text
        result += f"*{name}*\n"

        menu = CSSSelector(".menicka ul")(tree)[0]

        for child in CSSSelector("li .polozka")(menu):
            result += child.xpath("string()")
            result += "\n"

        result += "\n"

    slack_client.chat_postMessage(
        channel=channel,
        text=result
    )


@slack.RTMClient.run_on(event="message")
def handle_message(**payload):
    if any(command in payload["data"]["text"] for command in LUNCH_COMMANDS):
        fetch_menus(payload['web_client'], payload["data"]["channel"])


if __name__ == "__main__":
    slack_client = slack.RTMClient(token=os.environ["SLACK_TOKEN"])
    slack_client.start()

