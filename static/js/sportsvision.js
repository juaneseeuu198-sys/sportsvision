// ============================================
//  SportsVision — Main JavaScript
// ============================================

// ---- SIDEBAR TOGGLE ----
function toggleSidebar() {
  const sidebar = document.getElementById('svSidebar');
  if (!sidebar) return;
  sidebar.classList.toggle('open');
  sidebar.classList.toggle('collapsed');
}

// ---- RADIO BUTTON STYLING ----
function styleRadioGroup(name) {
  const radios = document.querySelectorAll(`[name="${name}"]`);
  radios.forEach(r => {
    r.addEventListener('change', () => {
      radios.forEach(rb => {
        const label = rb.nextElementSibling;
        if (label) label.classList.remove('active');
      });
      const activeLabel = r.nextElementSibling;
      if (activeLabel) activeLabel.classList.add('active');
    });
    // Init checked state
    if (r.checked) {
      const label = r.nextElementSibling;
      if (label) label.classList.add('active');
    }
  });
}

// ---- EQUIPMENT CHECKBOX STYLING ----
function initEquipCards() {
  document.querySelectorAll('.equip-checkbox').forEach(cb => {
    cb.addEventListener('change', () => {
      cb.closest('.equip-card').classList.toggle('selected', cb.checked);
    });
    if (cb.checked) {
      cb.closest('.equip-card').classList.add('selected');
    }
  });
}

// ---- MUSCLE CHECKBOX STYLING ----
function initMuscleButtons() {
  document.querySelectorAll('.muscle-check').forEach(cb => {
    cb.addEventListener('change', () => {
      const btn = cb.nextElementSibling;
      if (btn) btn.classList.toggle('active', cb.checked);
    });
  });
}

// ---- WORKOUT: TOGGLE ATTRIBUTE FIELD ----
function toggleAttr(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

function removeAttr(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = 'none';
}

function toggleField(id) {
  const el = document.getElementById(id);
  if (el) el.style.display = el.style.display === 'none' ? 'block' : 'none';
}

// ---- AUTO-DISMISS ALERTS ----
function autoDismissAlerts() {
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => {
      a.style.transition = 'opacity 0.5s';
      a.style.opacity = '0';
      setTimeout(() => a.remove(), 500);
    });
  }, 3500);
}

// ---- SPIN ANIMATION ----
document.querySelectorAll('.spin').forEach(el => {
  el.style.animation = 'spin 0.6s linear infinite';
});

// ---- INIT on DOMContentLoaded ----
document.addEventListener('DOMContentLoaded', () => {
  initEquipCards();
  initMuscleButtons();
  autoDismissAlerts();

  // Style all radio groups
  ['genero', 'nivel', 'nivel_actividad', 'objetivo'].forEach(styleRadioGroup);
});
