from planner.schemas import skill_result


def run_study_skill(intent, context):
    return skill_result(
        "study",
        recommendations=[
            {
                "title": "Homework deep work",
                "duration_minutes": 90,
                "preferred_window": "evening_after_dinner",
                "location": "Powell Library",
            },
            {
                "title": "Review sprint",
                "duration_minutes": 75,
                "preferred_window": "midweek_afternoon",
                "location": "Study commons",
            },
        ],
        constraints=["schedule_homework_tonight", "avoid_class_overlap", "include_transition_buffer"],
        evidence=["prompt_homework_constraint"],
    )
