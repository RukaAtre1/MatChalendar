const plannerSteps = [
  "Understanding goal",
  "Parsing intent",
  "Routing skills",
  "Running internal skills",
  "Replanning calendar",
  "Building explanations",
  "Rendering PlanResponse"
];

const plannerRequestTimeoutMs = 30000;

const skillLabels = {
  calendar: "Calendar",
  transportation: "Transportation",
  sustainability_carbon: "Carbon",
  carbon: "Carbon",
  dining: "Dining",
  health: "Health",
  energy: "Energy",
  study: "Study",
  explanation: "Explanation"
};

const scoreLabels = {
  time: "Timing",
  health: "Health",
  energy: "Energy",
  sustainability: "Balance",
  carbon: "Carbon"
};

const fallbackPlanResponse = {
  summary: "A health-first campus week that protects energy and complete meals before optimizing climate impact.",
  generated_by: "local_fallback_plan_response",
  metadata: {
    generated_by: "local_fallback_plan_response",
    planner_mode: "frontend_local_fallback",
    integrations_used: ["frontend_fallback"],
    fallback_reason: "Backend unavailable.",
    local_ai_available: false,
    asi_one_available: false,
    memory_used: false,
    soul_used: false
  },
  response_version: "mvp-0.1",
  intent: {
    primary_goal: "reduce_weekly_carbon",
    planning_scope: "this_week",
    detected_constraints: ["class_10_to_2", "homework_tonight", "emergency_uber"],
    skills_used: [
      "calendar",
      "study",
      "transportation",
      "sustainability_carbon",
      "dining",
      "health",
      "energy",
      "explanation"
    ]
  },
  carbon_budget: {
    weekly_target_kg_co2e: 35.0,
    current_estimated_kg_co2e: 19.4,
    status: "slightly_above_expected_today",
    adjustment_strategy: "lower_carbon_dining_and_walkable_routes"
  },
  memory_update_suggestion: {
    should_update: false,
    reason: "",
    markdown_patch: ""
  },
  plan_blocks: [
    {
      id: "block_class_mon",
      title: "PHYSCI 5",
      type: "class",
      start: "2026-04-27T10:00:00",
      end: "2026-04-27T14:00:00",
      location: "Boelter Hall",
      reason: "This fixed class block is protected before meals, recovery, and study work are placed around it.",
      scores: { time: 0.98, health: 0.66, energy: 0.7, sustainability: 0.72, carbon: 0.84 },
      carbon: { estimated_co2e_kg: 0.1, category: "calendar" },
      skills_used: ["calendar"],
      data_sources: ["user_schedule"]
    },
    {
      id: "block_walk_mon",
      title: "Walk break",
      type: "recovery",
      start: "2026-04-27T14:15:00",
      end: "2026-04-27T14:45:00",
      location: "Bruin Walk",
      reason: "A short walk after class creates an energy reset without adding more transportation emissions after the emergency Uber.",
      scores: { time: 0.88, health: 0.84, energy: 0.8, sustainability: 0.9, carbon: 0.96 },
      carbon: { estimated_co2e_kg: 0, category: "transportation" },
      skills_used: ["calendar", "transportation", "energy", "health", "sustainability_carbon"],
      data_sources: ["carbon_factors", "user_schedule"]
    },
    {
      id: "block_dinner_mon",
      title: "Bruin Plate",
      type: "meal",
      start: "2026-04-27T18:30:00",
      end: "2026-04-27T19:15:00",
      location: "Bruin Plate",
      reason: "The emergency Uber raised today's transportation impact, so dinner shifts toward a plant-forward option while preserving protein and evening energy.",
      scores: { time: 0.86, health: 0.9, energy: 0.82, sustainability: 0.94, carbon: 0.92 },
      carbon: { estimated_co2e_kg: 0.7, category: "dining" },
      menu_sections: [
        { station: "Freshly Bowled", items: [{ name: "Create-Your-Own Omelet Bar", quantity: 0 }] },
        { station: "Harvest", items: [{ name: "Plant-based grain bowl", quantity: 1 }, { name: "Seasonal vegetables", quantity: 1 }] }
      ],
      dining_choices: [
        {
          dining_hall: "De Neve",
          estimated_co2e_kg: 0.6,
          menu_sections: [
            { station: "Harvest", items: [{ name: "Lentil vegetable plate", quantity: 1 }, { name: "Seasonal greens", quantity: 1 }] },
            { station: "Freshly Bowled", items: [{ name: "Build-your-own grain bowl", quantity: 0 }] }
          ]
        },
        {
          dining_hall: "Epicuria",
          estimated_co2e_kg: 0.8,
          menu_sections: [
            { station: "Mediterranean Table", items: [{ name: "Chickpea vegetable stew", quantity: 1 }, { name: "Herbed couscous", quantity: 1 }] },
            { station: "Garden", items: [{ name: "Seasonal greens", quantity: 1 }] }
          ]
        }
      ],
      skills_used: ["dining", "sustainability_carbon", "health", "energy", "calendar"],
      data_sources: ["ucla_dining_mock", "carbon_factors", "local_planner"]
    },
    {
      id: "block_study_mon",
      title: "Math homework",
      type: "study",
      start: "2026-04-27T19:45:00",
      end: "2026-04-27T21:15:00",
      location: "Powell Library",
      reason: "Homework stays tonight, but starts after dinner and a transition buffer so the plan does not stack heavy work immediately after class.",
      scores: { time: 0.89, health: 0.72, energy: 0.78, sustainability: 0.8, carbon: 0.88 },
      carbon: { estimated_co2e_kg: 0.05, category: "study" },
      skills_used: ["study", "calendar", "energy", "explanation"],
      data_sources: ["user_schedule", "local_planner"]
    },
    {
      id: "block_winddown_mon",
      title: "Wind-down",
      type: "rest",
      start: "2026-04-27T22:30:00",
      end: "2026-04-27T23:00:00",
      location: "Dorm",
      reason: "A short wind-down block protects recovery after a day with class, emergency travel, and homework.",
      scores: { time: 0.82, health: 0.88, energy: 0.86, sustainability: 0.74, carbon: 0.9 },
      carbon: { estimated_co2e_kg: 0, category: "rest" },
      skills_used: ["health", "energy", "calendar"],
      data_sources: ["local_planner"]
    },
    {
      id: "block_transit_tue",
      title: "Big Blue Bus",
      type: "commute",
      start: "2026-04-28T09:20:00",
      end: "2026-04-28T09:50:00",
      location: "Big Blue Bus",
      reason: "Tomorrow's route uses transit where the schedule allows, compensating for today's ride-share without creating a rushed morning.",
      scores: { time: 0.78, health: 0.7, energy: 0.74, sustainability: 0.91, carbon: 0.93 },
      carbon: { estimated_co2e_kg: 0.3, category: "transportation" },
      skills_used: ["transportation", "sustainability_carbon", "calendar"],
      data_sources: ["carbon_factors", "user_schedule"]
    },
    {
      id: "block_lunch_tue",
      title: "De Neve",
      type: "meal",
      start: "2026-04-28T12:00:00",
      end: "2026-04-28T12:45:00",
      location: "De Neve",
      reason: "A lighter lunch keeps afternoon energy steady while continuing the lower-carbon dining pattern.",
      scores: { time: 0.84, health: 0.88, energy: 0.85, sustainability: 0.92, carbon: 0.9 },
      carbon: { estimated_co2e_kg: 0.6, category: "dining" },
      menu_sections: [
        { station: "Harvest", items: [{ name: "Lentil vegetable plate", quantity: 1 }, { name: "Seasonal greens", quantity: 1 }] },
        { station: "Freshly Bowled", items: [{ name: "Build-your-own grain bowl", quantity: 0 }] }
      ],
      dining_choices: [
        {
          dining_hall: "Bruin Plate",
          estimated_co2e_kg: 0.7,
          menu_sections: [
            { station: "Freshly Bowled", items: [{ name: "Create-Your-Own Omelet Bar", quantity: 0 }] },
            { station: "Harvest", items: [{ name: "Plant-based grain bowl", quantity: 1 }, { name: "Seasonal vegetables", quantity: 1 }] }
          ]
        },
        {
          dining_hall: "Epicuria",
          estimated_co2e_kg: 0.8,
          menu_sections: [
            { station: "Mediterranean Table", items: [{ name: "Chickpea vegetable stew", quantity: 1 }, { name: "Herbed couscous", quantity: 1 }] },
            { station: "Garden", items: [{ name: "Seasonal greens", quantity: 1 }] }
          ]
        }
      ],
      skills_used: ["dining", "health", "energy", "sustainability_carbon"],
      data_sources: ["ucla_dining_mock", "carbon_factors"]
    },
    {
      id: "block_review_wed",
      title: "CS review",
      type: "study",
      start: "2026-04-29T15:00:00",
      end: "2026-04-29T16:15:00",
      location: "Study Commons",
      reason: "A midweek review prevents Monday night from becoming the only academic catch-up slot.",
      scores: { time: 0.84, health: 0.7, energy: 0.79, sustainability: 0.76, carbon: 0.86 },
      carbon: { estimated_co2e_kg: 0.05, category: "study" },
      skills_used: ["study", "calendar", "energy"],
      data_sources: ["user_schedule"]
    },
    {
      id: "block_workout_thu",
      title: "Wooden workout",
      type: "recovery",
      start: "2026-04-30T16:00:00",
      end: "2026-04-30T17:00:00",
      location: "John Wooden Center",
      reason: "A light workout lands in a low-conflict window and supports health without making the week feel overpacked.",
      scores: { time: 0.8, health: 0.92, energy: 0.75, sustainability: 0.78, carbon: 0.88 },
      carbon: { estimated_co2e_kg: 0.02, category: "health" },
      skills_used: ["health", "energy", "calendar"],
      data_sources: ["local_planner"]
    },
    {
      id: "block_market_fri",
      title: "Westwood grocery",
      type: "commute",
      start: "2026-05-01T17:15:00",
      end: "2026-05-01T18:00:00",
      location: "Westwood Village",
      reason: "A walkable grocery stop avoids a short ride-share trip and sets up lower-waste weekend meals.",
      scores: { time: 0.82, health: 0.78, energy: 0.74, sustainability: 0.93, carbon: 0.91 },
      carbon: { estimated_co2e_kg: 0, category: "transportation" },
      skills_used: ["transportation", "sustainability_carbon", "dining", "calendar"],
      data_sources: ["carbon_factors", "local_planner"]
    },
    {
      id: "block_dinner_fri",
      title: "Dorm dinner",
      type: "meal",
      start: "2026-05-01T18:30:00",
      end: "2026-05-01T19:15:00",
      location: "Dorm kitchen",
      reason: "Dinner uses the grocery stop to keep the meal low-carbon and reduce packaging waste before the weekend.",
      scores: { time: 0.8, health: 0.86, energy: 0.82, sustainability: 0.95, carbon: 0.93 },
      carbon: { estimated_co2e_kg: 0.5, category: "dining" },
      skills_used: ["dining", "health", "energy", "sustainability_carbon"],
      data_sources: ["carbon_factors", "local_planner"]
    },
    {
      id: "block_bike_sat",
      title: "Study cafe",
      type: "study",
      start: "2026-05-02T10:30:00",
      end: "2026-05-02T12:00:00",
      location: "Study cafe",
      reason: "A weekend study block is paired with biking instead of a car trip, keeping academic progress and carbon goals aligned.",
      scores: { time: 0.83, health: 0.8, energy: 0.84, sustainability: 0.9, carbon: 0.92 },
      carbon: { estimated_co2e_kg: 0.05, category: "transportation" },
      skills_used: ["study", "transportation", "energy", "sustainability_carbon"],
      data_sources: ["carbon_factors", "user_schedule"]
    },
    {
      id: "block_meal_prep_sun",
      title: "Meal prep",
      type: "meal",
      start: "2026-05-03T17:00:00",
      end: "2026-05-03T18:15:00",
      location: "Dorm kitchen",
      reason: "Sunday meal prep turns leftover groceries into weekday meals, reducing food waste and lowering next week's dining impact.",
      scores: { time: 0.78, health: 0.88, energy: 0.82, sustainability: 0.96, carbon: 0.94 },
      carbon: { estimated_co2e_kg: 0.4, category: "dining" },
      skills_used: ["dining", "health", "energy", "sustainability_carbon", "calendar"],
      data_sources: ["carbon_factors", "local_planner"]
    }
  ]
};

