const plannerSteps = [
  "Understanding goal",
  "Checking schedule",
  "Estimating Uber impact",
  "Analyzing dining",
  "Balancing health/energy/carbon",
  "Running ASUS GX10",
  "Replanning calendar"
];

const skillLabels = {
  calendar: "Calendar",
  transportation: "Transportation",
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

const demoPlan = {
  summary: "A calm UCLA week balanced around class, homework, recovery, and lower-carbon choices after today's emergency Uber.",
  plan_blocks: [
    {
      id: "class_mon",
      day: "Mon",
      title: "Class block",
      type: "class",
      start: "2026-04-27T10:00:00",
      end: "2026-04-27T14:00:00",
      location: "UCLA campus",
      reason: "This is the fixed academic anchor. MatChalendar protects it before placing meals, movement, and study time around it.",
      impact: "Locks the day around a known constraint and prevents accidental overlap.",
      scores: { time: 0.98, health: 0.66, energy: 0.7, sustainability: 0.72, carbon: 0.84 },
      carbon: { estimated_co2e_kg: 0.1, delta_co2e_kg: 0 },
      skills_used: ["calendar"]
    },
    {
      id: "walk_mon",
      day: "Mon",
      title: "Recovery walk",
      type: "recovery",
      start: "2026-04-27T14:15:00",
      end: "2026-04-27T14:45:00",
      location: "Bruin Walk",
      reason: "A short walk after four hours of class gives a low-effort reset and avoids adding more transportation emissions after the emergency Uber.",
      impact: "Restores energy without increasing the week's carbon load.",
      scores: { time: 0.88, health: 0.84, energy: 0.8, sustainability: 0.9, carbon: 0.96 },
      carbon: { estimated_co2e_kg: 0, delta_co2e_kg: -0.4 },
      skills_used: ["calendar", "transportation", "energy", "health", "carbon"]
    },
    {
      id: "dinner_mon",
      day: "Mon",
      title: "Low-carbon dinner",
      type: "meal",
      start: "2026-04-27T18:30:00",
      end: "2026-04-27T19:15:00",
      location: "Bruin Plate",
      reason: "The emergency Uber raised today's transportation impact, so dinner shifts toward a plant-forward option while preserving protein and evening energy.",
      impact: "Keeps the carbon goal visible without turning dinner into a punishment.",
      scores: { time: 0.86, health: 0.9, energy: 0.82, sustainability: 0.94, carbon: 0.92 },
      carbon: { estimated_co2e_kg: 0.7, delta_co2e_kg: -1.1 },
      skills_used: ["dining", "carbon", "health", "energy", "calendar"]
    },
    {
      id: "study_mon",
      day: "Mon",
      title: "Homework deep work",
      type: "study",
      start: "2026-04-27T19:45:00",
      end: "2026-04-27T21:15:00",
      location: "Powell Library",
      reason: "Homework stays tonight, but starts after dinner and a transition buffer so the plan does not stack heavy work immediately after class.",
      impact: "Protects assignment progress while keeping the evening realistic.",
      scores: { time: 0.89, health: 0.72, energy: 0.78, sustainability: 0.8, carbon: 0.88 },
      carbon: { estimated_co2e_kg: 0.05, delta_co2e_kg: -0.15 },
      skills_used: ["study", "calendar", "energy", "explanation"]
    },
    {
      id: "winddown_mon",
      day: "Mon",
      title: "Sleep wind-down",
      type: "rest",
      start: "2026-04-27T22:30:00",
      end: "2026-04-27T23:00:00",
      location: "Dorm",
      reason: "A short wind-down block protects recovery after a day with class, emergency travel, and homework.",
      impact: "Reduces overload and preserves tomorrow's energy.",
      scores: { time: 0.82, health: 0.88, energy: 0.86, sustainability: 0.74, carbon: 0.9 },
      carbon: { estimated_co2e_kg: 0, delta_co2e_kg: 0 },
      skills_used: ["health", "energy", "calendar"]
    },
    {
      id: "transit_tue",
      day: "Tue",
      title: "Transit-first commute",
      type: "recovery",
      start: "2026-04-28T09:20:00",
      end: "2026-04-28T09:50:00",
      location: "Big Blue Bus",
      reason: "Tomorrow's route uses transit where the schedule allows, compensating for today's ride-share without creating a rushed morning.",
      impact: "Shifts the week back toward the carbon target.",
      scores: { time: 0.78, health: 0.7, energy: 0.74, sustainability: 0.91, carbon: 0.93 },
      carbon: { estimated_co2e_kg: 0.3, delta_co2e_kg: -0.9 },
      skills_used: ["transportation", "carbon", "calendar"]
    },
    {
      id: "lunch_tue",
      day: "Tue",
      title: "Plant-forward lunch",
      type: "meal",
      start: "2026-04-28T12:00:00",
      end: "2026-04-28T12:45:00",
      location: "De Neve",
      reason: "A lighter lunch keeps afternoon energy steady while continuing the lower-carbon dining pattern.",
      impact: "Supports energy and keeps food emissions below the default dining baseline.",
      scores: { time: 0.84, health: 0.88, energy: 0.85, sustainability: 0.92, carbon: 0.9 },
      carbon: { estimated_co2e_kg: 0.6, delta_co2e_kg: -0.9 },
      skills_used: ["dining", "health", "energy", "carbon"]
    },
    {
      id: "review_wed",
      day: "Wed",
      title: "Review sprint",
      type: "study",
      start: "2026-04-29T15:00:00",
      end: "2026-04-29T16:15:00",
      location: "Study commons",
      reason: "A midweek review prevents Monday night from becoming the only academic catch-up slot.",
      impact: "Spreads workload across the week.",
      scores: { time: 0.84, health: 0.7, energy: 0.79, sustainability: 0.76, carbon: 0.86 },
      carbon: { estimated_co2e_kg: 0.05, delta_co2e_kg: 0 },
      skills_used: ["study", "calendar", "energy"]
    },
    {
      id: "workout_thu",
      day: "Thu",
      title: "Light workout",
      type: "recovery",
      start: "2026-04-30T16:00:00",
      end: "2026-04-30T17:00:00",
      location: "John Wooden Center",
      reason: "A light workout lands in a low-conflict window and supports energy without making the week feel overpacked.",
      impact: "Adds movement while preserving recovery.",
      scores: { time: 0.8, health: 0.92, energy: 0.75, sustainability: 0.78, carbon: 0.88 },
      carbon: { estimated_co2e_kg: 0.02, delta_co2e_kg: 0 },
      skills_used: ["health", "energy", "calendar"]
    }
  ]
};

const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const startHour = 8;
const endHour = 24;
const headerHeight = 32;
const hourHeight = 36;

const form = document.querySelector("#plannerForm");
const trace = document.querySelector("#compactTrace");
const calendarGrid = document.querySelector("#calendarGrid");
const planSummary = document.querySelector("#planSummary");
const regenerateBtn = document.querySelector("#regenerateBtn");
const drawerEmpty = document.querySelector("#drawerEmpty");
const drawerContent = document.querySelector("#drawerContent");
const closeDrawer = document.querySelector("#closeDrawer");

let selectedBlock = null;
let currentBlocks = [];

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
  currentBlocks = blocks;
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

    blocks
      .filter((block) => block.day === day)
      .forEach((block) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `calendar-block block-${block.type}`;
        button.dataset.blockId = block.id;
        button.style.top = `${headerHeight + minutesFromStart(block.start)}px`;
        button.style.height = `${Math.max(38, durationMinutes(block.start, block.end) * (hourHeight / 60))}px`;
        button.innerHTML = `<strong>${block.title}</strong><small>${timeRange(block.start, block.end)} · ${block.location}</small>`;
        button.addEventListener("click", () => selectBlock(block.id));
        column.appendChild(button);
      });

    calendarGrid.appendChild(column);
  });

  if (blocks.length === 0) {
    const empty = document.createElement("div");
    empty.className = "calendar-empty";
    empty.textContent = "Calendar will populate after Run Planner.";
    calendarGrid.appendChild(empty);
  }
}

