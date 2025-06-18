from langchain_aws.chat_models.bedrock import ChatBedrock
from langchain_aws.embeddings.bedrock import BedrockEmbeddings
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
    
class BedrockEmbeddingsClient:
    """Amazon Bedrock埋め込みクライアント"""

    def __init__(self):
        self.client = self._initialize_client()

    def _initialize_client(self) -> BedrockEmbeddings:
        """Amazon Bedrock埋め込みクライアントを初期化"""
        try:
            return BedrockEmbeddings(
                model_id='amazon.titan-embed-text-v1',
                region_name=settings.AWS_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            raise ValueError(f"Amazon Bedrock埋め込みクライアントの初期化に失敗しました: {str(e)}")

    def get_client(self) -> BedrockEmbeddings:
        """Bedrock埋め込みクライアントを取得"""
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
    
class BedrockEmbeddingsService:
    """Amazon Bedrock埋め込みサービス"""
    
    def __init__(self):
        self.client = BedrockEmbeddingsClient().get_client()

    def get_prompt(self, recipe_name, ingredients, processes, genrue, keyword) -> str:
        print("入力確認", ingredients,processes)
        ingredients_text = '\n'.join([f"{ing['ingredient']},{ing['amount']}" for ing in ingredients])
        processes_text = '\n'.join([f"{p['process_number']}番目 {p['process']}" for p in processes])

        return f"""レシピ名:{recipe_name}
ジャンル: {genrue}
keyword: {keyword}
材料:
{ingredients_text}

調理手順:
{processes_text}


"""

    def embed_text(self, text: str) -> list:
        """テキストを埋め込み"""
        if not text:
            raise ValueError("テキストは空ではいけません。")
        return self.client.embed_query(text)