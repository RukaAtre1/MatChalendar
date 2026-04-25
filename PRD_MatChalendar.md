# PRD: MatChalendar - Local-first AI Planner-Orchestrator for Campus Life

## 1. Product Summary

MatChalendar is a local-first, carbon-aware AI planner-orchestrator for campus life.

It understands a student's natural-language intent, routes planning tasks to specialist skills, and replans the user's weekly calendar across classes, assignments, dining, health, energy, transportation, rest, and sustainability goals.

MatChalendar is not just a calendar app and not just a chatbot. It turns fragmented student decisions into an executable and explainable weekly calendar.

```text
MatChalendar = Master AI Planner + Specialist Skills + Food Data Intelligence + Carbon-aware Calendar Replanning
```

## 2. Core Product Idea

Most calendar apps only store time. Generic AI chatbots give advice but do not produce executable calendar blocks.

MatChalendar connects time, campus context, food choices, health goals, study workload, transportation, energy level, and carbon goals into one explainable plan.

```text
User prompt
-> Intent Understanding
-> Master AI Planner
-> Skill Router
-> Specialist Skills
-> Calendar Replanner
-> Explainable Weekly Calendar
```

Core rule:

```text
Skills propose. Planner decides. Calendar renders.
```

The Master Planner owns the final calendar decision. Skills do not independently edit the final calendar; they return recommendations, constraints, scores, and evidence.

## 3. Target User and Pain Points

Primary user:

```text
Busy college students who want help planning classes, homework, meals, workouts, rest, transportation, energy, and sustainability goals.
```

Initial target environment:

```text
UCLA campus / LA Hacks student users
```

Pain points:

- Students have fragmented decisions across classes, homework, meals, health, sleep, workouts, commuting, and carbon goals.
- Calendar apps record events but do not optimize life decisions.
- Generic AI chatbots give advice but do not create executable calendar blocks.
- Dining, health, energy, and carbon choices are connected, but students usually manage them separately.
- Sustainability advice is often abstract; MatChalendar turns it into concrete calendar decisions.
- Student schedule, health preferences, energy level, transportation choices, and carbon goals are sensitive lifestyle data.

## 4. Core User Flow

1. User opens MatChalendar.
2. User enters a natural-language goal:

```text
Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency and took an Uber today. I also have class from 10 to 2 and homework tonight.
```

3. MatChalendar detects intent, constraints, and planning scope.
4. Master Planner selects relevant skills.
5. Skills return recommendations, constraints, scores, and evidence.
6. Calendar Replanner produces an updated weekly calendar.
7. User clicks each block to see explanations, scores, carbon impact, and skills used.
8. User accepts or regenerates the plan.

## 5. Master Planner Architecture

The Master Planner is the central orchestrator.

It is responsible for:

- understanding user intent
- detecting goals and constraints
- deciding planning scope
- selecting relevant skills
- collecting skill outputs
- resolving conflicts between skills
- generating the final weekly calendar
- passing final blocks to the Explanation Skill

```text
User Prompt
  -> Intent Parser
  -> Master Planner
  -> Skill Router
     |-- Calendar Skill
     |-- Dining Skill
     |-- Study Skill
     |-- Health Skill
     |-- Energy Skill
     |-- Transportation Skill
     |-- Sustainability / Carbon Skill
     `-- Explanation Skill
  -> Calendar Replanner
  -> Final Weekly Calendar
```

The Master Planner acts like a planning director. It asks specialist skills for domain-specific options and then makes the final calendar decision.

## 6. Skills System

MatChalendar uses internal specialist skills. They are not separate user-facing apps.

### 6.1 Calendar Skill

Handles fixed events, free slots, conflicts, and placement constraints.

- read fixed class / meeting / assignment events
- identify available time slots
- prevent schedule conflicts
- provide placement constraints

### 6.2 Dining Skill

Recommends dining halls and meal options based on time, location, availability, user preferences, nutrition, and carbon impact.

- check dining hall availability
- recommend meal options
- use food profiles from the Food Data Intelligence Layer
- return candidate meals with health, energy, sustainability, and carbon scores

### 6.3 Study Skill

Schedules homework, deep work, review blocks, and study breaks based on deadlines and available time.

- estimate study time needed
- suggest deep work blocks
- avoid class conflicts
- include breaks when workload is high

### 6.4 Health Skill

Evaluates meals and activities based on health goals, protein needs, workout preferences, and recovery needs.

- evaluate meals against health goals
- recommend workouts or light movement
- consider recovery and sleep needs
- avoid unrealistic plans for low-energy days

### 6.5 Energy Skill

Adjusts planning intensity based on user energy level, meal heaviness, rest needs, and study workload.

- detect low-energy or high-stress days
- recommend lighter meals or workouts when needed
- place breaks before or after demanding work blocks
- avoid overloading the calendar

### 6.6 Transportation Skill

Estimates walking, biking, bus, and ride-share options, including time and carbon impact.

- estimate transportation time
- identify walking or transit-friendly options
- detect high-carbon events such as Uber / ride-share
- return transportation constraints and carbon estimates

### 6.7 Sustainability / Carbon Skill

Tracks weekly carbon goals, detects high-carbon events, estimates carbon impact, and recommends low-carbon adjustments.

- maintain a weekly carbon goal or budget
- estimate transportation and food carbon impact
- detect high-carbon events
- recommend low-carbon meals, walking routes, transit options, or future compensating choices

### 6.8 Explanation Skill

Explains why each calendar block was selected.

- explain timing
- explain location choices
- explain health / energy / sustainability / carbon tradeoffs
- list skills used
- show data sources when possible

## 7. Food Data Intelligence Layer

MatChalendar uses a shared Food Data Intelligence Layer before skill planning.

```text
UCLA Dining Website / Mock Dining Data
  -> Food Data Pipeline
  -> Nutrition + Carbon Enrichment
  -> Shared Food Knowledge Base
  -> Dining Skill + Health Skill + Energy Skill + Carbon Skill