const initialCarbonBudget = {
  weekly_target_kg_co2e: 35.0,
  current_estimated_kg_co2e: 0
};

const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const startHour = 8;
const endHour = 24;
const headerHeight = 32;
const hourHeight = 36;

const form = document.querySelector("#plannerForm");
const trace = document.querySelector("#compactTrace");
const workspace = document.querySelector(".workspace");
const calendarGrid = document.querySelector("#calendarGrid");
const regenerateBtn = document.querySelector("#regenerateBtn");
const detailDrawer = document.querySelector(".detail-drawer");
const drawerEmpty = document.querySelector("#drawerEmpty");
const drawerContent = document.querySelector("#drawerContent");
const closeDrawer = document.querySelector("#closeDrawer");
const promptInput = document.querySelector("#promptInput");
const menuSection = document.querySelector("#menuSection");
const menuSections = document.querySelector("#menuSections");
const nutritionSection = document.querySelector("#nutritionSection");
const nutritionDetails = document.querySelector("#nutritionDetails");
const mealStatus = document.querySelector("#mealStatus");
const whySection = document.querySelector("#whySection");
const whyDetails = document.querySelector("#whyDetails");
const activitySection = document.querySelector("#activitySection");
const activityDetails = document.querySelector("#activityDetails");
const transportSection = document.querySelector("#transportSection");
const transportDetails = document.querySelector("#transportDetails");
const choicesSection = document.querySelector("#choicesSection");
const diningChoices = document.querySelector("#diningChoices");
const climateDetails = document.querySelector("#climateDetails");
const plannerBadge = document.querySelector("#plannerBadge");
const memoryCard = document.querySelector("#memoryCard");
const memoryReason = document.querySelector("#memoryReason");
const memoryPatch = document.querySelector("#memoryPatch");
const saveMemoryBtn = document.querySelector("#saveMemoryBtn");
const ignoreMemoryBtn = document.querySelector("#ignoreMemoryBtn");
const openMemoryBtn = document.querySelector("#openMemoryBtn");
const closeMemoryBtn = document.querySelector("#closeMemoryBtn");
const memoryViewer = document.querySelector("#memoryViewer");
const memoryViewerContent = document.querySelector("#memoryViewerContent");

