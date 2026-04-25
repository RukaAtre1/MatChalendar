def estimate_food_carbon(item):
    return item.get("carbon", {}).get("estimated_co2e_kg", 0)
