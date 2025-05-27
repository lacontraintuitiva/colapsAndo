document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('projectForm');
  if (!form) return;

  form.addEventListener('submit', function(e) {
    // Busca todos los campos requeridos visibles en el paso actual
    const currentStep = document.querySelector('.form-step:not(.d-none)');
    const requiredFields = currentStep.querySelectorAll('[required]');
    let missing = [];

    requiredFields.forEach(field => {
      let isEmpty = false;
      if (field.type === 'checkbox' && !field.checked) {
        isEmpty = true;
      } else if (field.type === 'radio') {
        // Solo valida el primer radio de cada grupo
        if (!currentStep.querySelector(`[name="${field.name}"]:checked`)) {
          isEmpty = true;
        }
      } else if (!field.value.trim()) {
        isEmpty = true;
      }
      if (isEmpty) {
        let label = field.placeholder || field.getAttribute('aria-label') || field.name;
        // Evita duplicados para radios
        if (!missing.includes(label)) missing.push(label);
        // Resalta el campo faltante
        field.classList.add('is-invalid');
      } else {
        field.classList.remove('is-invalid');
      }
    });

    if (missing.length > 0) {
      e.preventDefault();
      alert(
        "Por favor completa los siguientes campos obligatorios:\n\n" +
        missing.map(f => `• ${f.replace(' *','')}`).join('\n')
      );
    }
  });

  // Elimina la clase is-invalid al escribir
  form.querySelectorAll('input, textarea, select').forEach(field => {
    field.addEventListener('input', function() {
      field.classList.remove('is-invalid');
    });
  });
});