let selectedBlock = null;
let currentBlocks = [];
let pendingMemoryPatch = "";
let currentMemorySections = [];

function renderTrace(activeIndex = -1, complete = false, steps = plannerSteps) {
  trace.hidden = false;
  trace.innerHTML = steps
    .map((step, index) => {
      const state = complete || index < activeIndex ? "done" : index === activeIndex ? "active" : "";
      return `<li class="${state}">${escapeHtml(step)}</li>`;
    })
    .join("");
}

function renderCalendar(blocks) {
  currentBlocks = blocks.map(normalizeBlock);
  calendarGrid.innerHTML = "";

  const rail = document.createElement("div");
  rail.className = "time-rail";
  rail.style.height = `${headerHeight + (endHour - startHour) * hourHeight}px`;

  for (let hour = startHour; hour <= endHour; hour += 2) {
    const label = document.createElement("div");
    label.className = "time-label";
    label.style.top = `${headerHeight + (hour - startHour) * hourHeight - 7}px`;
    label.textContent = hour === 24 ? "12 AM" : formatHour(hour);
    rail.appendChild(label);
  }
  calendarGrid.appendChild(rail);

  days.forEach((day) => {
    const column = document.createElement("div");
    column.className = "day-column";
    column.style.height = `${headerHeight + (endHour - startHour) * hourHeight}px`;

    const head = document.createElement("div");
    head.className = "day-head";
    head.textContent = day;
    column.appendChild(head);

    for (let hour = startHour; hour <= endHour; hour += 1) {
      const line = document.createElement("div");
      line.className = "hour-line";
      line.style.top = `${headerHeight + (hour - startHour) * hourHeight}px`;
      column.appendChild(line);
    }

    currentBlocks
      .filter((block) => block.day === day)
      .forEach((block) => {
        const button = document.createElement("button");
        button.type = "button";
        const footprintLevel = carbonLevel(block);
        button.className = `calendar-block block-${block.type} footprint-${footprintLevel}`;
        button.dataset.blockId = block.id;
        button.style.top = `${headerHeight + minutesFromStart(block.start)}px`;
        button.style.height = `${Math.max(38, durationMinutes(block.start, block.end) * (hourHeight / 60))}px`;
        button.innerHTML = `
          <span class="block-top">
            <strong>${calendarBlockTitle(block)}</strong>
            <time>${compactTimeRange(block.start, block.end)}</time>
          </span>
          <span class="block-bottom">
            <span>${block.location}</span>
            ${mealCalendarBadge(block)}
            <span class="carbon-mini-pill">${carbonFootprintLabel(block)}</span>
          </span>
        `;
        button.addEventListener("click", () => selectBlock(block.id));
        column.appendChild(button);
      });

    calendarGrid.appendChild(column);
  });

  if (currentBlocks.length === 0) {
    const empty = document.createElement("div");
    empty.className = "calendar-empty";
    empty.textContent = "Calendar will populate after Run Planner.";
    calendarGrid.appendChild(empty);
  }
}

function normalizeBlock(block) {
  return {
    ...block,
    day: block.day || dayFromIso(block.start)
  };
}

function applyPlan(plan) {
  renderCalendar(plan.plan_blocks || []);
  renderCarbonBudget(plan.carbon_budget);
  renderPlannerMetadata(plan);
  renderMemorySuggestion(plan.memory_update_suggestion);
  const executionSteps = buildExecutionSteps(plan);
  renderTrace(executionSteps.length - 1, true, executionSteps);
  clearSelection();
}

function buildExecutionSteps(plan) {
  const contextSteps = (plan.ai_planner_context?.priority_order || []).map(shortPolicyPhrase).filter(Boolean);
  const strategySteps = strategyToSteps(plan.calendar_strategy || plan.explanation_draft || "");
  const blockSteps = blocksToSteps(plan.plan_blocks || []);
  const steps = uniqueList([...contextSteps, ...strategySteps, ...blockSteps]);
  return steps.length > 0 ? steps.slice(0, 6) : plannerSteps;
}

function strategyToSteps(strategy) {
  const cleaned = String(strategy)
    .replace(/^Your week was replanned with this strategy:\s*/i, "")
    .trim();
  if (!cleaned) return [];

  const numbered = [];
  const numberedPattern = /\(\d+\)\s*([\s\S]*?)(?=(?:,\s*)?\(\d+\)|$)/g;
  let match = numberedPattern.exec(cleaned);
  while (match) {
    numbered.push(match[1]);
    match = numberedPattern.exec(cleaned);
  }

  const clauses = numbered.length > 0
    ? numbered
    : cleaned
        .split(/(?:;|\.\s+|\band\b\s+(?=\w))/i)
        .filter((part) => part.length > 0);

  return clauses.map(shortPolicyPhrase).filter(Boolean);
}

