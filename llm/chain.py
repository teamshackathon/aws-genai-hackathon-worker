import json
import re

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

from .base import BaseChain
from .schemas import GENRE_SCHEMAS, KEYWORD_SCHEMAS, RECIPE_SCHEMAS, RECIPENAME_SCHEMAS


#ジャンル分類するChain
class GenreClassificationChain(BaseChain):
    """Chain for analyzing conversation history"""

    def __init__(self, 
            chat_llm: BaseChatModel
        ):
        self.chat_llm = chat_llm
        self.prompt = PromptTemplate(
            template='''あなたは料理レシピのジャンルを判定するAIです。

以下の構造化されたレシピJSONの内容をもとに、料理のジャンルを以下の選択肢から1つだけ選んでください：

入力JSON：
"""
{recipe_json}
"""

["和食", "洋食", "中華", "韓国風", "エスニック", "スイーツ", "その他"]

選択のポイント：
- 日本の家庭料理・丼もの・しょうゆやみりんベース：→ 「和食」
- バター・チーズ・オーブン料理など：→ 「洋食」
- 中華鍋、オイスターソース、甜麺醤など：→ 「中華」
- コチュジャン、キムチ、韓国風焼肉など：→ 「韓国風」
- ナンプラー、パクチー、スパイスが特徴：→ 「エスニック」
- デザート類（ケーキ、クッキー、プリンなど）：→ 「スイーツ」
- 上記に当てはまらない・ジャンルが混在：→ 「その他」

---

- 出力形式は必ず **以下の JSON スキーマ形式のみ** に従ってください。
- **テキスト出力や説明文、Markdownは絶対に含めないでください。**
- JSON 以外の文字を含むとエラーとなります。

出力形式:"""
{schema}
"""
''',
    input_variables=["recipe_json", "schema"]
    )
        self.chain = self.prompt | self.chat_llm | StrOutputParser() | RunnableLambda(self.replaced2json)

    def get_prompt(self, inputs, **kwargs):
        """Get the prompt string for the given inputs."""

        # Create formatted input
        formatted_input = {
            "history": inputs,
            "schema": GENRE_SCHEMAS,
        }

        return self.prompt.invoke(formatted_input, **kwargs).to_string()
        
    def invoke(self, 
            inputs: str,            
        ):
        """Invoke the chain for conversation analysis."""

        # Prepare the input for the chain
        formatted_input = {
            "recipe_json": inputs,
            "schema": GENRE_SCHEMAS,
        }

        # Execute the chain
        response = self.chain.invoke(formatted_input)

        print(f"Response: {response}")

        return json.loads(response)
    
    @staticmethod
    def replaced2json(output: str) -> str:
        replaced_output = output.replace('```json', '').replace('```', '')
        # 正規表現を使って空白行（改行だけや空白のみの行）を削除
        replaced_output = re.sub(r'^\s*\n', '', replaced_output, flags=re.MULTILINE)
        # 正規表現を使って最後のカンマを削除
        replaced_output = re.sub(r',\s*$', '', replaced_output)
        # replaced_output = json.loads(replaced_output) # これを加えるとdict型になってしまう
        return replaced_output
    
