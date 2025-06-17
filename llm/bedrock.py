from langchain_aws.chat_models.bedrock import ChatBedrock
from langchain_core.language_models.chat_models import BaseChatModel

from config import settings

from .chain import GenreClassificationChain, RecipeKeywordsGenerationChain, RecipeNameGenerationChain, RecipeRewriteChain


class BedrockClient:
    """Amazon Bedrockクライアント"""

    def __init__(self):
        self.client = self._initialize_client()

    def _initialize_client(self) -> BaseChatModel:
        """Amazon Bedrockクライアントを初期化"""
        try:
            return ChatBedrock(
                model_id='apac.amazon.nova-pro-v1:0',
                region_name=settings.AWS_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            raise ValueError(f"Amazon Bedrockクライアントの初期化に失敗しました: {str(e)}")

    def get_client(self) -> BaseChatModel:
        """Bedrockクライアントを取得"""
        return self.client
    


class BedrockService:

    """Amazon Bedrockサービス"""
    def __init__(self):
        self.client = BedrockClient().get_client()
        self.genre_chain = GenreClassificationChain(chat_llm=self.client)
        self.recipe_name_chain = RecipeNameGenerationChain(chat_llm=self.client)
        self.recipe_keywords_chain = RecipeKeywordsGenerationChain(chat_llm=self.client)

    def generate_genre(self, recipe_json: dict) -> str:
        """レシピJSONからジャンルを生成"""
        if not recipe_json:
            raise ValueError("レシピJSONは空ではいけません。")
        # 文字列型に変換
        if isinstance(recipe_json, dict):
            recipe_json = str(recipe_json)
        return self.genre_chain.invoke(recipe_json)

    def generate_recipe_name(self, recipe_json: dict) -> str:
        """レシピJSONからレシピ名を生成"""
        if not recipe_json:
            raise ValueError("レシピJSONは空ではいけません。")
        # 文字列型に変換
        if isinstance(recipe_json, dict):
            recipe_json = str(recipe_json)
        return self.recipe_name_chain.invoke(recipe_json)

    def generate_keywords(self, recipe_json: dict) -> str:
        """レシピJSONからキーワードを生成"""
        if not recipe_json:
            raise ValueError("レシピJSONは空ではいけません。")
        # 文字列型に変換
        if isinstance(recipe_json, dict):
            recipe_json = str(recipe_json)
        return self.recipe_keywords_chain.invoke(recipe_json)
    
    def rewrite_recipe(self, recipe_json: dict) -> str:
        """レシピJSONをリライト"""
        if not recipe_json:
            raise ValueError("レシピJSONは空ではいけません。")
        # 文字列型に変換
        if isinstance(recipe_json, dict):
            recipe_json = str(recipe_json)
        rewrite_chain = RecipeRewriteChain(chat_llm=self.client)
        return rewrite_chain.invoke(recipe_json)