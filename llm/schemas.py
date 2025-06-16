RECIPE_SCHEMAS = """{
    "type": "object",
    "required": ["recipes", "processes", "ingredients"],
    "properties": {
        "recipes": {
            "type": "object",
            "required": ["recipe_name"],
            "properties": {
                "recipe_name": {
                    "type": "string",
                    "description": "The name of the recipe."
                }
            }
        },
        "processes": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["process_number", "process"],
                "properties": {
                    "process_number": {
                        "type": "integer",
                        "description": "The step number in the recipe."
                    },
                    "process": {
                        "type": "string",
                        "description": "A description of the process step."
                    }
                }
            }
            
        },
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["ingredient", "amount"],
                "properties": {
                    "ingredient_name": {
                        "type": "string",
                        "description": "The name of the ingredient."
                    },
                    "amount": {
                        "type": "string",
                        "description": "The amount of the ingredient required for the recipe."
                    }
                }
            }
        }
    }
}"""