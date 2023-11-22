import json
from typing import Literal

from tools.common import Tool, ToolCallResult
from utils.llm import get_response_content_from_gpt
from utils.logger import Logger

separator = "\n`````\n"


class EmailWriter(Tool):
    name: str = "email_writer"
    description: str = "This is very helpful if you need to write email"

    file_name: str = "./email.txt"

    async def run(self, recipient: str, subject: str, requirements: str, email_type=Literal["business", "personal"],
                  draft_email="", email_confirmation=False, other_information: str = None) -> ToolCallResult:
        Logger.info(
            f"tool:{self.name} recipient: {recipient}, subject: {subject}, requirements: {requirements}, other_information: {other_information}")

        etiquette = self._get_business_email_etiquette() if email_type == "business" else self._get_personal_etiquette()
        system_message = {"role": "system", "content": f"""You are a email writer. You always follow belows principles in writing
        a email:
        Before drafting your email, consider the following:
        Identify The Purpose: Clearly define the reason for your email. It could be a concern, a suggestion, or a request.
        Gather Relevant Information: If your email is about a specific incident or person, gather all the pertinent details.
        Be Respectful: Remember that you’re addressing an authority figure. Maintain a respectful tone throughout your email.
        
        {etiquette}"""}

        if email_confirmation is False:
            recipient = f"Recipient: {recipient}\n"
            subject = f"Subject: {subject}\n"
            requirements = f"Email Requirements: {requirements}\n"
            other_information = f"Other Information: {other_information}\n" if other_information else ""

            user_message = {"role": "user", "content": f"""Please help me to write a email.
                     {recipient}{subject}{requirements}{other_information}"""} if draft_email == "" else {
                "role": "user", "content": f"""Please help me to refine the following email base on the the information,
                {recipient}{subject}{requirements}{other_information}
                
                Draft Email:
                {draft_email}"""}

            response = await get_response_content_from_gpt([system_message, user_message])
            return ToolCallResult(result=json.dumps({
                "status": "draft",
                "content": response,
                "next_step": "ask user to confirm the draft email"
            }))
        else:

            self._send(recipient, subject, draft_email)

            return ToolCallResult(result=json.dumps({
                "status": "success",
                "content": draft_email,
                "next_step": "send email"
            }))

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
                        "recipient": {
                            "type": "string",
                            "description": "The recipient of the email.",
                        },
                        "subject": {
                            "type": "string",
                            "description": "The subject of the email.",
                        },
                        "requirements": {
                            "type": "string",
                            "description": "The requirements of the email.",
                        },
                        "other_information": {
                            "type": "string",
                            "description": "The others of the email.",
                        },
                        "email_type": {
                            "type": "string",
                            "enum": ["business", "personal"],
                            "description": "The type of the email.",
                            "default": "personal"
                        },
                        "draft_email": {
                            "type": "string",
                            "description": "The drafted email",
                            "default": ""
                        },
                        "email_confirmation": {
                            "type": "boolean",
                            "description": "User has confirm the draft email.",
                            "default": False
                        },
                    },
                    "required": ["recipient", "subject", "requirements", "email_type", "draft_email",
                                 "email_confirmation"]
                },

            }
        }

    def _get_business_email_etiquette(self) -> str:
        return """This is a business email. Remember the following business email etiquettes,
        1. Use a direct subject line. Strong subject lines are brief, descriptive, and whenever possible, action-oriented. For example, \"Board Meeting moved to Tuesday, 11/21\"
        2. Use professional greetings. \"Dear Mr. Smith\" or \"Hello, Mr. Smith\" are appropriate greetings and use "Sincerely" "Kind regards" or "Best wishes" for sign-off.
        3. Be wary of excessive exclamation points. 
        4. Don't use emojis.
        5. Keep your tone professional. Use positive words, such as \"opportunities\" and \"challenges,\" instead of \"obstacles\" and \"limitations.\""""

    def _get_personal_etiquette(self) -> str:
        return """The email should include:
        Subject Line: Make it concise and informative. The subject line should summarize the purpose of your email.
        Salutation: Address the principal formally, using their correct title and surname.
        Introduction: Introduce yourself and your relationship to the school (e.g., parent, student).
        Body of Email: State your purpose for writing. Be clear, concise, and respectful.
        Closing: Express your appreciation for their time and request any necessary follow-up action. Sign off politely."""

    def _send(self, recipient: str, subject: str, email: str):
        file = open(self.file_name, "a")  # append mode
        file.write(email + separator)
        file.close()