function selectBlock(blockId) {
  const block = currentBlocks.find((item) => item.id === blockId);
  if (!block) return;
  selectedBlock = block;

  document.querySelectorAll(".calendar-block").forEach((button) => {
    button.classList.toggle("selected", button.dataset.blockId === blockId);
  });

  drawerEmpty.hidden = true;
  drawerContent.hidden = false;

  document.querySelector("#blockType").textContent = block.type;
  document.querySelector("#blockTitle").textContent = block.title;
  document.querySelector("#blockMeta").textContent = `${block.day} · ${timeRange(block.start, block.end)} · ${block.location}`;
  document.querySelector("#blockReason").textContent = block.reason;
  document.querySelector("#blockImpact").textContent = block.impact;
  document.querySelector("#carbonEstimate").textContent = `${block.carbon.estimated_co2e_kg} kg CO2e`;

  const delta = block.carbon.delta_co2e_kg;
  const deltaEl = document.querySelector("#carbonDelta");
  deltaEl.textContent = `${delta > 0 ? "+" : ""}${delta} kg CO2e`;
  deltaEl.className = delta < 0 ? "delta-good" : delta > 0 ? "delta-warn" : "";

  document.querySelector("#scoreStack").innerHTML = Object.entries(block.scores)
    .map(([key, value]) => scoreRow(key, value))
    .join("");

  document.querySelector("#drawerSkills").innerHTML = block.skills_used
    .map((skill) => `<span class="skill-chip">${skillLabels[skill] || skill}</span>`)
    .join("");
}

function scoreRow(key, value) {
  const score = Math.round(value * 100);
  return `
    <div class="score-row">
      <span>${scoreLabels[key] || key}</span>
      <div class="score-bar"><span style="width: ${score}%"></span></div>
      <strong>${score}</strong>
    </div>
  `;
}

function clearSelection() {
  selectedBlock = null;
  drawerContent.hidden = true;
  drawerEmpty.hidden = false;
  document.querySelectorAll(".calendar-block").forEach((button) => button.classList.remove("selected"));
}

function runPlanner() {
  clearSelection();
  renderCalendar([]);
  planSummary.textContent = "Planning in progress...";
  renderTrace(0);

  plannerSteps.forEach((_, index) => {
    window.setTimeout(() => {
      renderTrace(index);

      if (index === plannerSteps.length - 1) {
        window.setTimeout(() => {
          renderTrace(index, true);
          renderCalendar(demoPlan.plan_blocks);
          planSummary.textContent = demoPlan.summary;
          clearSelection();
        }, 420);
      }
    }, index * 360);
  });
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

function formatTime(iso) {
  const date = new Date(iso);
  const hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, "0");
  const suffix = hours >= 12 ? "PM" : "AM";
  const hour = hours % 12 || 12;
  return `${hour}:${minutes} ${suffix}`;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  runPlanner();
});

regenerateBtn.addEventListener("click", runPlanner);
closeDrawer.addEventListener("click", clearSelection);

renderCalendar([]);
clearSelection();