class RecipeNameGenerationChain(BaseChain):
    """Chain for generating recipe names"""

    def __init__(self,
            chat_llm: BaseChatModel
        ):
        self.chat_llm = chat_llm
        self.prompt = PromptTemplate(
            template='''以下の構造化レシピJSONに基づいて、この料理の名前を生成してください。
親しみやすく、キャッチーな名前を考えてください。ただし、あまり長くならないようにしてください。
また料理の内容からは逸脱しないようにしてください。

入力:"""
{recipe_json}
"""

- 出力形式は必ず **以下の JSON スキーマ形式のみ** に従ってください。
- **テキスト出力や説明文、Markdownは絶対に含めないでください。**
- JSON 以外の文字を含むとエラーとなります。

出力形式:"""
{schema}
"""
''',
            input_variables=["recipe_json", "schema"]
        )
        self.chain = self.prompt | self.chat_llm | StrOutputParser() | RunnableLambda(self.replaced2json)
    
    def get_prompt(self, inputs, **kwargs):
        """Get the prompt string for the given inputs."""

        # Create formatted input
        formatted_input = {
            "recipe_json": inputs,
            "schema": RECIPENAME_SCHEMAS,
        }

        return self.prompt.invoke(formatted_input, **kwargs).to_string()
    
    def invoke(self,
            inputs: str,
        ):
        """Invoke the chain for recipe name generation."""

        # Prepare the input for the chain
        formatted_input = {
            "recipe_json": inputs,
            "schema": RECIPE_SCHEMAS,
        }

        # Execute the chain
        response = self.chain.invoke(formatted_input)

        print(f"Response: {response}")

        return json.loads(response)
    
    @staticmethod
    def replaced2json(output: str) -> str:
        replaced_output = output.replace('```json', '').replace('```', '')
        # 正規表現を使って空白行（改行だけや空白のみの行）を削除
        replaced_output = re.sub(r'^\s*\n', '', replaced_output, flags=re.MULTILINE)
        # 正規表現を使って最後のカンマを削除
        replaced_output = re.sub(r',\s*$', '', replaced_output)
        # replaced_output = json.loads(replaced_output) # これを加えるとdict型になってしまう
        return replaced_output
    

class RecipeKeywordsGenerationChain(BaseChain):
    """Chain for generating recipe keywords"""

    def __init__(self,
            chat_llm: BaseChatModel
        ):
        self.chat_llm = chat_llm
        self.prompt = PromptTemplate(
            template='''あなたは料理のレシピJSONを分析して、関連するキーワードを抽出するAIです。

以下のJSONは料理レシピの構造化データです。  
このレシピの特徴や材料、調理方法をもとに、関連する単語やフレーズからなる **キーワードリスト** を生成してください。

**以下のスキーマに従って、キーワードの配列だけを含んだJSONとして出力してください。**

絶対に上記のような `keywords` プロパティだけを含むJSONだけを出力してください。
`type`, `properties`, `required` などのスキーマ構文は一切含めないでください。

入力:"""
{recipe_json}
"""

- 出力形式は必ず **以下の JSON スキーマ形式のみ** に従ってください。
- **テキスト出力や説明文、Markdownは絶対に含めないでください。**
- JSON 以外の文字を含むとエラーとなります。

出力形式:"""
{schema}
"""
''',
            input_variables=["recipe_json", "schema"]
        )
        self.chain = self.prompt | self.chat_llm | StrOutputParser() | RunnableLambda(self.replaced2json)

    def get_prompt(self, inputs, **kwargs):
        """Get the prompt string for the given inputs."""

        # Create formatted input
        formatted_input = {
            "recipe_json": inputs,
            "schema": KEYWORD_SCHEMAS,
        }
        return self.prompt.invoke(formatted_input, **kwargs).to_string()
    
    def invoke(self,
            inputs: str,
        ):
        """Invoke the chain for recipe keyword generation."""

        # Prepare the input for the chain
        formatted_input = {
            "recipe_json": inputs,
            "schema": KEYWORD_SCHEMAS,
        }

        # Execute the chain
        response = self.chain.invoke(formatted_input)

        print(f"Response: {response}")

        return json.loads(response)

    @staticmethod
    def replaced2json(output: str) -> str:
        replaced_output = output.replace('```json', '').replace('```', '')
        # 正規表現を使って空白行（改行だけや空白のみの行）を削除
        replaced_output = re.sub(r'^\s*\n', '', replaced_output, flags=re.MULTILINE)
        # 正規表現を使って最後のカンマを削除
        replaced_output = re.sub(r',\s*$', '', replaced_output)
        # replaced_output = json.loads(replaced_output) # これを加えるとdict型になってしまう
        return replaced_output
    
