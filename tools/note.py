from tools.common import Tool

separator = "\n`````\n"


class WriteToMyNoteTool(Tool):
    name = "write_to_my_note"
    description = "This is very helpful if you need to write down something into the notebook"

    file_name = "./my_note.txt"

    def run(self, args: dict) -> str:
        print('args: ', args)

        content = args.get("content")
        file = open(self.file_name, "a")  # append mode
        file.write(content + separator)
        file.close()
        return "Successfully written to notebook."

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
                        "content": {
                            "type": "string",
                            "description": "The content you want to write down.",
                        },
                    },
                    "required": ["content"]
                },

            }
        }


class ReadFromMyNoteTool(Tool):
    name = "read_from_my_note"
    description = "This is very helpful if you need to read something from the notebook"

    file_name = "./my_note.txt"

    def run(self, args: dict) -> str:
        content = args.get("content")
        file = open(self.file_name, "r")  # append mode
        return file.read()

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
                        "content": {
                            "type": "string",
                            "description": "The content you read look for.",
                        }
                    },
                    "required": ["content"]
                }
            }
        }
