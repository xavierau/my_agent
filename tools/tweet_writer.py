import json
import os
import time
from dataclasses import Field
from datetime import datetime

import requests
from requests_oauthlib import OAuth1Session

from tools.common import Tool, ToolCallResult
from tools.twitter import Twitter
from utils.llm import get_response_content_from_gpt
from utils.logger import Logger
from utils.retry import retry


class SimpleTweetWriter(Tool):
    name: str = "tweet_writer"
    description: str = "This tool is use when you need to post a tweet to twitter"
    file_path: str = "./tweet.txt"
    twitter: Twitter = Twitter()

    class Config:
        arbitrary_types_allowed = True

    system_message: str = """You are a tweet writer. You always follow belows principles in writing engaging tweets.
    Know Your Audience: Understand who your followers are and what they care about. This helps in tailoring your content to their interests.
    Keep it Concise: Twitter limits tweets to 280 characters. Make every word count. Be clear, direct, and to the point.
    Use Visuals: Images, videos, and GIFs can make your tweets more engaging. Visual content tends to attract more views, likes, and retweets.
    Engage in Trending Topics: Participate in trending conversations or use trending hashtags (but only if they are relevant to your content). This can increase the visibility of your tweets.
    Add Value: Share useful information, insightful opinions, or entertaining content. People are more likely to engage with tweets that offer them something valuable.
    Ask Questions: This encourages your followers to interact with your tweet, increasing engagement through replies.
    Use Humor (When Appropriate): Funny tweets tend to get more engagement, but make sure the humor is appropriate for your audience and brand.
    Be Authentic: Authenticity resonates with people. Show your personality in your tweets.
    Timing Matters: Tweet when your audience is most active. This can vary depending on your audience demographic and time zone.
    Use Hashtags Wisely: Hashtags increase the discoverability of your tweets but use them judiciously. Too many can seem spammy.
    Engage with Replies: Respond to comments on your tweets. This not only boosts engagement but also shows that you value your audience's input.
    Promote Interaction: Encourage retweets, shares, and tags. This can be through contests, questions, or direct calls to action.
    
    Always create hashtags for your tweets and put them at the end of the tweet.
    Finally, remember twitter does not support markdown, only plain text.
    """

    async def run(self, topic: str, detail: str = None, image_url=None) -> ToolCallResult:
        Logger.info(f"tool:{self.name} topic: {topic}, detail: {detail}, image_url: {image_url}")

        user_profile = {}
        audience = self.analyze_audience(user_profile)
        tweet = await self.generate_content(topic, detail, audience, image_url)
        # best_time = self.calculate_best_time_to_tweet(user_profile)
        await self.post_tweet(tweet, media=image_url)

        return ToolCallResult(result=tweet)

    @property
    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The main topic you want to tweet about.",
                        },
                        "detail": {
                            "type": "string",
                            "description": "Additional information for tweet generation.",
                        },
                        "image_url": {
                            "type": "string",
                            "description": "The image url that required to post with the tweet together.",
                        }
                    },
                    "required": ["topic"]
                },
            }
        }

    def analyze_audience(self, user_profile: dict):
        # audiencePreferences = getAudiencePreferences(user_profile)
        return {
            "categories": {
                "occupation": "engineer",
                "industry": "tech",
                "interests": ["technology", "programming", "gaming", "nature", "music", "sports", "travel", "food"],
                "preferable tone": ["casual", "modest", "humor"],
            }

        }

    @retry(max_attempts=3)
    async def generate_content(self, topic, detail, audience, image_url=None) -> str:

        print("generate content")

        system_message = {"role": "system", "content": self.system_message}
        user_message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""Please help me to write a tweet.
                            Topic: {topic}
                            Detail: {detail}
                            Audience: {audience}
                            Current Time: {datetime.now()}"""
                }
            ]
        }

        messages = [system_message, user_message]

        if image_url is not None:
            user_message['content'].append({
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": "high"
                }
            })

            print("use vision with url:", user_message['content'])

            return await get_response_content_from_gpt(messages,
                                                       model_name="gpt-4-vision-preview",
                                                       max_tokens=1000)

        return await get_response_content_from_gpt(messages)

    def calculate_best_time_to_tweet(self, user_profile):
        pass

    async def post_tweet(self, tweet, media=None, best_time=None):
        response = await self.twitter.publish_tweet(tweet, media)
        self.save_action(response)

    def save_action(self, response: dict):
        read_file = open(self.file_path, "r")
        content = read_file.read()
        read_file.close()

        try:
            content = json.loads(content)
        except:
            content = []

        content.append(response)

        write_file = open(self.file_path, "w")

        write_file.write(json.dumps(content))

        write_file.close()