```

For the MVP, this layer uses mock UCLA dining data. Nutrition and carbon values are estimated for planning purposes.

Example enriched food item:

```json
{
  "id": "bplate_dinner_001",
  "name": "Plant-based grain bowl",
  "dining_hall": "Bruin Plate",
  "meal_period": "dinner",
  "available_start": "17:00",
  "available_end": "21:00",
  "tags": ["vegan", "low_carbon", "high_fiber"],
  "estimated_nutrition": {
    "calories": 520,
    "protein_g": 22,
    "carbs_g": 68,
    "fat_g": 16
  },
  "carbon": {
    "estimated_co2e_kg": 0.7,
    "carbon_category": "low",
    "source": "ucla_mock_plus_estimator"
  },
  "scores": {
    "health": 0.88,
    "energy": 0.82,
    "sustainability": 0.94,
    "carbon": 0.94
  }
}
```

## 8. Carbon-aware Replanning

If the user sets a weekly carbon reduction goal and logs a high-carbon event, such as taking an Uber for an emergency, the planner updates the carbon budget and adjusts future recommendations.

Planner response:

- detect increased transportation emissions
- update weekly carbon budget
- ask Dining Skill for lower-carbon meal options
- ask Health and Energy Skills to keep the meal realistic
- replan dinner and future transportation choices
- explain the tradeoff in the calendar block

Example explanation:

```text
You took an Uber today for an urgent event, which increased your transportation carbon impact. This dinner was shifted to a lower-carbon meal to help keep your weekly carbon goal on track while still supporting your energy and protein needs.
```

## 9. Calendar Output and Explanation

Each calendar block should include:

- id
- title
- type
- start
- end
- location
- reason
- scores
- carbon impact
- skills used
- data sources

Recommended score dimensions:

```json
{
  "time": 0.86,
  "health": 0.90,
  "energy": 0.82,
  "sustainability": 0.94,
  "carbon": 0.92
}
```

Each explanation should answer:

```text
Why this time?
Why this location?
Why this meal or activity?
How does it affect health?
How does it affect energy?
How does it affect the carbon goal?
Which skills contributed?
```

## 10. Frontend Experience

The frontend should make planning understandable in one screen.

```text
Left: AI chatbox / goal input
Right: weekly calendar
Drawer: explanation + scores + carbon impact + skills used
Badge: ASUS GX10 local-AI integration point
```

The frontend should show:

- MatChalendar title
- left prompt input
- right weekly calendar
- clickable calendar blocks
- explanation drawer
- carbon budget card
- skills used trace
- plan regeneration
- visible future integration points

Example status steps:

```text
Understanding goal...
Parsing intent...
Routing skills...
Running internal skills...
Replanning calendar...
Building explanations...
Rendering PlanResponse...
```

## 11. Backend Architecture

Current MVP structure:

```text
backend/
  main.py
  planner/
    master_planner.py
    intent_parser.py
    skill_router.py
    calendar_replanner.py
    schemas.py
  skills/
    calendar_skill.py
    dining_skill.py
    study_skill.py
    health_skill.py
    energy_skill.py
    transportation_skill.py
    sustainability_carbon_skill.py
    explanation_skill.py
  food/
    food_data_pipeline.py
    nutrition_estimator.py
    carbon_estimator.py
    food_store.py
  data/
    dining_mock.json
    sample_schedule.json
    carbon_factors.json
