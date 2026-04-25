# PRD: MatChalendar — Local-first AI Planner-Orchestrator for Campus Life

## 1. Product Summary

**MatChalendar** is a local-first, carbon-aware AI planner-orchestrator for campus life.

It understands a student's natural language intent, routes planning tasks to specialist skills, and replans the user's weekly calendar across classes, assignments, dining, health, energy, transportation, rest, and sustainability goals.

中文定位：

**MatChalendar 是一个本地优先、碳感知的校园生活 AI 规划编排器。它先理解学生意图，再调用不同 specialist skills，最后重新规划完整 calendar。**

MatChalendar is not just a calendar app and not just a chatbot. It is a planning system that turns fragmented student decisions into an executable and explainable weekly calendar.

Core product line:

```text
MatChalendar = Master AI Planner + Specialist Skills + Food Data Intelligence + Carbon-aware Calendar Replanning
```

---

## 2. Core Product Idea

Most calendar apps only store time. Generic AI chatbots give advice but do not produce executable calendar blocks.

MatChalendar actively connects time, campus context, food choices, health goals, study workload, transportation, energy level, and carbon goals into one explainable plan.

Core logic:

```text
User prompt
→ Intent Understanding
→ Master AI Planner
→ Skill Router
→ Specialist Skills
→ Calendar Replanner
→ Explainable Weekly Calendar
```

Key principle:

```text
Skills propose. Planner decides. Calendar renders.
```

中文理解：

```text
Skill 提建议，Planner 做决策，Calendar 做展示。
```

The Master Planner owns the final calendar decision. Skills do not independently edit the final calendar. They return recommendations, constraints, scores, and evidence to the Master Planner.

---

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

- Students have fragmented daily decisions: classes, homework, meals, health, sleep, workouts, commuting, and carbon goals.
- Calendar apps record events but do not optimize life decisions.
- Generic AI chatbots give advice but do not create executable calendar blocks.
- Dining, health, energy, and carbon choices are connected, but students usually manage them separately.
- Sustainability advice is often abstract; MatChalendar turns it into concrete calendar decisions.
- Student schedule, health preferences, energy level, transportation choices, and carbon goals are sensitive lifestyle data.

---

## 4. Core User Flow

1. User opens MatChalendar.
2. User enters a natural language goal:

```text
Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency and took an Uber today. I also have class from 10 to 2 and homework tonight.
```

3. MatChalendar detects intent, constraints, and planning scope.
4. Master Planner selects relevant skills.
5. Skills return recommendations, constraints, scores, and evidence.
6. Calendar Replanner produces an updated weekly calendar.
7. User clicks each block to see explanations, scores, carbon impact, and skills used.
8. User accepts or regenerates the plan.

---

## 5. Master Planner Architecture

The **Master Planner** is the central orchestrator.

It is responsible for:

- understanding user intent
- detecting goals and constraints
- deciding planning scope: today, tomorrow, this week, or a specific date range
- selecting relevant skills
- collecting skill outputs
- resolving conflicts between skills
- generating the final weekly calendar
- passing final blocks to the Explanation Skill

Architecture:

```text
User Prompt
  ↓
Intent Parser
  ↓
Master Planner
  ↓
Skill Router
  ├─ Calendar Skill
  ├─ Dining Skill
  ├─ Study Skill
  ├─ Health Skill
  ├─ Energy Skill
  ├─ Transportation Skill
  ├─ Sustainability / Carbon Skill
  └─ Explanation Skill
  ↓
Calendar Replanner
  ↓
Final Weekly Calendar
```

The Master Planner should act like a planning director. It does not need to know every dining detail, nutrition rule, or transportation estimate itself. Instead, it asks specialist skills for domain-specific options and then makes the final calendar decision.

---

## 6. Skills System

MatChalendar uses internal specialist skills. These are not separate user-facing apps. They are internal capabilities called by the Master Planner.

### 6.1 Calendar Skill

Handles fixed events, free slots, conflicts, and calendar placement constraints.

Responsibilities:

- read fixed class / meeting / assignment events
- identify available time slots
- prevent schedule conflicts
- provide placement constraints for calendar blocks

### 6.2 Dining Skill

Recommends dining halls and meal options based on time, location, availability, user preferences, nutrition, and carbon impact.

Responsibilities:

- check dining hall availability
- recommend meal options
- use food profiles from the Food Data Intelligence Layer
- return candidate meals with health, energy, sustainability, and carbon scores

### 6.3 Study Skill

Schedules homework, deep work, review blocks, and study breaks based on deadlines and available time.

Responsibilities:

- estimate study time needed
- suggest deep work blocks
- avoid class conflicts
- include breaks when workload is high

### 6.4 Health Skill

Evaluates meals and activities based on health goals, protein needs, workout preferences, and recovery needs.

Responsibilities:

- evaluate whether meals match health goals
- recommend workouts or light movement
- consider recovery and sleep needs
- avoid unrealistic plans for low-energy days

### 6.5 Energy Skill

Adjusts planning intensity based on user energy level, meal heaviness, rest needs, and study workload.

Responsibilities:

- detect low-energy or high-stress days
- recommend lighter meals or lighter workouts when needed
- place breaks before or after demanding work blocks
- avoid overloading the calendar

### 6.6 Transportation Skill

Estimates travel choices such as walking, biking, bus, or ride-share, including time and carbon impact.

Responsibilities:

- estimate transportation time
- identify walking or transit-friendly options
- detect high-carbon transportation events such as Uber / ride-share
- return transportation constraints and carbon estimates

### 6.7 Sustainability / Carbon Skill

Tracks weekly carbon goals, detects high-carbon events, estimates carbon impact, and recommends low-carbon adjustments.

Responsibilities:

- maintain a weekly carbon goal or budget
- estimate carbon impact from transportation and food choices
- detect high-carbon events
- recommend low-carbon meals, walking routes, transit options, or future compensating choices

### 6.8 Explanation Skill

Explains why each calendar block was selected.

Responsibilities:

- explain the timing
- explain location choices
- explain health / energy / sustainability / carbon tradeoffs
- list skills used
- show data sources when possible

Important rule:

```text
Skills do not independently edit the final calendar. They return recommendations, constraints, scores, and evidence to the Master Planner.
```

---

## 7. Food Data Intelligence Layer

MatChalendar uses a shared **Food Data Intelligence Layer** before skill planning.

The system collects or loads UCLA dining menu data, extracts dietary and sustainability labels, estimates calories, protein, energy load, and carbon impact, then exposes enriched food profiles to Dining Skill, Health Skill, Energy Skill, and Sustainability / Carbon Skill.

Data flow:

```text
UCLA Dining Website / Mock Dining Data
  ↓
Food Data Pipeline
  ↓
Nutrition + Carbon Enrichment
  ↓
Shared Food Knowledge Base
  ↓
Dining Skill + Health Skill + Energy Skill + Carbon Skill
```

Dining, Health, Energy, and Carbon skills should share the same analyzed food dataset instead of scraping or estimating independently.

For the MVP, this layer may use mock UCLA dining data or scraped menu data when available. Nutrition and carbon values can be estimated for planning purposes.

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
    "source": "ucla_label_plus_estimator"
  },
  "scores": {
    "health": 0.88,
    "energy": 0.82,
    "sustainability": 0.94,
    "carbon": 0.94
  }
}
```

---

## 8. Carbon-aware Replanning

MatChalendar supports carbon-aware replanning.

If the user sets a weekly carbon reduction goal and then logs a high-carbon event, such as taking an Uber for an emergency, the planner updates the carbon budget and adjusts future recommendations.

Example:

```text
User goal:
I want to reduce carbon emissions this week.

New event:
I had an emergency and took an Uber today.

Planner response:
- Detect increased transportation emissions
- Update weekly carbon budget
- Ask Dining Skill for lower-carbon meal options
- Ask Health and Energy Skills to keep the meal realistic
- Replan dinner and future transportation choices
- Explain the tradeoff in the calendar block
```

Example explanation:

```text
You took an Uber today for an urgent event, which increased your transportation carbon impact. This dinner was shifted to a lower-carbon meal to help keep your weekly carbon goal on track while still supporting your energy and protein needs.
```

This turns sustainability from abstract advice into concrete calendar decisions.

---

## 9. Calendar Output and Explanation

The final output is an explainable weekly calendar.

Each calendar block should include:

- title
- type
- start time
- end time
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
How does it affect carbon goal?
Which skills contributed?
```

---

## 10. Frontend Experience

The frontend should make the planning process understandable in one screen.

Recommended layout:

```text
Left: AI Chatbox
Right: Weekly Calendar
Drawer: Explanation + Scores + Carbon Impact + Skills Used
Badge: Powered locally by ASUS Ascent GX10
```

The frontend should show:

- MatChalendar title
- left chatbox for user intent
- right weekly calendar
- clickable calendar blocks
- explanation drawer
- local AI badge
- carbon budget card
- skills used trace
- plan regeneration / accept plan button

Example status steps:

```text
Understanding your goal...
Checking your class schedule...
Analyzing dining options...
Estimating health, energy, and carbon tradeoffs...
Running local planner on ASUS Ascent GX10...
Replanning your weekly calendar...
```

---

## 11. Backend Architecture

Suggested backend structure:

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

Suggested API endpoints:

```text
POST /api/plan
GET /api/dining
GET /api/demo-schedule
GET /api/health
```

The MVP can start with deterministic skills and a rule-based calendar replanner. Local AI can then be added for intent understanding, option ranking, and explanations.

---

## 12. Data Model

Example PlanResponse:

```json
{
  "summary": "Your week was replanned to balance class, homework, energy, meals, and your carbon reduction goal.",
  "generated_by": "asus_gx10_local_master_planner",
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
      "start": "2026-04-25T18:30:00",
      "end": "2026-04-25T19:15:00",
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
        "carbon",
        "health",
        "energy",
        "calendar"
      ],
      "data_sources": [
        "ucla_dining_data",
        "carbon_factors",
        "user_schedule",
        "local_planner"
      ]
    }
  ]
}
```

---

## 13. ASUS GX10 Local AI Integration

ASUS Ascent GX10 is used as the local AI planning server.

Local AI responsibilities:

- intent understanding
- planner reasoning
- skill routing assistance
- explanation generation
- ranking candidate options
- summarizing tradeoffs

Sensitive student context such as schedule, health preferences, energy level, transportation choices, and carbon goals should be reasoned over locally when possible.

Possible environment variables:

```bash
GX10_OLLAMA_URL=http://GX10_IP:11434/api/generate
LOCAL_MODEL_NAME=gemma3:4b
USE_LOCAL_AI=true
FALLBACK_TO_MOCK=true
```

If local AI is unavailable, the backend should still return a deterministic fallback plan so the demo remains stable.

---

## 14. Agentverse / OmegaClaw Integration

MatChalendar exposes its planner as one external campus-life planning capability.

External skill:

```text
CampusLifePlannerSkill
```

Internal skills:

```text
Calendar, Dining, Study, Health, Energy, Transportation, Sustainability / Carbon, Explanation
```

Call chain:

```text
OmegaClaw
  ↓
CampusLifePlannerSkill
  ↓
Agentverse
  ↓
MatChalendar Campus Planner Agent
  ↓
Master Planner
  ↓
Internal Skills
  ↓
Final Calendar Plan
```

The external skill should return a concise plan with calendar blocks, reasons, scores, carbon impact, and skills used.

---

## 15. LA Hacks Track Alignment

### ASUS / Local AI

MatChalendar uses ASUS Ascent GX10 for local AI planning over sensitive student context, including schedule, health preferences, energy level, transportation choices, and carbon goals.

### Fetch.ai / Agentverse

MatChalendar exposes the campus planner as an Agentverse specialist agent.

### OmegaClaw Skill

OmegaClaw can invoke CampusLifePlannerSkill to generate a full campus-life calendar plan.

### Sustainability / Social Impact

MatChalendar turns carbon reduction from abstract advice into concrete calendar decisions through carbon-aware replanning.

---

## 16. MVP Demo Scenario

Demo prompt:

```text
Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency and took an Uber today. I also have class from 10 to 2 and homework tonight.
```

Expected system behavior:

- Detect intent: reduce weekly carbon emissions.
- Detect event: emergency Uber.
- Detect constraints: class from 10 to 2, homework tonight.
- Select skills: calendar, transportation, carbon, dining, health, energy, study, explanation.
- Update carbon budget.
- Recommend low-carbon dinner.
- Schedule homework deep work.
- Generate weekly calendar blocks.
- Show explanation drawer with carbon impact and skills used.

Example final plan:

```text
10:00 AM - 2:00 PM Class
2:15 PM - 2:45 PM Recovery walk
6:30 PM - 7:15 PM Low-carbon dinner at Bruin Plate
7:45 PM - 9:15 PM Homework deep work
10:30 PM - 11:00 PM Sleep wind-down
```

Example explanation:

```text
Low-carbon dinner at Bruin Plate

Reason:
You took an Uber today for an urgent event, which increased your transportation carbon impact. This dinner was shifted to a lower-carbon meal to help keep your weekly carbon goal on track while still supporting your energy and protein needs.

Scores:
Time: 86
Health: 90
Energy: 82
Sustainability: 94
Carbon: 92

Carbon impact:
Estimated: 0.7 kg CO2e
Compared with original option: -1.1 kg CO2e

Skills used:
Dining Skill, Carbon Skill, Health Skill, Energy Skill, Calendar Skill
```

---

## 17. Success Criteria

The MVP is successful if:

- User can enter one natural language prompt.
- MatChalendar detects intent and constraints.
- Master Planner selects relevant skills.
- Skills return recommendations, scores, and constraints.
- Final weekly calendar is generated.
- Each block has explanation, scores, skills used, and carbon impact.
- Carbon-aware replanning is visible in the demo.
- ASUS GX10 local AI role is visible.
- Agentverse / OmegaClaw integration is explainable or minimally demoable.

---

## 18. Final Pitch

MatChalendar is a local-first, carbon-aware AI planner-orchestrator for campus life. It understands a student's intent, routes the task to specialist skills, and replans the weekly calendar across classes, assignments, dining, health, energy, transportation, rest, and sustainability goals. It uses ASUS Ascent GX10 for local AI reasoning and exposes the planner as a CampusLifePlannerSkill through Agentverse and OmegaClaw.
