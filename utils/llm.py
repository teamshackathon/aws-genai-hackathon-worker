def transform_recipe_data(original_data, url: str, user_id: int) -> dict:
    return {
        "recipes": {
            "status_id": 1,
            "external_service_id": 0,
            "url": url,
            "recipe_name": original_data["recipes"].get("recipe_name", "AIが生成したレシピ"),
        },
        "user_recipes": {
            "user_id": user_id,
        },
        "processes": [
            {
                "process": p["process"],
                "process_number": p["process_number"]
            }
            for p in original_data.get("processes", [])
        ],
        "ingredients": [
            {
                "ingredient": ing.get("ingredient_name", ""),
                "amount": ing.get("amount", "")
            }
            for ing in original_data.get("ingredients", [])
        ]
    }