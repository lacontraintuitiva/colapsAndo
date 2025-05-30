console.log('--- project_form_persistence.js SCRIPT INICIADO ---'); // PRIMERA LÍNEA DEL ARCHIVO

document.addEventListener('DOMContentLoaded', () => {
  console.log('--- DOMContentLoaded EVENTO DISPARADO ---'); // PRIMERA LÍNEA DENTRO DEL LISTENER
  
  // CONSTANTES - Asegúrate que estos IDs existen en tu project_form.html
  const form = document.getElementById('projectForm');
  const steps = Array.from(form.querySelectorAll('.form-step'));
  const nextBtn = document.getElementById('nextStep');
  const prevBtn = document.getElementById('prevStep');
  const progressBar = document.getElementById('formProgress');
  const currentStepSpan = document.getElementById('current-step');
  const totalStepsSpan = document.getElementById('total-steps');
  
  // Verificar si los elementos cruciales fueron encontrados
  if (!form) console.error("ERROR: Elemento con id 'projectForm' NO ENCONTRADO.");
  if (!nextBtn) console.error("ERROR: Elemento con id 'nextStep' NO ENCONTRADO.");
  if (!prevBtn) console.error("ERROR: Elemento con id 'prevStep' NO ENCONTRADO.");
  if (!progressBar) console.error("ERROR: Elemento con id 'formProgress' NO ENCONTRADO.");
  if (steps.length === 0) console.warn("ADVERTENCIA: No se encontraron elementos con clase '.form-step'.");

  let currentStep = 0;

  // Inicializa la UI
  totalStepsSpan.textContent = steps.length;
  showStep(0);
  updateProgressBar();

  function showStep(idx) {
    steps.forEach((s,i) => s.classList.toggle('d-none', i !== idx));
    currentStepSpan.textContent = idx + 1;
    prevBtn.disabled = idx === 0;
    nextBtn.disabled = idx === steps.length - 1;
  }

  function updateProgressBar() {
    // Solo cuenta los campos required (excluye file inputs opcionales)
    const fields = Array.from(
      form.querySelectorAll('[required]:not([type="hidden"])')
    );
    const uniqueNames = [...new Set(fields.map(f => f.name))];

    let filled = 0;
    uniqueNames.forEach(name => {
      const els = Array.from(form.querySelectorAll(`[name="${name}"]`));
      const first = els[0];
      switch (first.type) {
        case 'checkbox':
          if (first.checked) filled++;
          break;
        case 'radio':
          if (els.some(r => r.checked)) filled++;
          break;
        default:
          if (first.value.trim()) filled++;
      }
    });

    const pct = uniqueNames.length
      ? Math.round((filled / uniqueNames.length) * 100)
      : 0;

    progressBar.style.width       = pct + '%';
    progressBar.setAttribute('aria-valuenow', pct);
    progressBar.textContent       = pct + '%';
    progressBar.className         = pct === 100
      ? 'progress-bar bg-success'
      : 'progress-bar bg-info';
  }

  function autosave() {
    console.log('--- AUTOSAVE LLAMADO ---'); // NUEVO PRINT
    console.log('Paso actual para autosave:', currentStep); // NUEVO PRINT
    const data = new FormData(form);
    data.append('current_step', currentStep);
    
    // Para depurar qué se envía:
    console.log('Datos FormData para autosave:'); // NUEVO PRINT
    for (let [key, value] of data.entries()) {
      console.log(key, value);
    }

    fetch('/admin/project/autosave', { method: 'POST', body: data })
      .then(response => {
        if (!response.ok) {
          console.error('Error en autosave (respuesta no OK):', response.status, response.statusText);
          return response.json().then(errData => {
            console.error('Detalles del error del servidor (autosave):', errData);
          }).catch(() => {
            console.error('No se pudieron obtener detalles del error del servidor (autosave).');
          });
        } else {
          return response.json();
        }
      })
      .then(result => {
        if (result && result.success) {
          console.log('Autosave exitoso en el servidor:', result); // NUEVO PRINT
        } else if (result && result.error) {
          console.error('Error en autosave (reportado por el servidor con success=false):', result.error);
        }
      })
      .catch(error => {
        console.error('Error en la solicitud de fetch para autosave (red/fetch):', error);
      });
  }

  // ——— Carga inicial del borrador ———
  fetch('/project/load-progress') // Esta es la ruta correcta que definiste en admin.py
    .then(r => {
      if (!r.ok) { 
        console.error("Error en fetch /project/load-progress:", r.status, r.statusText);
        return r.text().then(text => { 
            console.error("Cuerpo del error de /project/load-progress:", text);
            throw new Error(`Error ${r.status} al cargar progreso`);
        });
      }
      return r.json(); 
    })
    .then(json => {
      console.log("JSON recibido de /project/load-progress:", json); 
      if (json && json.success && json.project) { 
        const proj = json.project;
        currentStep = parseInt(proj.current_step) || 0;
        
        Object.entries(proj).forEach(([name, val]) => {
          console.log(`CARGA INICIAL - Campo: ${name}, Valor del backend: ${val}`);
          const els = form.querySelectorAll(`[name="${name}"]`);
          els.forEach(el => {
            if (el.type === 'file') {
              // No modificar el input file
            } else if (el.type === 'radio') {
              el.checked = el.value === String(val);
            } else if (el.type === 'checkbox') {
              el.checked = Boolean(val);
            } else {
              el.value = val !== null && val !== undefined ? String(val) : '';
            }
          });
        });
        console.log("Formulario llenado con datos del backend."); 
      } else {
        console.warn("No se recibieron datos de proyecto válidos de /project/load-progress o json.success no es true.");
        if (json && json.error) {
            console.error("Error reportado por /project/load-progress:", json.error);
        }
      }
      showStep(currentStep);
      updateProgressBar();

      // Manejo de eliminación de archivo cargado
      const removeBtn = document.getElementById('remove-file-btn');
      const fileInfoBlock = document.getElementById('file-info-block');
      const fileInput = document.getElementById('project_files');

      if (removeBtn && fileInfoBlock && fileInput) {
        removeBtn.addEventListener('click', () => {
          // Reemplaza el input file por uno nuevo
          const newInput = fileInput.cloneNode();
          newInput.value = '';
          newInput.disabled = false;
          fileInput.parentNode.replaceChild(newInput, fileInput);

          // Oculta el bloque de info del archivo cargado
          fileInfoBlock.style.display = 'none';

          // Marca en un campo oculto que el archivo debe eliminarse en el backend
          let hidden = document.getElementById('remove_project_files');
          if (!hidden) {
            hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = 'remove_project_files';
            hidden.id = 'remove_project_files';
            hidden.value = '1';
            newInput.parentNode.appendChild(hidden);
          }

          // Opcional: da foco al input para que el usuario pueda seleccionar uno nuevo
          newInput.focus();

          // Llama autosave para guardar el cambio
          autosave();
        });
      }
    })
    .catch(error => { 
        console.error("Error general en la carga inicial del borrador:", error);
    });

  // ——— Navegación multipaso ———
  nextBtn.addEventListener('click', () => {
    if (currentStep < steps.length - 1) {
      currentStep++;
      showStep(currentStep);
      updateProgressBar();
      autosave();
    }
  });
  prevBtn.addEventListener('click', () => {
    if (currentStep > 0) {
      currentStep--;
      showStep(currentStep);
      updateProgressBar();
      autosave();
    }
  }); // Fin del listener de prevBtn

  console.log("Intentando registrar listener 'change' en el formulario..."); // NUEVO PRINT
  // ——— Autosave al cambiar cualquier campo ———
  form.addEventListener('change', () => {
    console.log("Evento 'change' detectado en el formulario."); // NUEVO PRINT
    updateProgressBar();
    autosave();
  });

  // ——— Manejo de archivos seleccionados ———
  const fileInput = document.getElementById('project_files');
  const fileInfoBlock = document.getElementById('file-info-block');

  if (fileInput) {
    fileInput.addEventListener('change', () => {
      // Si hay archivos seleccionados, muestra sus nombres
      if (fileInput.files && fileInput.files.length > 0) {
        let nombres = Array.from(fileInput.files).map(f => f.name).join(', ');
        if (fileInfoBlock) {
          fileInfoBlock.innerHTML = `
            <small class="text-success">
              <i class="fas fa-check-circle me-1"></i>
              <strong>Archivos cargados:</strong> ${nombres}
            </small>
          `;
        }
      } else if (fileInfoBlock) {
        // Si no hay archivos seleccionados, muestra el mensaje por defecto
        fileInfoBlock.innerHTML = `
          <small class="form-text text-muted">
            Seleccione uno o más archivos (imágenes, videos, documentos PDF)
          </small>
        `;
      }
    });
  }
}); // Fin del DOMContentLoaded