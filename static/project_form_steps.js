document.addEventListener('DOMContentLoaded', function() {
  const steps = document.querySelectorAll('.form-step');
  const totalSteps = steps.length;
  let current = 0;

  const currentStepSpan = document.getElementById('current-step');
  const totalStepsSpan = document.getElementById('total-steps');
  const prevBtn = document.getElementById('prevStep');
  const nextBtn = document.getElementById('nextStep');
  // El submitBtn siempre está visible, no se oculta

  if (totalStepsSpan) totalStepsSpan.textContent = totalSteps;

  function showStep(idx) {
    steps.forEach((step, i) => {
      step.classList.toggle('d-none', i !== idx);
    });
    if (currentStepSpan) currentStepSpan.textContent = idx + 1;
    if (prevBtn) prevBtn.disabled = idx === 0;
    if (nextBtn) nextBtn.classList.toggle('d-none', idx === totalSteps - 1);
    // submitBtn siempre visible, no se oculta
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      if (current > 0) {
        current--;
        showStep(current);
      }
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      if (current < totalSteps - 1) {
        current++;
        showStep(current);
      }
    });
  }

  showStep(current);
});