function shortPolicyPhrase(value) {
  const text = String(value)
    .replace(/\s+/g, " ")
    .replace(/[.)]+$/g, "")
    .trim();
  const lower = text.toLowerCase();
  if (!text) return "";

  if (lower.includes("10-2") || lower.includes("10 to 2")) return "Protect 10-2 class block";
  if (lower.includes("fixed") || lower.includes("class")) return "Protect fixed class blocks";
  if (lower.includes("homework")) return "Schedule homework tonight";
  if (lower.includes("focused") || lower.includes("study")) return "Schedule focused study blocks";
  if (lower.includes("walk") || lower.includes("bike") || lower.includes("transit") || lower.includes("transportation")) {
    return "Walk, bike, and use transit";
  }
  if (lower.includes("vegetarian")) return "Prefer vegetarian meals";
  if (lower.includes("plant") || lower.includes("dining") || lower.includes("meal") || lower.includes("waste")) {
    return "Choose low-waste plant-forward meals";
  }
  if (lower.includes("carbon") || lower.includes("sustainability")) return "Track carbon-aware choices";
  if (lower.includes("cluster") || lower.includes("trip")) return "Cluster errands and activities";
  if (lower.includes("recovery") || lower.includes("energy") || lower.includes("wind-down")) return "Protect recovery time";
  if (lower.includes("meeting") || lower.includes("group")) return "Schedule group project time";

  return sentenceCase(text)
    .replace(/^Preserving\b/i, "Protect")
    .replace(/^Scheduling\b/i, "Schedule")
    .replace(/^Using\b/i, "Use")
    .replace(/^Choosing\b/i, "Choose")
    .replace(/^Clustering\b/i, "Cluster");
}

function blocksToSteps(blocks) {
  return blocks.map(blockToStep).filter(Boolean);
}

function blockToStep(block) {
  const title = block.title || block.location || "";
  if (block.type === "class") return `Protect ${title} block`;
  if (block.type === "study") return `Place ${title}`;
  if (block.type === "meal") return `Plan low-carbon ${block.location || "meal"}`;
  if (block.type === "commute") return `Use ${title || block.location}`;
  if (block.type === "recovery" || block.type === "rest") return `Add ${title}`;
  return "";
}