class RecipeRewriteChain(BaseChain):
    """Chain for rewriting recipe content"""

    def __init__(self,
            chat_llm: BaseChatModel
        ):
        self.chat_llm = chat_llm
        self.prompt = PromptTemplate(
            template='''あなたは料理レシピを、ユーザーの好みに合わせて編集する優秀なAIです。

以下のJSONには、ある料理のレシピ（名前、手順、材料）が構造化されて含まれています。

入力JSON：
"""
{recipe_json}
"""
レシピについて、一般的な料理のレシピと比較して、抜け漏れや不自然な点がないかも確認してください。
焼いたり煮たりする手順がある場合は、火加減や時間の目安が抜けていないか、抜けている場合は一般的なレシピから類推してください。

このレシピを下記のユーザーの好みや条件に合うように書き換えてください。
レシピの時間を大きく短縮する時は、調理方法や材料を変更しても構いません。
火が通らなかったり危険な調理になる場合には、好みを無視してでも安全な調理方法に変更してください。


人数設定:
"""
{people_count}
"""

調理時間設定:
"""
{cooking_time}
"""

重視する傾向:
"""
{preference}
"""

塩味の強さ:
"""
{saltiness}
"""

甘味の強さ:
"""
{sweetness}
"""

辛味の強さ:
"""
{spiciness}
"""

嫌いな食材:
"""
{disliked_ingredients}
"""

ただし、**出力のスキーマ構造（項目名など）は変更せず、料理とはあまり関係ない好みは取り込まない**ようにしてください。  
料理の意味が変わるような大幅な改変や創作は行わないでください。特にrecipe_nameは変更しないでください。

- 出力形式は必ず **以下の JSON スキーマ形式のみ** に従ってください。
- **テキスト出力や説明文、Markdownは絶対に含めないでください。**
- JSON 以外の文字を含むとエラーとなります。

出力形式:"""
{schema}
"""
''',
            input_variables=["recipe_json", "people_count", "cooking_time", "preference", "saltiness", "sweetness", "spiciness", "disliked_ingredients", "schema"]
        )
        self.chain = self.prompt | self.chat_llm | StrOutputParser() | RunnableLambda(self.replaced2json)    
    def get_prompt(self, inputs, **kwargs):
        """Get the prompt string for the given inputs."""

        # Create formatted input
        formatted_input = {
            "recipe_json": inputs["recipe_json"],
            "people_count": inputs.get("people_count", "レシピ通り"),
            "cooking_time": inputs.get("cooking_time", "レシピ通り"),
            "preference": inputs.get("preference", "レシピ通り"),
            "saltiness": inputs.get("saltiness", "レシピ通り"),
            "sweetness": inputs.get("sweetness", "レシピ通り"),
            "spiciness": inputs.get("spiciness", "レシピ通り"),
            "disliked_ingredients": inputs.get("disliked_ingredients", "特になし"),
            "schema": RECIPE_SCHEMAS,
        }
        return self.prompt.invoke(formatted_input, **kwargs).to_string()    
    def invoke(self,
            inputs: dict,
        ):
        """Invoke the chain for recipe rewriting."""

        # Prepare the input for the chain
        formatted_input = {
            "recipe_json": inputs["recipe_json"],
            "people_count": inputs.get("people_count", "レシピ通り"),
            "cooking_time": inputs.get("cooking_time", "レシピ通り"),
            "preference": inputs.get("preference", "レシピ通り"),
            "saltiness": inputs.get("saltiness", "レシピ通り"),
            "sweetness": inputs.get("sweetness", "レシピ通り"),
            "spiciness": inputs.get("spiciness", "レシピ通り"),
            "disliked_ingredients": inputs.get("disliked_ingredients", "特になし"),
            "schema": RECIPE_SCHEMAS,
        }

        print(f"Formatted Input: {formatted_input}")

        # Execute the chain
        response = self.chain.invoke(formatted_input)

        print(f"Response: {response}")

        return json.loads(response)
    
    @staticmethod
    def replaced2json(output: str) -> str:
        replaced_output = output.replace('```json', '').replace('```', '')
        # 正規表現を使って空白行（改行だけや空白のみの行）を削除
        replaced_output = re.sub(r'^\s*\n', '', replaced_output, flags=re.MULTILINE)
        # 正規表現を使って最後のカンマを削除
        replaced_output = re.sub(r',\s*$', '', replaced_output)
        # replaced_output = json.loads(replaced_output) # これを加えるとdict型になってしまう
        return replaced_output