import requests
def mealdb_recipe_search(recipe_name: str) -> str:
    """
    Use this tool to search for non-Thai recipe ingredients using TheMealDB.
    Input should be the recipe name, e.g., 'lasagna'.
    """
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={recipe_name}"
    res = requests.get(url).json()
    meals = res.get("meals")
    if not meals:
        return f"No recipe found for '{recipe_name}' in MealDB."
    
    meal = meals[0]
    name = meal["strMeal"]
    instructions = meal["strInstructions"]
    ingredients = []
    
    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")
        if ingredient and ingredient.strip():
            ingredients.append(f"{ingredient.strip()} - {measure.strip()}")
    
    return f"Recipe: {name}\n\nIngredients:\n" + "\n".join(ingredients) + f"\n\nInstructions:\n{instructions}"
