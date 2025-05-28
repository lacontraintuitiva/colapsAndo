document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('projectForm');
    const prevBtn = document.getElementById('prevStep');
    const nextBtn = document.getElementById('nextStep');
    const submitBtn = document.getElementById('submitBtn');
    const steps = document.querySelectorAll('.form-step');
    
    // DEBUG: Verificar que todo existe
    console.log('🔍 Form:', form);
    console.log('🔍 Steps found:', steps.length);
    console.log('🔍 PrevBtn:', prevBtn);
    console.log('🔍 NextBtn:', nextBtn);
    
    let currentStep = 0;
    let autosaveTimeout = null;

    function showStep(step) {
        steps.forEach((div, idx) => {
            div.classList.toggle('d-none', idx !== step);
        });
        document.getElementById('current-step').textContent = step + 1;
        document.getElementById('total-steps').textContent = steps.length;
        
        // OCULTAR/MOSTRAR botones manteniendo su espacio
        if (step === 0) {
            prevBtn.style.visibility = 'hidden'; // Ocultar pero mantener espacio
        } else {
            prevBtn.style.visibility = 'visible'; // Mostrar
            prevBtn.disabled = false; // Asegurar que esté habilitado
        }
        
        if (step === steps.length - 1) {
            nextBtn.style.visibility = 'hidden'; // Ocultar pero mantener espacio
        } else {
            nextBtn.style.visibility = 'visible'; // Mostrar
        }
        
        // Mostrar botón submit solo en la última sección
        submitBtn && (submitBtn.style.display = (step === steps.length - 1) ? 'inline-block' : 'none');
    }

    function updateProgressBar() {
        const requiredFields = form.querySelectorAll('[required]');
        let filled = 0;
        
        requiredFields.forEach(field => {
            if (field.type === 'file') {
                // Para archivos: verificar si hay archivos seleccionados O guardados previamente
                const hasNewFiles = field.files && field.files.length > 0;
                const hasSavedFiles = field.getAttribute('data-has-files') === 'true';
                
                if (hasNewFiles || hasSavedFiles) {
                    filled++;
                }
            } else if (field.type === 'checkbox') {
                if (field.checked) {
                    filled++;
                }
            } else if (field.type === 'radio') {
                if (form.querySelector(`[name="${field.name}"]:checked`)) {
                    filled++;
                }
            } else {
                if (field.value.trim()) {
                    filled++;
                }
            }
        });
        
        const percent = requiredFields.length ? Math.round((filled / requiredFields.length) * 100) : 100;
        const bar = document.getElementById('formProgress');
        
        // Cambiar color según el porcentaje
        if (percent === 100) {
            bar.className = 'progress-bar bg-success';
        } else {
            bar.className = 'progress-bar bg-info';
        }
        
        bar.style.width = percent + '%';
        bar.setAttribute('aria-valuenow', percent);
        bar.textContent = percent + '%';
    }

    function validateField(field) {
        // Validación visual opcional - no bloquea navegación
        if (field.required && !field.value.trim()) {
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    }

    function autosaveForm() {
        const formData = new FormData(form);
        formData.append('current_step', currentStep);
        
        fetch('/project/autosave', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('✅ Guardado automático exitoso');
            } else {
                console.error('❌ Error en guardado:', data.error);
            }
        })
        .catch(error => {
            console.error('❌ Error de red:', error);
        });
    }

    showStep(currentStep);
    updateProgressBar();

    nextBtn.addEventListener('click', function() {
        if (currentStep < steps.length - 1) {
            currentStep++;
            showStep(currentStep);
        }
    });

    prevBtn.addEventListener('click', function() {
        if (currentStep > 0) {
            currentStep--;
            showStep(currentStep);
        }
    });

    // EVENTO CLAVE para detectar cambios y guardar
    form.addEventListener('input', function(e) {
        console.log('📝 Campo modificado:', e.target.name, '=', e.target.value);
        validateField(e.target);
        updateProgressBar();
        clearTimeout(autosaveTimeout);
        autosaveTimeout = setTimeout(autosaveForm, 500);
    });

    // También escuchar cambios en radio buttons y checkboxes
    form.addEventListener('change', function(e) {
        console.log('✅ Campo cambiado:', e.target.name, '=', e.target.value);
        validateField(e.target);
        updateProgressBar();
        clearTimeout(autosaveTimeout);
        autosaveTimeout = setTimeout(autosaveForm, 500);
    });
});