function uniqueList(values) {
  const seen = new Set();
  return values.filter((value) => {
    const key = value.toLowerCase();
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function sentenceCase(value) {
  const text = String(value).trim();
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : "";
}

function renderPlannerMetadata(plan) {
  const metadata = plan.metadata || {};
  const mode = metadata.planner_mode || plan.generated_by || "unknown";
  plannerBadge.innerHTML = `<span class="status-dot"></span>${plannerModeLabel(mode)}`;
}

function plannerModeLabel(mode) {
  if (mode === "gx10_local_ai") return "GX10 assisted";
  if (mode === "asi_one_hosted_ai") return "ASI:One assisted";
  if (mode === "frontend_local_fallback") return "Frontend fallback";
  return "Deterministic fallback";
}

function renderMemorySuggestion(suggestion) {
  const shouldShow = suggestion?.should_update && suggestion?.markdown_patch;
  memoryCard.hidden = !shouldShow;
  pendingMemoryPatch = shouldShow ? suggestion.markdown_patch : "";
  if (!shouldShow) return;
  memoryReason.textContent = suggestion.reason || "The planner found a preference that may be useful later.";
  memoryPatch.textContent = suggestion.markdown_patch;
  memoryPatch.setAttribute("contenteditable", "true");
  memoryPatch.setAttribute("role", "textbox");
  memoryPatch.setAttribute("aria-label", "Editable memory preference suggestion");
}

function renderCarbonBudget(budget) {
  if (!budget) return;
  const current = budget.current_estimated_kg_co2e;
  const target = budget.weekly_target_kg_co2e;
  const percent = Math.min(100, Math.round((current / target) * 100));
  const budgetCard = document.querySelector(".carbon-card");
  const meter = document.querySelector("#carbonMeter");
  const budgetLevel = carbonBudgetLevel(current, target);

  document.querySelector("#carbonCurrent").textContent = current === 0 ? "0" : current.toFixed(1);
  document.querySelector("#carbonTarget").textContent = `/ ${formatKg(target)} kg CO2e`;
  document.querySelector("#carbonPercent").textContent = `${percent}%`;
  meter.style.width = `${percent}%`;
  budgetCard.classList.remove(
    "budget-footprint-zero",
    "budget-footprint-low",
    "budget-footprint-moderate",
    "budget-footprint-high"
  );
  budgetCard.classList.add(`budget-footprint-${budgetLevel}`);
  budgetCard.dataset.footprintLevel = budgetLevel;
}

function selectBlock(blockId) {
  const block = currentBlocks.find((item) => item.id === blockId);
  if (!block) return;
  selectedBlock = block;

  document.querySelectorAll(".calendar-block").forEach((button) => {
    button.classList.toggle("selected", button.dataset.blockId === blockId);
  });

  workspace.classList.add("drawer-open");
  detailDrawer.hidden = false;
  drawerEmpty.hidden = true;
  drawerContent.hidden = false;

  document.querySelector("#blockType").textContent = block.type;
  document.querySelector("#blockTitle").textContent = block.type === "meal" ? mealPanelTitle(block) : block.title;
  document.querySelector("#blockMeta").textContent = `${block.day} | ${timeRange(block.start, block.end)} | ${block.location}`;
  renderMealStatus(block);
  renderMenu(block);
  renderNutrition(block);
  renderClimate(block);
  renderWhy(block);
  renderActivity(block);
  renderTransport(block);
  renderDiningChoices(block);
}

function renderMealStatus(block) {
  const shouldShow = block.type === "meal";
  mealStatus.hidden = !shouldShow;
  if (!shouldShow) {
    mealStatus.innerHTML = "";
    return;
  }

  const healthLabel = block.adequacy_status === "complete_meal" ? "Health-first" : "Snack/side";
  mealStatus.innerHTML = `
    <span class="${block.adequacy_status === "complete_meal" ? "balanced-badge" : "meal-warning"}">${escapeHtml(healthLabel)}</span>
    <span class="carbon-badge">${escapeHtml(carbonBadgeLabel(block))}</span>
  `;
}

function renderMenu(block) {
  const sections = block.type === "meal" ? mealCompositionGroups(block) : [];
  const shouldShowMenu = block.type === "meal" && sections.length > 0;

  menuSection.hidden = !shouldShowMenu;
  menuSections.innerHTML = shouldShowMenu
    ? sections
        .map((section) => `
          <article class="meal-composition-card">
            <h3>${escapeHtml(section.label)}</h3>
            <ul>
              ${(section.items || []).map(compositionItemMarkup).join("")}
            </ul>
          </article>
        `)
        .join("")
    : "";
}

function renderNutrition(block) {
  const nutrition = block.estimated_nutrition || block.nutrition || {};
  const shouldShow = block.type === "meal" && Object.keys(nutrition).length > 0;
  nutritionSection.hidden = !shouldShow;
  nutritionDetails.innerHTML = shouldShow
    ? [
        metricMarkup("Overall", healthScoreLabel(block), ""),
        metricMarkup("Energy", energyFitLabel(block, nutrition), ""),
        metricMarkup("Protein", proteinFitLabel(nutrition.protein_g), ""),
        metricMarkup("Fiber", fiberFitLabel(nutrition.fiber_g), ""),
        metricMarkup("Added sugar", addedSugarFitLabel(nutrition.added_sugar_g), ""),
        metricMarkup("Sodium", sodiumFitLabel(nutrition.sodium_mg), ""),
        metricMarkup("Calories", nutrition.calories, "kcal"),
        metricMarkup("Fat", nutrition.fat_g, "g")
      ].join("")
    : "";
}

function renderClimate(block) {
  const footprint = Number(block.carbon?.estimated_co2e_kg || 0);
  if (block.type !== "meal") {
    climateDetails.innerHTML = `
      <div class="impact-row"><span>Estimated footprint</span><strong>${formatKg(footprint)} kg CO2e</strong></div>
    `;
    return;
  }

  const comparison = climateComparisonCopy(footprint);
  climateDetails.innerHTML = `
    <div class="climate-box">
      <strong>${formatKg(footprint)} kg CO2e</strong>
      <span>${escapeHtml(carbonRatingLabel(footprint))} carbon rating</span>
      <p>${escapeHtml(comparison.better)}</p>
      <p>${escapeHtml(comparison.higher)}</p>
    </div>
  `;
}

function renderWhy() {
  whySection.hidden = true;
  whyDetails.textContent = "";
}

function renderActivity(block) {
  const activity = block.activity || {};
  const shouldShow = Object.keys(activity).length > 0;
  activitySection.hidden = !shouldShow;
  activityDetails.innerHTML = shouldShow
    ? [
        metricMarkup("Intensity", activity.intensity || "", ""),
        metricMarkup("Duration", activity.duration_minutes, "min"),
        metricMarkup("Burn", activity.calories_burned, "kcal"),
        metricMarkup("Method", activity.method || "", "")
      ].join("")
    : "";
}

function renderTransport(block) {
  const transport = block.transportation || {};
  const shouldShow = Object.keys(transport).length > 0;
  transportSection.hidden = !shouldShow;
  transportDetails.innerHTML = shouldShow
    ? [
        metricMarkup("Mode", transport.mode || "", ""),
        metricMarkup("Time", transport.estimated_minutes, "min"),
        metricMarkup("Footprint", transport.estimated_co2e_kg, "kg CO2e")
      ].join("")
    : "";
}

function renderDiningChoices(block) {
  const choices = Array.isArray(block.dining_choices)
    ? block.dining_choices.filter((choice) => choice.dining_hall !== block.location)
    : [];
  const shouldShowChoices = block.type !== "meal" && choices.length > 0;

  choicesSection.hidden = !shouldShowChoices;
  diningChoices.innerHTML = shouldShowChoices
    ? choices.map((choice, index) => diningChoiceMarkup(choice, index)).join("")
    : "";

  if (!shouldShowChoices) return;

  diningChoices.querySelectorAll(".dining-choice").forEach((choiceEl) => {
    choiceEl.addEventListener("toggle", () => {
      if (!choiceEl.open) return;
      diningChoices.querySelectorAll(".dining-choice").forEach((otherEl) => {
        if (otherEl !== choiceEl) otherEl.open = false;
      });
    });
  });
}

function diningChoiceMarkup(choice, index) {
  const sections = Array.isArray(choice.menu_sections) ? choice.menu_sections : [];
  const statusLabel = choice.adequacy_status === "complete_meal" ? "Balanced meal" : "Snack/side";
  return `
    <details class="dining-choice" ${index === 0 ? "open" : ""}>
      <summary>
        <span class="choice-name">${escapeHtml(choice.meal_name || choice.dining_hall)}</span>
        <span class="choice-status">${escapeHtml(statusLabel)}</span>
        <strong>${formatKg(choice.estimated_co2e_kg || 0)} kg CO2e</strong>
        <span class="choice-arrow" aria-hidden="true">›</span>
      </summary>
      <div class="choice-menu">
        ${sections.map((section) => `
          <article class="menu-station">
            <h3>${escapeHtml(section.station)}</h3>
            <ul>
              ${(section.items || []).map(menuItemMarkup).join("")}
            </ul>
          </article>
        `).join("")}
      </div>
    </details>
  `;
}

function menuItemMarkup(item) {
  const normalizedItem = typeof item === "string"
    ? { name: item, quantity: 1 }
    : { name: item.name, quantity: item.quantity ?? 1 };
  return `
    <li>
      <span>${escapeHtml(normalizedItem.name)}</span>
      <strong>${menuItemDetail(normalizedItem)}</strong>
    </li>
  `;
}

function compositionItemMarkup(item) {
  const normalizedItem = typeof item === "string"
    ? { name: item, quantity: 1 }
    : item;
  return `
    <li>
      <span>${escapeHtml(formatFoodName(normalizedItem.name))}</span>
      <strong>${escapeHtml(portionLabel(normalizedItem))}</strong>
    </li>
  `;
}

function metricMarkup(label, value, unit) {
  if (value === undefined || value === null || value === "") return "";
  const display = typeof value === "number" ? formatQuantity(value) : escapeHtml(value);
  return `
    <div class="metric-chip">
      <span>${escapeHtml(label)}</span>
      <strong>${display}${unit ? ` ${escapeHtml(unit)}` : ""}</strong>
    </div>
  `;
}

function mealPanelTitle(block) {
  const mealType = block.meal_type || "meal";
  const location = block.location || "campus dining";
  if (block.adequacy_status === "complete_meal") return `Balanced ${mealType} at ${location}`;
  return block.meal_name || block.title || `${formatLabel(mealType)} at ${location}`;
}

function mealCompositionGroups(block) {
  const plate = block.plate_balance || {};
  const menuSections = Array.isArray(block.menu_sections) ? block.menu_sections : [];
  const mealItems = flattenMenuItems(menuSections);
  const classified = classifyMealItems(mealItems);
  const groups = [
    { label: "Protein", items: classified.protein },
    { label: "Whole grain / carb", items: classified.carb },
    { label: "Vegetables", items: classified.vegetable }
  ];

  fillMissingCompositionGroups(groups, plate, classified.optional);

  const optionalItems = classified.optional.concat(itemsFromNames(normalizeNameList(plate.healthy_fat)));
  const hydration = block.hydration_note || plate.hydration || "Water / unsweetened drink";
  optionalItems.push(
    { name: addOnEnergyCopy(block), quantity: 1 },
    { name: hydrationName(hydration), quantity: 1 }
  );

  return groups
    .concat({ label: "Optional add-on", items: uniqueMealItems(optionalItems) })
    .map((group) => ({ ...group, items: uniqueMealItems(group.items).filter((item) => item.name) }))
    .filter((group) => group.items.length);
}

function flattenMenuItems(menuSections) {
  return menuSections.flatMap((section) => (
    Array.isArray(section.items)
      ? section.items.map((item) => (typeof item === "string"
          ? { name: item, quantity: 1 }
          : { ...item, name: item.name, quantity: item.quantity ?? 1 }))
      : []
  )).filter((item) => item.name && Number(item.quantity ?? 1) > 0);
}

function normalizeNameList(value) {
  if (!Array.isArray(value)) return [];
  return value.map((item) => String(item || "").trim()).filter(Boolean);
}

function classifyMealItems(mealItems) {
  const result = { protein: [], carb: [], vegetable: [], optional: [] };
  mealItems.forEach((item) => {
    const category = mealItemCategory(item.name);
    if (category) result[category].push(item);
  });
  return result;
}

function mealItemCategory(name) {
  const lower = String(name || "").toLowerCase();
  const optionalKeywords = ["fruit", "blueberry", "bar", "cookie", "cake", "crisp", "dessert", "milk"];
  const proteinKeywords = ["bean", "edamame", "chicken", "tofu", "lentil", "egg", "fish", "salmon", "tuna", "turkey", "beef", "pork", "tempeh", "seitan", "garbanzo", "chickpea", "beyond burger", "burger"];
  const vegetableKeywords = ["kale", "mushroom", "green", "dandelion", "vegetable", "salad", "lettuce", "broccoli", "spinach", "avocado", "tomato", "pepper", "cauliflower", "carrot", "squash"];
  const carbKeywords = ["quinoa", "rice", "grain", "wrap", "bread", "pasta", "potato", "couscous", "oat", "noodle", "tortilla"];

  if (optionalKeywords.some((keyword) => lower.includes(keyword))) return "optional";
  if (proteinKeywords.some((keyword) => lower.includes(keyword))) return "protein";
  if (carbKeywords.some((keyword) => lower.includes(keyword))) return "carb";
  if (vegetableKeywords.some((keyword) => lower.includes(keyword))) return "vegetable";
  return "";
}

function fillMissingCompositionGroups(groups, plate, optionalItems = []) {
  const fallbackByLabel = {
    Protein: itemsFromNames(normalizeNameList(plate.healthy_protein)),
    "Whole grain / carb": itemsFromNames(normalizeNameList(plate.whole_grains_or_quality_carbs)),
    Vegetables: itemsFromNames(normalizeNameList(plate.vegetables_and_fruits))
  };
  const used = new Set(groups.concat({ items: optionalItems }).flatMap((group) => group.items).map((item) => item.name.toLowerCase()));

  groups.forEach((group) => {
    if (group.items.length) return;
    group.items = (fallbackByLabel[group.label] || []).filter((item) => {
      const category = mealItemCategory(item.name);
      if (category === "optional") return false;
      if (category && category !== compositionCategoryForLabel(group.label)) return false;
      const key = item.name.toLowerCase();
      if (used.has(key)) return false;
      used.add(key);
      return true;
    });
  });
}

function compositionCategoryForLabel(label) {
  if (label === "Protein") return "protein";
  if (label === "Whole grain / carb") return "carb";
  if (label === "Vegetables") return "vegetable";
  return "";
}

function addOnEnergyCopy(block) {
  const calories = Number((block.estimated_nutrition || block.nutrition || {}).calories || 0);
  if (calories && calories < 600) return "Fruit or milk if you need more energy later";
  return "Fruit or extra greens if you need more energy later";
}

function itemsFromNames(names) {
  return names.map((name) => ({ name, quantity: 1 }));
}

function uniqueMealItems(items) {
  const seen = new Set();
  return items.filter((item) => {
    const normalized = String(item?.name || "").trim();
    const key = normalized.toLowerCase();
    if (!normalized || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function formatFoodName(name) {
  return String(name || "")
    .replace(/\s+w\/\s+/gi, " with ")
    .replace(/\s*&\s*/g, " and ")
    .replace(/,\s*and\s*/gi, " · ")
    .replace(/,\s*/g, " · ")
    .replace(/\s+\/\s+/g, " / ")
    .replace(/\s{2,}/g, " ")
    .trim();
}

function hydrationName(value) {
  return String(value || "Water / unsweetened drink")
    .replace(/^choose\s+/i, "")
    .replace(/\ban?\s+unsweetened/i, "unsweetened")
    .replace(/\s+or\s+/i, " / ")
    .replace(/[.。]+$/g, "")
    .trim();
}

function portionLabel(item) {
  const quantity = item.quantity ?? 1;
  return `×${formatQuantity(quantity)}`;
}

function healthScoreLabel(block) {
  const score = Number(block.scores?.health);
  if (!score) return adequacyLabel(block.adequacy_status);
  return `${Math.round(score * 100)} / 100`;
}

function energyFitLabel(block, nutrition) {
  const energy = Number(block.scores?.energy);
  const calories = Number(nutrition.calories || 0);
  if (energy >= 0.9 || calories >= 650) return "High";
  if (energy >= 0.7 || calories >= 400) return "Medium";
  return "Light";
}

function proteinFitLabel(value) {
  const grams = Number(value || 0);
  if (grams >= 30) return "Excellent";
  if (grams >= 20) return "Good";
  if (grams > 0) return "Low";
  return "";
}

function fiberFitLabel(value) {
  const grams = Number(value || 0);
  if (grams >= 8) return "Excellent";
  if (grams >= 5) return "Good";
  if (grams > 0) return "Low";
  return "";
}

function addedSugarFitLabel(value) {
  const grams = Number(value || 0);
  if (grams <= 2) return "Excellent";
  if (grams <= 8) return "Moderate";
  return "High";
}

function sodiumFitLabel(value) {
  const mg = Number(value || 0);
  if (mg <= 500) return "Excellent";
  if (mg <= 900) return "Moderate";
  return "High";
}

function carbonBadgeLabel(block) {
  return `${carbonRatingLabel(Number(block.carbon?.estimated_co2e_kg || 0))} CO2`;
}

function carbonRatingLabel(value) {
  if (value === 0) return "Zero";
  if (value <= 0.8) return "Low";
  if (value <= 2.2) return "Moderate-low";
  if (value <= 3.5) return "Moderate";
  return "High";
}

function climateComparisonCopy(value) {
  if (value <= 0.8) {
    return {
      better: "Better than meat-heavy meals",
      higher: "Close to fully plant-based meals"
    };
  }
  return {
    better: "Better than beef-heavy meals",
    higher: "Higher than fully plant-based meals"
  };
}

function mealCalendarBadge(block) {
  if (block.type !== "meal" || block.adequacy_status !== "complete_meal") return "";
  return `<span class="balanced-mini-pill">Balanced</span>`;
}

function adequacyLabel(status) {
  const labels = {
    complete_meal: "Complete meal",
    incomplete_meal: "Incomplete meal",
    snack: "Snack"
  };
  return labels[status] || "";
}

function formatWarning(value) {
  return String(value || "")
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function menuItemDetail(item) {
  const details = [];
  if (item.quantity !== undefined) details.push(`x${formatQuantity(item.quantity)}`);
  if (item.calories) details.push(`${formatQuantity(item.calories)} kcal`);
  if (item.protein_g) details.push(`${formatQuantity(item.protein_g)}g protein`);
  return escapeHtml(details.join(" | "));
}

function clearSelection() {
  selectedBlock = null;
  workspace.classList.remove("drawer-open");
  detailDrawer.hidden = true;
  drawerContent.hidden = true;
  drawerEmpty.hidden = false;
  drawerEmpty.innerHTML = "";
  menuSection.hidden = true;
  menuSections.innerHTML = "";
  nutritionSection.hidden = true;
  nutritionDetails.innerHTML = "";
  mealStatus.hidden = true;
  mealStatus.innerHTML = "";
  whySection.hidden = true;
  whyDetails.textContent = "";
  activitySection.hidden = true;
  activityDetails.innerHTML = "";
  transportSection.hidden = true;
  transportDetails.innerHTML = "";
  choicesSection.hidden = true;
  diningChoices.innerHTML = "";
  climateDetails.innerHTML = "";
  document.querySelectorAll(".calendar-block").forEach((button) => button.classList.remove("selected"));
}

async function runPlanner() {
  clearSelection();
  renderCalendar([]);
  renderTrace(0);

  const planPromise = requestPlan(promptInput.value).catch((error) => ({
    ...fallbackPlanResponse,
    summary: `Backend planner unavailable, showing local fallback. ${error.message}`,
    metadata: {
      ...fallbackPlanResponse.metadata,
      fallback_reason: error.message || "Backend unavailable."
    }
  }));

  for (let index = 0; index < plannerSteps.length; index += 1) {
    renderTrace(index);
    await delay(260);
  }

  const plan = await planPromise;
  renderTrace(plannerSteps.length - 1, true);
  applyPlan(plan);
}

async function requestPlan(prompt) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), plannerRequestTimeoutMs);
  const apiUrl = plannerApiUrl();

  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
      signal: controller.signal
    });

    if (!response.ok) throw new Error(`Planner API returned ${response.status}`);
    return await response.json();
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(`Planner API timed out after ${Math.round(plannerRequestTimeoutMs / 1000)} seconds.`);
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

async function saveMemorySuggestion() {
  pendingMemoryPatch = memoryPatch.textContent.trim();
  if (!pendingMemoryPatch) return;
  saveMemoryBtn.disabled = true;
  try {
    const response = await fetch(`${apiBaseUrl()}/api/memory/update`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ markdown_patch: pendingMemoryPatch })
    });
    if (!response.ok) throw new Error(`Memory API returned ${response.status}`);
    memoryReason.textContent = "Saved to MEMORY.md.";
    memoryPatch.textContent = pendingMemoryPatch;
    pendingMemoryPatch = "";
    window.setTimeout(() => {
      memoryCard.hidden = true;
      saveMemoryBtn.disabled = false;
    }, 900);
  } catch (error) {
    memoryReason.textContent = "Could not save memory because the backend is unavailable.";
    saveMemoryBtn.disabled = false;
  }
}

function ignoreMemorySuggestion() {
  pendingMemoryPatch = "";
  memoryCard.hidden = true;
}

async function openMemoryViewer() {
  memoryViewer.hidden = false;
  openMemoryBtn.setAttribute("aria-expanded", "true");
  memoryViewerContent.innerHTML = `<p class="memory-empty">Loading memory...</p>`;

  try {
    const response = await fetch(`${apiBaseUrl()}/api/memory`);
    if (!response.ok) throw new Error(`Memory API returned ${response.status}`);
    const payload = await response.json();
    renderMemoryViewer(payload.memory || "");
  } catch (error) {
    memoryViewerContent.innerHTML = `<p class="memory-empty">Memory is unavailable while the backend is offline.</p>`;
  }
}

function closeMemoryViewer() {
  memoryViewer.hidden = true;
  openMemoryBtn.setAttribute("aria-expanded", "false");
}

function renderMemoryViewer(markdown) {
  currentMemorySections = parseMemoryMarkdown(markdown);
  const visibleSections = currentMemorySections.filter((section) => section.items.length > 0);
  if (!visibleSections.length) {
    memoryViewerContent.innerHTML = `<p class="memory-empty">No saved preferences yet.</p>`;
    return;
  }

  memoryViewerContent.innerHTML = visibleSections
    .map((section) => `
      <section class="memory-section" data-section-id="${section.id}">
        <h3>${escapeHtml(section.title)}</h3>
        <ul>
          ${section.items.map((item) => `
            <li class="memory-preference" data-item-id="${item.id}">
              <textarea class="memory-preference-input" rows="1" aria-label="Edit preference">${escapeHtml(item.text)}</textarea>
              <button class="memory-delete-button" type="button" aria-label="Delete preference">&times;</button>
            </li>
          `).join("")}
        </ul>
      </section>
    `)
    .join("");

  memoryViewerContent.querySelectorAll(".memory-preference-input").forEach((input) => {
    resizeMemoryInput(input);
    input.addEventListener("input", () => resizeMemoryInput(input));
    input.addEventListener("blur", () => saveEditedMemoryPreference(input));
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        input.blur();
      }
    });
  });

  memoryViewerContent.querySelectorAll(".memory-delete-button").forEach((button) => {
    button.addEventListener("mousedown", (event) => event.preventDefault());
    button.addEventListener("click", () => deleteMemoryPreference(button));
  });
}

