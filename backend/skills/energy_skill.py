from planner.schemas import skill_result


def run_energy_skill(intent, context):
    low_energy = "low_energy" in intent.get("detected_constraints", [])
    return skill_result(
        "energy",
        recommendations=[
            {"type": "transition_buffer", "duration_minutes": 30},
            {"type": "sleep_winddown", "duration_minutes": 30},
            {"type": "planning_intensity", "level": "light" if low_energy else "balanced"},
        ],
        constraints=["do_not_stack_class_homework_without_break", "protect_evening_recovery"],
        evidence=["prompt_energy_state", "default_student_energy_model"],
    )
