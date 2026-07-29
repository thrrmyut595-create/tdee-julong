// ==========================================================
// script.js — จัดการการทำงานฝั่งหน้าเว็บทั้งหมด
// ==========================================================

// ตอนพัฒนาในเครื่อง (เปิดผ่าน http://localhost:5000) ใช้ path แบบ relative ได้เลย
// ตอน deploy จริง frontend จะอยู่บน Firebase Hosting คนละโดเมนกับ backend (Render)
// จึงต้องระบุ URL เต็มของ backend ตรงนี้ -> แก้ตรงนี้เป็นลิงก์ Render ของคุณหลัง deploy เสร็จ
const RENDER_BACKEND_URL = "https://YOUR-APP-NAME.onrender.com"; // <-- แก้ตรงนี้!

const isLocal = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const API_BASE = isLocal ? "/api" : `${RENDER_BACKEND_URL}/api`;
const RING_CIRCUMFERENCE = 427.3; // 2 * PI * 68

let currentGoal = 0; // เป้าหมาย TDEE ล่าสุด

// ---------- Utility: fetch แบบมี error handling ----------
async function apiFetch(path, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `เกิดข้อผิดพลาด (${res.status})`);
    }
    return res.json();
  } catch (err) {
    console.error(err);
    alert(`เชื่อมต่อเซิร์ฟเวอร์ไม่สำเร็จ: ${err.message}\n(ตรวจสอบว่ารัน backend python app.py อยู่หรือไม่)`);
    return null;
  }
}

// ---------- Tabs ----------
const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanels = document.querySelectorAll(".tab-panel");

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    tabButtons.forEach((b) => b.classList.remove("active"));
    tabPanels.forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(`tab-${btn.dataset.tab}`).classList.add("active");
  });
});

// ---------- Ring progress ----------
function updateRing(totalCalories) {
  const ring = document.getElementById("ringProgress");
  const percent = currentGoal > 0 ? Math.min(totalCalories / currentGoal, 1) : 0;
  const offset = RING_CIRCUMFERENCE * (1 - percent);
  ring.style.strokeDashoffset = offset;

  document.getElementById("totalCaloriesText").textContent = Math.round(totalCalories);
  document.getElementById("goalText").textContent =
    currentGoal > 0 ? `${Math.round(currentGoal)} kcal` : "ยังไม่ได้คำนวณ";
  document.getElementById("remainText").textContent =
    currentGoal > 0 ? `${Math.round(currentGoal - totalCalories)} kcal` : "—";
}

// ---------- BMR / TDEE form ----------
const bmrForm = document.getElementById("bmrForm");
bmrForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(bmrForm);
  const payload = Object.fromEntries(formData.entries());

  const result = await apiFetch("/calculate-bmr", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!result) return;

  document.getElementById("bmrValue").textContent = result.bmr;
  document.getElementById("tdeeValue").textContent = result.tdee;
  document.getElementById("bmrResult").hidden = false;

  currentGoal = result.tdee;
  refreshLogs();
});

async function loadLatestProfile() {
  const profile = await apiFetch("/user-profile/latest");
  if (profile) {
    currentGoal = profile.tdee;
  }
}

// ---------- คลังอาหาร (foods) ----------
async function loadFoods() {
  const foods = await apiFetch("/foods");
  if (!foods) return;

  // เติมตัวเลือกใน select ของแท็บบันทึกอาหาร
  const select = document.getElementById("foodSelect");
  select.innerHTML = '<option value="">— เลือกอาหาร (หรือกรอกเองด้านล่าง) —</option>';
  foods.forEach((f) => {
    const opt = document.createElement("option");
    opt.value = f.id;
    opt.textContent = `${f.name} (${f.calories_per_100g} kcal/100g)`;
    opt.dataset.name = f.name;
    opt.dataset.calories = f.calories_per_100g;
    select.appendChild(opt);
  });

  // เติมตารางในแท็บคลังอาหาร
  const tbody = document.getElementById("foodTableBody");
  tbody.innerHTML = "";
  foods.forEach((f) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeHtml(f.name)}</td>
      <td>${f.calories_per_100g}</td>
      <td>${f.protein_g}</td>
      <td>${f.fat_g}</td>
      <td>${f.carb_g}</td>
    `;
    tbody.appendChild(tr);
  });
}

document.getElementById("foodSelect").addEventListener("change", (e) => {
  const opt = e.target.selectedOptions[0];
  if (opt && opt.value) {
    document.getElementById("foodNameInput").value = opt.dataset.name;
    document.getElementById("caloriesPer100Input").value = opt.dataset.calories;
  }
});

const foodForm = document.getElementById("foodForm");
foodForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(foodForm);
  const payload = Object.fromEntries(formData.entries());

  const result = await apiFetch("/foods", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!result) return;

  foodForm.reset();
  loadFoods();
});

// ---------- บันทึกอาหารที่กิน (food logs) ----------
const logForm = document.getElementById("logForm");
const logDateInput = document.getElementById("logDateInput");

logDateInput.value = new Date().toISOString().slice(0, 10);
logDateInput.addEventListener("change", refreshLogs);

logForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const foodSelect = document.getElementById("foodSelect");
  const selectedOption = foodSelect.selectedOptions[0];

  const payload = {
    food_id: selectedOption && selectedOption.value ? Number(selectedOption.value) : null,
    food_name: document.getElementById("foodNameInput").value,
    calories_per_100g: Number(document.getElementById("caloriesPer100Input").value),
    amount_g: Number(document.getElementById("amountInput").value),
    log_date: logDateInput.value,
  };

  const result = await apiFetch("/food-logs", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!result) return;

  logForm.reset();
  document.getElementById("amountInput").value = 100;
  refreshLogs();
});

async function refreshLogs() {
  const data = await apiFetch(`/food-logs?date=${logDateInput.value}`);
  if (!data) return;

  const listEl = document.getElementById("logList");
  listEl.innerHTML = "";

  if (data.logs.length === 0) {
    listEl.innerHTML = '<p class="log-empty">ยังไม่มีรายการอาหารในวันนี้</p>';
  } else {
    data.logs.forEach((log) => {
      const item = document.createElement("div");
      item.className = "log-item";
      item.innerHTML = `
        <div>
          <div>${escapeHtml(log.food_name)}</div>
          <div class="log-meta">${log.amount_g} กรัม · ${Math.round(log.calories)} kcal</div>
        </div>
        <button data-id="${log.id}">ลบ</button>
      `;
      item.querySelector("button").addEventListener("click", () => deleteLog(log.id));
      listEl.appendChild(item);
    });
  }

  updateRing(data.total_calories);
}

async function deleteLog(id) {
  const result = await apiFetch(`/food-logs/${id}`, { method: "DELETE" });
  if (result) refreshLogs();
}

// ---------- Helper ----------
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---------- เริ่มต้นโหลดข้อมูล ----------
(async function init() {
  await loadLatestProfile();
  await loadFoods();
  await refreshLogs();
})();