function parseMemoryMarkdown(markdown) {
  const sections = [];
  let current = null;
  let sectionIndex = 0;
  let itemIndex = 0;

  String(markdown || "").split(/\r?\n/).forEach((line) => {
    const heading = line.match(/^##\s+(.+)/);
    if (heading) {
      current = { id: `section_${sectionIndex}`, title: heading[1].trim(), items: [] };
      sections.push(current);
      sectionIndex += 1;
      return;
    }

    const bullet = line.match(/^-\s+(.+)/);
    if (bullet && current) {
      current.items.push({ id: `item_${itemIndex}`, text: bullet[1].trim() });
      itemIndex += 1;
    }
  });

  return sections;
}

function serializeMemoryMarkdown(sections) {
  const blocks = ["# MatChalendar MEMORY"];
  sections.forEach((section) => {
    blocks.push("");
    blocks.push(`## ${section.title}`);
    blocks.push("");
    section.items.forEach((item) => {
      const text = item.text.trim();
      if (text) blocks.push(`- ${text}`);
    });
  });
  return `${blocks.join("\n").trim()}\n`;
}

async function saveCurrentMemory() {
  const response = await fetch(`${apiBaseUrl()}/api/memory/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ memory: serializeMemoryMarkdown(currentMemorySections) })
  });
  if (!response.ok) throw new Error(`Memory API returned ${response.status}`);
  const payload = await response.json();
  renderMemoryViewer(payload.memory || "");
}

async function saveEditedMemoryPreference(input) {
  const preference = findMemoryPreference(input);
  if (!preference) return;

  const nextText = input.value.replace(/\s+/g, " ").trim();
  if (!nextText) {
    await deleteMemoryPreference(input);
    return;
  }
  if (nextText === preference.item.text) return;

  preference.item.text = nextText;
  await persistMemoryEdit(input);
}

async function deleteMemoryPreference(source) {
  const preference = findMemoryPreference(source);
  if (!preference) return;

  preference.section.items = preference.section.items.filter((item) => item.id !== preference.item.id);
  await persistMemoryEdit(source);
}

async function persistMemoryEdit(source) {
  const preferenceEl = source.closest(".memory-preference");
  if (preferenceEl) preferenceEl.classList.add("saving");
  try {
    await saveCurrentMemory();
  } catch (error) {
    memoryViewerContent.innerHTML = `<p class="memory-empty">Could not save memory because the backend is unavailable.</p>`;
  }
}

function findMemoryPreference(source) {
  const preferenceEl = source.closest(".memory-preference");
  const sectionEl = source.closest(".memory-section");
  if (!preferenceEl || !sectionEl) return null;

  const section = currentMemorySections.find((item) => item.id === sectionEl.dataset.sectionId);
  const item = section?.items.find((entry) => entry.id === preferenceEl.dataset.itemId);
  return section && item ? { section, item } : null;
}

function resizeMemoryInput(input) {
  input.style.height = "auto";
  input.style.height = `${input.scrollHeight}px`;
}

function apiBaseUrl() {
  return plannerApiUrl().replace(/\/api\/plan$/, "");
}

function plannerApiUrl() {
  if (window.MATCHALENDAR_API_URL) return window.MATCHALENDAR_API_URL;
  if (window.location.protocol === "http:" || window.location.protocol === "https:") {
    return `${window.location.origin}/api/plan`;
  }
  return "http://127.0.0.1:8000/api/plan";
}

function minutesFromStart(iso) {
  const date = new Date(iso);
  return ((date.getHours() - startHour) * 60 + date.getMinutes()) * (hourHeight / 60);
}

function durationMinutes(start, end) {
  return (new Date(end) - new Date(start)) / 60000;
}

function formatHour(hour) {
  if (hour === 12) return "12 PM";
  if (hour > 12) return `${hour - 12} PM`;
  return `${hour} AM`;
}

function timeRange(start, end) {
  return `${formatTime(start)} - ${formatTime(end)}`;
}

function compactTimeRange(start, end) {
  const startDate = new Date(start);
  const endDate = new Date(end);
  const startSuffix = startDate.getHours() >= 12 ? "PM" : "AM";
  const endSuffix = endDate.getHours() >= 12 ? "PM" : "AM";
  const startLabel = formatCompactTime(startDate, startSuffix !== endSuffix);
  const endLabel = formatCompactTime(endDate, true);
  return `${startLabel}-${endLabel}`;
}

function formatCompactTime(date, includeSuffix) {
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const hour = hours % 12 || 12;
  const suffix = hours >= 12 ? "PM" : "AM";
  const minuteLabel = minutes === 0 ? "" : `:${String(minutes).padStart(2, "0")}`;
  return `${hour}${minuteLabel}${includeSuffix ? suffix : ""}`;
}

function formatTime(iso) {
  const date = new Date(iso);
  const hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const suffix = hours >= 12 ? "PM" : "AM";
  const hour = hours % 12 || 12;
  return `${hour}:${minutes} ${suffix}`;
}

function calendarBlockTitle(block) {
  if (block.type === "meal" && block.location) return block.location;
  return block.title;
}

function dayFromIso(iso) {
  return new Date(iso).toLocaleDateString("en-US", { weekday: "short" });
}

function formatLabel(value) {
  return String(value).replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatKg(value) {
  return Number.isInteger(value) ? String(value) : value.toFixed(1);
}

function formatQuantity(value) {
  const quantity = Number(value);
  return Number.isInteger(quantity) ? String(quantity) : quantity.toFixed(1);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

function carbonLevel(block) {
  return carbonFootprintLevel(block.carbon?.estimated_co2e_kg);
}

function carbonFootprintLevel(value) {
  const footprint = Number(value || 0);
  if (footprint <= 0) return "zero";
  if (footprint <= 0.3) return "low";
  if (footprint <= 0.8) return "moderate";
  return "high";
}

function carbonFootprintLabel(block) {
  const footprint = Number(block.carbon?.estimated_co2e_kg || 0);
  return `${formatKg(footprint)} kg`;
}

function carbonBudgetLevel(current, target) {
  const currentKg = Number(current || 0);
  const targetKg = Number(target || 0);
  if (currentKg <= 0) return "zero";
  if (targetKg <= 0) return "high";

  const usageRatio = currentKg / targetKg;
  if (usageRatio <= 0.5) return "low";
  if (usageRatio <= 0.75) return "moderate";
  return "high";
}

function delay(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  runPlanner();
});

regenerateBtn.addEventListener("click", runPlanner);
closeDrawer.addEventListener("click", clearSelection);
saveMemoryBtn.addEventListener("click", saveMemorySuggestion);
ignoreMemoryBtn.addEventListener("click", ignoreMemorySuggestion);
openMemoryBtn.addEventListener("click", () => {
  if (memoryViewer.hidden) {
    openMemoryViewer();
  } else {
    closeMemoryViewer();
  }
});
closeMemoryBtn.addEventListener("click", closeMemoryViewer);

renderCalendar([]);
renderCarbonBudget(initialCarbonBudget);
renderPlannerMetadata(fallbackPlanResponse);
clearSelection();
