import openai
from newschatbot.lib.settings import settings

openai.api_key = settings.openai_api_key

class StatelessClient:
    def __init__(self, context: str):
        self.context = context

    def request(self, message: str) -> str:
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "user", "content": self.context},
                {"role": "user", "content": message},
            ],
        )
        return response.choices[0]["message"]["content"].strip()
