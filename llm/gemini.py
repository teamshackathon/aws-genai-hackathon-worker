import re

import google.genai as genai
from google.genai import types

from config import settings

from .schemas import RECIPE_SCHEMAS


class GeminiClient:

    def __init__(self):
        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self.model = 'models/gemini-2.0-flash'

    def invoke(self, prompt: str, file_url: str):
        """
        Invoke the Gemini model with a prompt and file URL.

        Args:
            prompt (str): The prompt to send to the model.
            file_url (str): The URL of the file to be processed.
        """

        contents = types.Content(
            parts=[
                types.Part(
                    file_data=types.FileData(file_uri=file_url)
                ),
                types.Part(text=prompt)
            ]
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
        )

        return response.text

class GeminiService:

    def __init__(self):
        self.client = GeminiClient()

    def generate_content(self, file_url: str):
        """
        Generate content using the Gemini model.

        Args:
            prompt (str): The prompt to send to the model.
            file_url (str): The URL of the file to be processed.

        Returns:
            Response from the Gemini model.
        """

        if not file_url:
            raise ValueError("Prompt and file URL must not be empty.")
        
        youtube_shorts_pattern = r'^https://(www\.)?youtube\.com/shorts/[a-zA-Z0-9_-]+$'

        if not re.match(youtube_shorts_pattern, file_url):
            raise ValueError(f"File URL must be a valid YouTube Shorts URL.: {file_url}")
        
        prompt = f'''あなたは料理動画を分析して、構造化されたJSONデータを出力するとても優秀なAIです。

次の動画の内容を分析して、以下の**スキーマに準拠した形式**でレシピ情報を抽出してください。

**何があっても、以下のスキーマの形のみ出力するように絶対従ってください。**

出力形式："""
{RECIPE_SCHEMAS}
"""
'''     
        response = self.client.invoke(prompt, file_url)

        response = self.replaced2json(response)

        if not response:
            raise ValueError("Response is empty or invalid JSON format.")
        try:
            # JSONの形式が正しいか検証
            import json
            response_json = json.loads(response)
            return response_json
        except json.JSONDecodeError as e:
            raise ValueError(f"Response is not a valid JSON format: {e}")
    
    def replaced2json(self, output: str) -> str:
        replaced_output = output.replace('```json', '').replace('```', '')
        # 正規表現を使って空白行（改行だけや空白のみの行）を削除
        replaced_output = re.sub(r'^\s*\n', '', replaced_output, flags=re.MULTILINE)
        # 正規表現を使って最後のカンマを削除
        replaced_output = re.sub(r',\s*$', '', replaced_output)
        # replaced_output = json.loads(replaced_output) # これを加えるとdict型になってしまう
        return replaced_output
