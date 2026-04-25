def run_explanation_skill(intent, blocks):
    for block in blocks:
        carbon = block["carbon"]
        delta = carbon.get("delta_co2e_kg", 0)
        if delta < 0:
            impact = f"Estimated {carbon['estimated_co2e_kg']} kg CO2e, saving {abs(delta)} kg versus the baseline."
        elif delta > 0:
            impact = f"Estimated {carbon['estimated_co2e_kg']} kg CO2e, adding {delta} kg versus the baseline."
        else:
            impact = f"Estimated {carbon['estimated_co2e_kg']} kg CO2e with no baseline change."

        block["explanation"] = {
            "impact": impact,
            "skills_used": block["skills_used"],
            "data_sources": block["data_sources"],
        }

    return blocks
