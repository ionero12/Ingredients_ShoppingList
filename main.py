import json
import os
import requests
from bs4 import BeautifulSoup
from collections import defaultdict


def get_recipe_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    ingredients = []
    for group in soup.find_all('div', class_='wprm-recipe-ingredients-container'):
        group_name_tag = group.find('h3', class_='wprm-recipe-group-name')

        # Handle the case where the group name is not present
        group_name = group_name_tag.text.strip() if group_name_tag else "Other"

        group_data = {'name': group_name, 'ingredients': []}
        for ingredient in group.find_all('li', class_='wprm-recipe-ingredient'):
            name_tag = ingredient.find('span', class_='wprm-recipe-ingredient-name')
            amount_tag = ingredient.find('span', class_='wprm-recipe-ingredient-amount')
            unit_tag = ingredient.find('span', class_='wprm-recipe-ingredient-unit')

            # Check if all necessary information is present
            if name_tag and amount_tag:
                name = name_tag.text.strip()
                amount = amount_tag.text.strip()
                unit = unit_tag.text.strip() if unit_tag else "no unit"

                ingredient_data = {'name': name, 'amount': amount, 'unit': unit}
                group_data['ingredients'].append(ingredient_data)

        ingredients.append(group_data)

    return ingredients


def update_shopping_list(recipe_list):
    # Load existing shopping list if it exists
    shopping_list = defaultdict(float)

    if os.path.exists('shopping_list.json'):
        with open('shopping_list.json', 'r') as file:
            shopping_list_json = json.load(file)

            # Convert quantities in the loaded shopping list to float
            shopping_list = {ingredient: float(quantity) for ingredient, quantity in shopping_list_json.items()}

    # Update the shopping list with the new recipe ingredients
    for recipe in recipe_list:
        for group in recipe['ingredients']:
            for ingredient in group['ingredients']:
                name = ingredient['name']
                quantity_str = ingredient['amount']
                unit = ingredient['unit']

                # Skip iteration if quantity is an empty string
                if not quantity_str:
                    print(f"Skipping ingredient '{name}' because quantity is empty.")
                    continue

                try:
                    quantity = float(quantity_str)

                    # If the ingredient exists in the shopping list, add the quantity
                    if name in shopping_list:
                        shopping_list[name] += quantity
                    else:
                        # If it doesn't exist, initialize with the given quantity
                        shopping_list[name] = quantity

                except ValueError:
                    print(f"Could not convert quantity '{quantity_str}' to float for ingredient '{name}'. Check for discrepancies in ingredient quantities.")

    # Save the updated shopping list
    with open('shopping_list.json', 'w') as file:
        json.dump(shopping_list, file, indent=2)

def main():
    # Example recipe URLs
    recipe_urls = [
        'https://jamilacuisine.ro/cascaval-pane-cu-ierburi-aromatice-video/',
        'https://jamilacuisine.ro/pui-cu-smantana-si-ciuperci-reteta-video/',
        'https://jamilacuisine.ro/pandispan-cu-cirese-visine-reteta-video/',
    ]

    recipes = []

    for url in recipe_urls:
        ingredients = get_recipe_data(url)

        if ingredients:
            recipe_data = {'url': url, 'ingredients': ingredients}
            recipes.append(recipe_data)

    update_shopping_list(recipes)


if __name__ == "__main__":
    main()
