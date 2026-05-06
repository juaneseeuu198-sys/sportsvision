// ============================================
//  SportsVision — Main JavaScript
// ============================================

// ---- SIDEBAR — abre con hover en el borde izquierdo ----
(function initSidebar() {
  const sidebar = document.getElementById('svSidebar');
  if (!sidebar) return;

  // Umbral de píxeles desde el borde izquierdo para abrir
  const TRIGGER_PX = 60;
  let closeTimer = null;

  function openSidebar() {
    clearTimeout(closeTimer);
    sidebar.classList.add('open');
  }

  function closeSidebar() {
    closeTimer = setTimeout(function() {
      sidebar.classList.remove('open');
    }, 200); // pequeño delay para que no cierre bruscamente
  }

  // Abre cuando el mouse está cerca del borde izquierdo de la ventana
  document.addEventListener('mousemove', function(e) {
    if (e.clientX <= TRIGGER_PX) {
      openSidebar();
    }
  });

  // Mantiene abierto mientras el mouse está dentro de la sidebar
  sidebar.addEventListener('mouseenter', openSidebar);
  sidebar.addEventListener('mouseleave', closeSidebar);

  // Botón de menú en móvil — muestra overlay
  var btnMobile = document.getElementById('btnToggleMobile');
  var overlay   = document.getElementById('sidebarOverlay');
  if (btnMobile) {
    btnMobile.addEventListener('click', function() {
      var isOpen = sidebar.classList.toggle('open');
      if (overlay) overlay.style.display = isOpen ? 'block' : 'none';
    });
  }

  // En móvil, cerrar al hacer clic en un enlace de la sidebar
  if (window.innerWidth < 768) {
    sidebar.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', function() {
        sidebar.classList.remove('open');
        if (overlay) overlay.style.display = 'none';
      });
    });
  }
})();

function toggleSidebar() {
  var sidebar = document.getElementById('svSidebar');
  if (sidebar) sidebar.classList.toggle('open');
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
