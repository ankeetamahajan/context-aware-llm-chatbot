import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient


load_dotenv()


class Chatbot:

    def __init__(self, token=None, model_id=None):

        self.token = (
            token
            or os.getenv("HF_TOKEN")
        )

        self.model_id = (
            model_id
            or os.getenv("MODEL_ID")
        )

        if not self.token:
            raise ValueError(
                "HF_TOKEN not found."
            )

        if not self.model_id:
            raise ValueError(
                "MODEL_ID not found."
            )

        self.client = InferenceClient(
            api_key=self.token,
            provider="auto"
        )

        self.system_prompt = """
You are a helpful conversational assistant.

Use previous messages from this conversation
when relevant.

If the user asks about something they previously
said, answer using the supplied conversation history.

Do not invent memories that are not present
in the supplied conversation.
""".strip()

    def reply(self, messages):

        full_messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]

        full_messages.extend(messages)

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=full_messages,
            temperature=0.4,
            max_tokens=800
        )

        answer = (
            response
            .choices[0]
            .message
            .content
        )

        if not answer:
            raise ValueError(
                "LLM returned an empty response."
            )

        return answer.strip()