from tools.common import Tool
from utils.llm import get_response_content_from_gpt
from utils.logger import Logger

separator = "\n`````\n"


class EmailWriter(Tool):
    name = "email_writer"
    description = "This is very helpful if you need to write email"

    file_name = "./email.txt"

    def run(self, recipient: str, subject: str, requirements: str, other_information: str = None) -> str:
        Logger.info(f"tool:{self.name} recipient: {recipient}, subject: {subject}, requirements: {requirements}, other_information: {other_information}")

        system_message = {"role": "system", "content": """You are a email writer. You always follow belows principles in writing
        a email:
        Before drafting your email, consider the following:
        Identify The Purpose: Clearly define the reason for your email. It could be a concern, a suggestion, or a request.
        Gather Relevant Information: If your email is about a specific incident or person, gather all the pertinent details.
        Be Respectful: Remember that you’re addressing an authority figure. Maintain a respectful tone throughout your email.
        
        The email should include:
        Subject Line: Make it concise and informative. The subject line should summarize the purpose of your email.
        Salutation: Address the principal formally, using their correct title and surname.
        Introduction: Introduce yourself and your relationship to the school (e.g., parent, student).
        Body of Email: State your purpose for writing. Be clear, concise, and respectful.
        Closing: Express your appreciation for their time and request any necessary follow-up action. Sign off politely."""}

        recipient = f"Recipient: {recipient}\n"
        subject = f"Subject: {subject}\n"
        requirements = f"Email Requirements: {requirements}\n"
        other_information = f"Other Information: {other_information}\n" if other_information else ""

        user_message = {"role": "user", "content": f"""Please help me to write a email.
         {recipient}{subject}{requirements}{other_information}"""}

        response = get_response_content_from_gpt([system_message, user_message])

        file = open(self.file_name, "a")  # append mode
        file.write(response + separator)
        file.close()

        return response

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
                    },
                    "required": ["recipient", "subject", "requirements"]
                },

            }
        }
