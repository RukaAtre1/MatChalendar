const plannerSteps = [
  "Understanding goal",
  "Parsing intent",
  "Routing skills",
  "Running internal skills",
  "Replanning calendar",
  "Building explanations",
  "Rendering PlanResponse"
];

const fallbackPlanResponse = {
  summary: "A low-carbon campus week that turns everyday student routines into climate actions.",
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

const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const startHour = 8;
const endHour = 24;
const headerHeight = 32;
const hourHeight = 36;

const form = document.querySelector("#plannerForm");
const trace = document.querySelector("#compactTrace");
const workspace = document.querySelector(".workspace");
const calendarGrid = document.querySelector("#calendarGrid");
const planSummary = document.querySelector("#planSummary");
const regenerateBtn = document.querySelector("#regenerateBtn");
const detailDrawer = document.querySelector(".detail-drawer");
const drawerEmpty = document.querySelector("#drawerEmpty");
const drawerContent = document.querySelector("#drawerContent");
const closeDrawer = document.querySelector("#closeDrawer");
const promptInput = document.querySelector("#promptInput");
const menuSection = document.querySelector("#menuSection");
const menuSections = document.querySelector("#menuSections");
const choicesSection = document.querySelector("#choicesSection");
const diningChoices = document.querySelector("#diningChoices");
const plannerBadge = document.querySelector("#plannerBadge");
const plannerMeta = document.querySelector("#plannerMeta");
const memoryCard = document.querySelector("#memoryCard");
const memoryReason = document.querySelector("#memoryReason");
const memoryPatch = document.querySelector("#memoryPatch");
const saveMemoryBtn = document.querySelector("#saveMemoryBtn");
const ignoreMemoryBtn = document.querySelector("#ignoreMemoryBtn");

let selectedBlock = null;
let currentBlocks = [];
let pendingMemoryPatch = "";

function renderTrace(activeIndex = -1, complete = false) {
  trace.hidden = false;
  trace.innerHTML = plannerSteps
    .map((step, index) => {
      const state = complete || index < activeIndex ? "done" : index === activeIndex ? "active" : "";
      return `<li class="${state}">${step}</li>`;
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
  planSummary.textContent = plan.summary || "PlanResponse generated.";
  clearSelection();
}

function renderPlannerMetadata(plan) {
  const metadata = plan.metadata || {};
  const mode = metadata.planner_mode || plan.generated_by || "unknown";
  const integrations = metadata.integrations_used || [];
  plannerBadge.innerHTML = `<span class="status-dot"></span>${plannerModeLabel(mode)}`;
  plannerMeta.textContent = [
    `Generated by ${formatLabel(metadata.generated_by || plan.generated_by || "unknown")}`,
    `Mode: ${formatLabel(mode)}`,
    integrations.length ? `Integrations: ${integrations.map(formatLabel).join(", ")}` : "",
    metadata.fallback_reason ? `Fallback: ${metadata.fallback_reason}` : "",
    metadata.soul_used ? "SOUL.md used" : "",
    metadata.memory_used ? "MEMORY.md used" : ""
  ].filter(Boolean).join(" | ");
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
}

function renderCarbonBudget(budget) {
  if (!budget) return;
  const current = budget.current_estimated_kg_co2e;
  const target = budget.weekly_target_kg_co2e;
  const percent = Math.min(100, Math.round((current / target) * 100));

  document.querySelector("#carbonCurrent").textContent = current.toFixed(1);
  document.querySelector("#carbonTarget").textContent = `/ ${formatKg(target)} kg CO2e`;
  document.querySelector("#carbonPercent").textContent = `${percent}%`;
  document.querySelector("#carbonMeter").style.width = `${percent}%`;
  document.querySelector("#carbonStatus").textContent = carbonStatusText(budget);
}

function carbonStatusText(budget) {
  const status = formatLabel(budget.status);
  const strategy = formatLabel(budget.adjustment_strategy);
  return `${status}. Strategy: ${strategy}.`;
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
  document.querySelector("#blockTitle").textContent = block.title;
  document.querySelector("#blockMeta").textContent = `${block.day} | ${timeRange(block.start, block.end)} | ${block.location}`;
  document.querySelector("#carbonEstimate").textContent = `${formatKg(block.carbon?.estimated_co2e_kg || 0)} kg CO2e`;
  renderMenu(block);
  renderDiningChoices(block);
}

function renderMenu(block) {
  const sections = Array.isArray(block.menu_sections) ? block.menu_sections : [];
  const shouldShowMenu = block.type === "meal" && sections.length > 0;

  menuSection.hidden = !shouldShowMenu;
  menuSections.innerHTML = shouldShowMenu
    ? sections
        .map((section) => `
          <article class="menu-station">
            <h3>${escapeHtml(section.station)}</h3>
            <ul>
              ${(section.items || []).map(menuItemMarkup).join("")}
            </ul>
          </article>
        `)
        .join("")
    : "";
}

function renderDiningChoices(block) {
  const choices = Array.isArray(block.dining_choices)
    ? block.dining_choices.filter((choice) => choice.dining_hall !== block.location)
    : [];
  const shouldShowChoices = block.type === "meal" && choices.length > 0;

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
  return `
    <details class="dining-choice" ${index === 0 ? "open" : ""}>
      <summary>
        <span class="choice-name">${escapeHtml(choice.dining_hall)}</span>
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
      <strong>x${formatQuantity(normalizedItem.quantity)}</strong>
    </li>
  `;
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
  choicesSection.hidden = true;
  diningChoices.innerHTML = "";
  document.querySelectorAll(".calendar-block").forEach((button) => button.classList.remove("selected"));
}

async function runPlanner() {
  clearSelection();
  renderCalendar([]);
  planSummary.textContent = "Planning in progress...";
  renderTrace(0);

  const planPromise = requestPlan(promptInput.value).catch(() => fallbackPlanResponse);

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
  const timeout = window.setTimeout(() => controller.abort(), 1800);
  const apiUrl = window.MATCHALENDAR_API_URL || "http://127.0.0.1:8000/api/plan";

  try {
    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
      signal: controller.signal
    });

    if (!response.ok) throw new Error(`Planner API returned ${response.status}`);
    return await response.json();
  } finally {
    window.clearTimeout(timeout);
  }
}

async function saveMemorySuggestion() {
  if (!pendingMemoryPatch) return;
  const apiBase = (window.MATCHALENDAR_API_URL || "http://127.0.0.1:8000/api/plan").replace(/\/api\/plan$/, "");
  saveMemoryBtn.disabled = true;
  try {
    const response = await fetch(`${apiBase}/api/memory/update`, {
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
  const footprint = Number(block.carbon?.estimated_co2e_kg || 0);
  if (footprint === 0) return "zero";
  if (footprint <= 0.3) return "low";
  if (footprint <= 0.8) return "moderate";
  return "high";
}

function carbonFootprintLabel(block) {
  const footprint = Number(block.carbon?.estimated_co2e_kg || 0);
  return `${formatKg(footprint)} kg`;
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

renderCalendar([]);
renderCarbonBudget(fallbackPlanResponse.carbon_budget);
renderPlannerMetadata(fallbackPlanResponse);
clearSelection();