```

Current endpoints:

```text
POST /api/plan
GET /api/dining
GET /api/demo-schedule
GET /api/health
```

The MVP starts with deterministic skills and a rule-based calendar replanner. Local AI can later be added for intent understanding, option ranking, and explanation generation.

## 12. Data Model

Example PlanResponse:

```json
{
  "summary": "Your week was replanned to balance class, homework, energy, meals, and your carbon reduction goal.",
  "generated_by": "deterministic_mvp_master_planner",
  "intent": {
    "primary_goal": "reduce_weekly_carbon",
    "planning_scope": "this_week",
    "detected_constraints": [
      "class_10_to_2",
      "homework_tonight",
      "emergency_uber"
    ],
    "skills_used": [
      "calendar",
      "transportation",
      "sustainability_carbon",
      "dining",
      "health",
      "energy",
      "study",
      "explanation"
    ]
  },
  "carbon_budget": {
    "weekly_target_kg_co2e": 35.0,
    "current_estimated_kg_co2e": 19.4,
    "status": "slightly_above_expected_today",
    "adjustment_strategy": "lower_carbon_dining_and_walkable_routes"
  },
  "plan_blocks": [
    {
      "id": "block_001",
      "title": "Low-carbon dinner at Bruin Plate",
      "type": "meal",
      "start": "2026-04-27T18:30:00",
      "end": "2026-04-27T19:15:00",
      "location": "Bruin Plate",
      "reason": "You took an Uber today, so this dinner shifts toward a lower-carbon option while preserving protein and energy.",
      "scores": {
        "time": 0.86,
        "health": 0.90,
        "energy": 0.82,
        "sustainability": 0.94,
        "carbon": 0.92
      },
      "carbon": {
        "estimated_co2e_kg": 0.7,
        "baseline_co2e_kg": 1.8,
        "delta_co2e_kg": -1.1,
        "category": "dining"
      },
      "skills_used": [
        "dining",
        "sustainability_carbon",
        "health",
        "energy",
        "calendar"
      ],
      "data_sources": [
        "ucla_dining_mock",
        "carbon_factors",
        "user_schedule",
        "local_planner"
      ]
    }
  ]
}
```

## 13. ASUS GX10 Local AI Integration Point

ASUS Ascent GX10 is a future local AI planning server integration. It is not implemented in the MVP.

Future responsibilities:

- intent understanding
- planner reasoning
- skill routing assistance
- explanation generation
- ranking candidate options
- summarizing tradeoffs

Possible future environment variables:

```bash
GX10_OLLAMA_URL=http://GX10_IP:11434/api/generate
LOCAL_MODEL_NAME=gemma3:4b
USE_LOCAL_AI=true
FALLBACK_TO_MOCK=true
```

If local AI is unavailable, the backend should continue returning a deterministic fallback plan so the demo remains stable.

## 14. Agentverse / OmegaClaw Integration Points

Agentverse and OmegaClaw are not implemented in the MVP.

Planned external skill:

```text
CampusLifePlannerSkill
```

Planned call chain:

```text
OmegaClaw
  -> CampusLifePlannerSkill
  -> Agentverse
  -> MatChalendar Campus Planner Agent
  -> Master Planner
  -> Internal Skills
  -> Final Calendar Plan
```

The external skill should return a concise plan with calendar blocks, reasons, scores, carbon impact, and skills used.

## 15. LA Hacks Track Alignment

### ASUS / Local AI

MatChalendar is designed to use ASUS Ascent GX10 for local AI planning over sensitive student context.

### Fetch.ai / Agentverse

MatChalendar can expose the campus planner as an Agentverse specialist agent.

### OmegaClaw Skill

OmegaClaw can invoke `CampusLifePlannerSkill` to generate a full campus-life calendar plan.

### Sustainability / Social Impact

MatChalendar turns carbon reduction from abstract advice into concrete calendar decisions through carbon-aware replanning.

## 16. MVP Demo Scenario

Demo prompt:

```text
Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency and took an Uber today. I also have class from 10 to 2 and homework tonight.
```

Expected behavior:

- detect intent: reduce weekly carbon emissions
- detect event: emergency Uber
- detect constraints: class from 10 to 2, homework tonight
- select skills: calendar, transportation, carbon, dining, health, energy, study, explanation
- update carbon budget
- recommend low-carbon dinner
- schedule homework deep work
- generate weekly calendar blocks
- show explanation drawer with carbon impact and skills used

Example final plan:

```text
10:00 AM - 2:00 PM Class
2:15 PM - 2:45 PM Recovery walk
6:30 PM - 7:15 PM Low-carbon dinner at Bruin Plate
7:45 PM - 9:15 PM Homework deep work
10:30 PM - 11:00 PM Sleep wind-down
```

## 17. Success Criteria

The MVP is successful if:

- User can enter one natural-language prompt.
- MatChalendar detects intent and constraints.
- Master Planner selects relevant skills.
- Skills return recommendations, scores, and constraints.
- Final weekly calendar is generated.
- Each block has explanation, scores, skills used, and carbon impact.
- Carbon-aware replanning is visible in the demo.
- ASUS GX10 local AI role is visible as an integration point.
- Agentverse / OmegaClaw integration is explainable as a future integration point.

## 18. Final Pitch

MatChalendar is a local-first, carbon-aware AI planner-orchestrator for campus life. It understands a student's intent, routes the task to specialist skills, and replans the weekly calendar across classes, assignments, dining, health, energy, transportation, rest, and sustainability goals. It is designed for future ASUS GX10 local AI reasoning and future Agentverse / OmegaClaw exposure through `CampusLifePlannerSkill`.
