from datetime import datetime

from tools.common import Tool
from utils.llm import get_response_content_from_gpt
from utils.logger import Logger
from utils.retry import retry


class TweetWriter(Tool):
    name = "tweet_writer"
    description = "This tool is use when you need to post a tweet to twitter"

    system_message = """You are a tweet writer. You always follow belows principles in writing engaging tweets.
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
    """

    def run(self, topic: str, detail: str = None) -> str:
        Logger.info(f"tool:{self.name} topic: {topic}, detail: {detail}")

        userProfile = {}
        audience = self.analyzeAudience(userProfile)
        tweet = self.generateContent(topic, detail, audience)
        # bestTime = self.calculateBestTimeToTweet(userProfile)
        self.postTweet(tweet)

        return f"Tweet successfully send.\n\nTweet Content:\n{tweet}"

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
                            "description": "The topic you want to tweet about.",
                        },
                        "detail": {
                            "type": "string",
                            "description": "Additional details you want to add to the tweet.",

                        },
                    },
                    "required": ["topic"]
                },

            }
        }

    def analyzeAudience(self, userProfile: dict):
        # audiencePreferences = getAudiencePreferences(userProfile)
        return {
            "categories": {
                "occupation": "engineer",
                "industry": "tech",
                "interests": ["technology", "programming", "gaming", "nature", "music", "sports", "travel", "food"],
                "preferable tone": ["casual", "modest", "humor"],
            }

        }

    @retry(max_attempts=3)
    def generateContent(self, topic, detail, audience):
        system_message = {"role": "system", "content": self.system_message}
        user_message = {"role": "user", "content": f"""Please help me to write a tweet.
         Topic: {topic}
         Detail: {detail}
         Audience: {audience}
         Current Time: {datetime.now()}"""}

        messages = [system_message, user_message]

        return get_response_content_from_gpt(messages)

    def calculateBestTimeToTweet(self, userProfile):
        pass

    def postTweet(self, tweet, bestTime=None):
        file = open('./tweet.txt', 'w')
        file.write(tweet)
        file.close()
