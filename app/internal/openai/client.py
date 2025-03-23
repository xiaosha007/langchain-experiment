from langchain.chat_models import init_chat_model

class OpenAIClient:
    def __init__(self, api_key: str):
        self.model = init_chat_model("gpt-4o-mini", model_provider="openai", api_key=api_key)

    def get_completion(self, prompt: str):
        return self.model.invoke(prompt)
