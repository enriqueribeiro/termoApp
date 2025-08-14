// Input animation and validation
document.addEventListener('DOMContentLoaded', () => {
  // Add animation to form elements
  animateFormElements();
  
  // Add input focus effects
  setupInputEffects();
  
  // Setup add form button functionality
  setupAddFormButton();
});

// ===== VALIDATION SYSTEM =====

// Validation rules and error messages
const VALIDATION_RULES = {
  nome: {
    required: true,
    minLength: 2,
    maxLength: 100,
    pattern: /^[a-zA-ZÀ-ÿ\s]+$/,
    messages: {
      required: "Nome é obrigatório",
      minLength: "Nome deve ter pelo menos 2 caracteres",
      maxLength: "Nome deve ter no máximo 100 caracteres",
      pattern: "Nome deve conter apenas letras e espaços"
    }
  },
  telefone: {
    required: true,
    pattern: /^[\d\s\(\)\-\+]+$/,
    validatePhone: true,
    messages: {
      required: "Telefone é obrigatório",
      pattern: "Telefone deve conter apenas números, espaços, parênteses e hífens"
    }
  },
  funcao: {
    required: true,
    minLength: 3,
    maxLength: 100,
    messages: {
      required: "Função é obrigatória",
      minLength: "Função deve ter pelo menos 3 caracteres",
      maxLength: "Função deve ter no máximo 100 caracteres"
    }
  },
  departamento: {
    required: true,
    messages: {
      required: "Departamento é obrigatório"
    }
  },
  empresa: {
    required: true,
    messages: {
      required: "Empresa é obrigatória"
    }
  },
  outrosFuncao: {
    required: false, // Only required when funcao is 'outros'
    minLength: 3,
    maxLength: 100,
    messages: {
      required: "Especifique a função",
      minLength: "Função deve ter pelo menos 3 caracteres",
      maxLength: "Função deve ter no máximo 100 caracteres"
    }
  },
  patrimonio: {
    required: true,
    pattern: /^[A-Z]{2,}\d+$/i,  // At least 2 letters followed by numbers
    messages: {
      required: "Patrimônio é obrigatório",
      pattern: "Formato inválido. Deve ter pelo menos 2 letras seguidas de números. Ex: CEL001, PC123, FON456"
    }
  },
  observacao: {
    required: false,
    maxLength: 100,
    messages: {
      maxLength: "Observação deve ter no máximo 500 caracteres"
    }
  }
};

// Error display system
class ErrorDisplay {
  constructor() {
    this.errorContainer = null;
    this.createErrorContainer();
  }

  createErrorContainer() {
    // Create global error container
    this.errorContainer = document.createElement('div');
    this.errorContainer.className = 'error-container';
    this.errorContainer.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      max-width: 400px;
      z-index: 10000;
      display: none;
    `;
    document.body.appendChild(this.errorContainer);
  }

  showError(message, fieldName = null) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
      background: #ef4444;
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      margin-bottom: 8px;
      box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
      animation: slideInRight 0.3s ease;
      font-size: 14px;
      line-height: 1.4;
    `;
    
    if (fieldName) {
      errorDiv.innerHTML = `<strong>${fieldName}:</strong> ${message}`;
    } else {
      errorDiv.innerHTML = message;
    }

    this.errorContainer.appendChild(errorDiv);
    this.errorContainer.style.display = 'block';

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (errorDiv.parentNode) {
        errorDiv.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
          if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
            if (this.errorContainer.children.length === 0) {
              this.errorContainer.style.display = 'none';
            }
          }
        }, 300);
      }
    }, 5000);
  }

  showFieldError(field, message) {
    // Remove existing error for this field
    this.removeFieldError(field);
    
    // Add error class to field
    field.classList.add('invalid');
    field.classList.remove('valid');
    
    // Create error message element
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error-message';
    errorDiv.style.cssText = `
      color: #ef4444;
      font-size: 12px;
      margin-top: 4px;
      margin-bottom: 8px;
      animation: fadeIn 0.3s ease;
    `;
    errorDiv.textContent = message;
    
    // Insert after the field
    const wrapper = field.closest('.input-wrapper') || field.parentElement;
    wrapper.appendChild(errorDiv);
    
    // Add shake animation
    field.classList.add('shake');
    setTimeout(() => {
      field.classList.remove('shake');
    }, 600);
  }

  removeFieldError(field) {
    // Remove error class
    field.classList.remove('invalid');
    
    // Remove existing error message
    const wrapper = field.closest('.input-wrapper') || field.parentElement;
    const existingError = wrapper.querySelector('.field-error-message');
    if (existingError) {
      existingError.remove();
    }
  }

  clearAllErrors() {
    // Remove all field errors
    document.querySelectorAll('.field-error-message').forEach(error => error.remove());
    document.querySelectorAll('.invalid').forEach(field => {
      field.classList.remove('invalid');
    });
  }
}

// Validation functions
class FieldValidator {
  static validateField(field, rules) {
    const value = field.value.trim();
    const fieldName = field.name || field.id;
    
    // Required validation
    if (rules.required && !value) {
      return {
        isValid: false,
        message: rules.messages.required
      };
    }
    
    // Skip other validations if field is empty and not required
    if (!value && !rules.required) {
      return { isValid: true };
    }
    
    // Min length validation
    if (rules.minLength && value.length < rules.minLength) {
      return {
        isValid: false,
        message: rules.messages.minLength
      };
    }
    
    // Max length validation
    if (rules.maxLength && value.length > rules.maxLength) {
      return {
        isValid: false,
        message: rules.messages.maxLength
      };
    }
    
    // Pattern validation
    if (rules.pattern && !rules.pattern.test(value)) {
      return {
        isValid: false,
        message: rules.messages.pattern
      };
    }
    
    // Special phone validation
    if (rules.validatePhone) {
      const digits = value.replace(/\D/g, '');
      if (digits.length < 10) {
        return {
          isValid: false,
          message: "Telefone deve ter pelo menos 10 dígitos"
        };
      }
      if (digits.length > 11) {
        return {
          isValid: false,
          message: "Telefone deve ter no máximo 11 dígitos"
        };
      }
    }
    
    return { isValid: true };
  }

  static validatePhoneNumber(value) {
    const digits = value.replace(/\D/g, '');
    return digits.length >= 10 && digits.length <= 11;
  }

  static validateName(value) {
    return /^[a-zA-ZÀ-ÿ\s]+$/.test(value);
  }
}

// Initialize error display
const errorDisplay = new ErrorDisplay();

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  
  @keyframes slideOutRight {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .field-error-message {
    color: #ef4444;
    font-size: 12px;
    margin-top: 4px;
    margin-bottom: 8px;
    animation: fadeIn 0.3s ease;
  }
  
  input.invalid, textarea.invalid, select.invalid {
    border-color: #ef4444;
    background-color: rgba(239, 68, 68, 0.05);
  }
  
  input.valid, textarea.valid, select.valid {
    border-color: #10b981;
    background-color: rgba(16, 185, 129, 0.05);
  }
`;
document.head.appendChild(style);

// ===== ENHANCED INPUT EFFECTS =====

// Configura os efeitos de input para todos os inputs
function setupInputEffects() {
  const inputs = document.querySelectorAll('input, textarea, select');
  inputs.forEach(input => {
    // Create a wrapper for the input if it doesn't have one
    let wrapper = input.parentElement;
    if (!wrapper.classList.contains('input-wrapper') && !wrapper.classList.contains('row')) {
      // Create a wrapper
      wrapper = document.createElement('div');
      wrapper.className = 'input-wrapper';
      
      // Insert the wrapper before the input
      input.parentNode.insertBefore(wrapper, input);
      
      // Move the input into the wrapper
      wrapper.appendChild(input);
    }
    
    // Create and append the focus effect element
    const focusEffect = document.createElement('div');
    focusEffect.className = 'focus-effect';
    wrapper.appendChild(focusEffect);
    
    // Position the focus effect relative to the input
    positionFocusEffect(input, focusEffect);
    
    // Add focus animation
    input.addEventListener('focus', () => {
      focusEffect.classList.add('active');
      // Clear any existing errors when user starts typing
      errorDisplay.removeFieldError(input);
    });
    
    input.addEventListener('blur', () => {
      focusEffect.classList.remove('active');
      
      // Validate field on blur
      const fieldName = input.name || input.id;
      const rules = VALIDATION_RULES[fieldName];
      
      if (rules) {
        const result = FieldValidator.validateField(input, rules);
        
        if (result.isValid) {
          input.classList.add('valid');
          input.classList.remove('invalid');
          errorDisplay.removeFieldError(input);
        } else {
          input.classList.add('invalid');
          input.classList.remove('valid');
          errorDisplay.showFieldError(input, result.message);
        }
      } else {
        // Simple validation for fields without specific rules
        if (input.value.trim() !== '') {
          input.classList.add('valid');
          input.classList.remove('invalid');
        } else {
          input.classList.remove('valid');
        }
      }
    });
    
    // Add typing animation
    input.addEventListener('input', () => {
      input.classList.add('typing');
      clearTimeout(input.typingTimer);
      input.typingTimer = setTimeout(() => {
        input.classList.remove('typing');
      }, 1000);
      
      // Clear errors as user types
      if (input.classList.contains('invalid')) {
        errorDisplay.removeFieldError(input);
      }
    });
  });
}

// Posiciona o elemento de efeito de foco em relação ao seu input
function positionFocusEffect(input, focusEffect) {
  
  // Add a small delay to ensure the DOM is fully updated
  setTimeout(() => {
    // Ensure the focus effect is properly sized
    if (input.parentElement) {
      focusEffect.style.width = '100%';
    }
  }, 0);
}

// Adiciona animação escalonada aos elementos do formulário
function animateFormElements() {
  const formSections = document.querySelectorAll('.form-section');
  const buttonContainer = document.querySelector('.button-container');
  
  // Reset animations if they've already played
  formSections.forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.animation = 'none';
  });
  
  buttonContainer.style.opacity = '0';
  buttonContainer.style.transform = 'translateY(20px)';
  buttonContainer.style.animation = 'none';
  
  // Force reflow
  void document.body.offsetWidth;
  
  // Play animations again
  formSections.forEach((section, index) => {
    section.style.animation = `fadeInUp 0.8s ${index * 0.2}s forwards`;
  });
  
  buttonContainer.style.animation = `fadeInUp 0.8s ${formSections.length * 0.2}s forwards`;
}

// Add spinner control functions
function showGlobalSpinner() {
  const spinner = document.getElementById('global-spinner-overlay');
  if (spinner) spinner.classList.add('active');
}
function hideGlobalSpinner() {
  const spinner = document.getElementById('global-spinner-overlay');
  if (spinner) spinner.classList.remove('active');
}

// Add showSuccessAndReset at the top level
function showSuccessAndReset() {
  // Remove any old message and overlay
  const oldMsg = document.getElementById('after-download-message');
  if (oldMsg) oldMsg.remove();
  const oldOverlay = document.getElementById('after-download-overlay');
  if (oldOverlay) oldOverlay.remove();

  // Helper to show the after-download overlay and message with fade-in
  function showAfterDownloadOverlayAndMessage() {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'after-download-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.background = 'rgba(0,0,0,0.45)'; // darker overlay
    overlay.style.zIndex = 9998;
    overlay.style.backdropFilter = 'blur(2px)';
    overlay.style.transition = 'opacity 0.4s';
    overlay.style.opacity = '0';
    document.body.appendChild(overlay);
    // Trigger fade-in
    setTimeout(() => {
      overlay.style.opacity = '1';
    }, 10);

    // Create message
    const msg = document.createElement('div');
    msg.id = 'after-download-message';
    msg.style.position = 'fixed';
    msg.style.top = '50%';
    msg.style.left = '50%';
    msg.style.transform = 'translate(-50%, -50%)';
    msg.style.background = '#fff';
    msg.style.padding = '2em';
    msg.style.borderRadius = '1em';
    msg.style.zIndex = 9999;
    msg.style.textAlign = 'center';
    msg.style.opacity = '0';
    msg.style.transition = 'opacity 0.4s';

    msg.innerHTML = `
      <div style="text-align:center;color:#111827">
        <h3>Documento baixado com sucesso!</h3>
        <p style="margin-top:0.5em;color:#6b7280;">A página será recarregada automaticamente...</p>
      </div>
    `;
    document.body.appendChild(msg);
    // Fade in message after overlay is visible
    setTimeout(() => {
      msg.style.opacity = '1';
    }, 200);

    // Auto-reload page after 3 seconds
    setTimeout(() => {
      msg.remove();
      overlay.remove();
      window.location.reload();
    }, 3000);
  }

  // Fade out spinner overlay, then show after-download overlay/message
  const spinnerOverlay = document.getElementById('global-spinner-overlay');
  if (spinnerOverlay && spinnerOverlay.classList.contains('active')) {
    spinnerOverlay.style.transition = 'opacity 0.4s';
    spinnerOverlay.style.opacity = '0';
    setTimeout(() => {
      spinnerOverlay.classList.remove('active');
      spinnerOverlay.style.opacity = '';
      showAfterDownloadOverlayAndMessage();
    }, 400);
  } else {
    showAfterDownloadOverlayAndMessage();
  }
}

// Enhanced form submission with comprehensive validation
function enviar(event) {
  const form = event.target.closest('form');
  let isValid = true;
  const errors = [];

  // Clear all previous errors
  errorDisplay.clearAllErrors();

  // Validate all form fields
  const allInputs = form.querySelectorAll('input, textarea, select');
  
  allInputs.forEach(input => {
    const fieldName = input.name || input.id;
    const rules = VALIDATION_RULES[fieldName];
    
    if (rules) {
      // Special handling for 'outrosFuncao' - only validate if funcao is 'outros'
      if (fieldName === 'outrosFuncao') {
        const funcaoSelect = form.querySelector('select[name="funcao"]');
        if (funcaoSelect && funcaoSelect.value === 'outros') {
          rules.required = true;
        } else {
          rules.required = false;
        }
      }
      
      const result = FieldValidator.validateField(input, rules);
      
      if (!result.isValid) {
        isValid = false;
        errors.push({
          field: fieldName,
          message: result.message
        });
        errorDisplay.showFieldError(input, result.message);
      } else {
        input.classList.add('valid');
        input.classList.remove('invalid');
      }
    }
  });

  // Special validation for assets - at least one required
  const assetInputs = form.querySelectorAll('input[name="patrimonio[]"]');
  const hasValidAsset = Array.from(assetInputs).some(input => input.value.trim() !== '');
  
  if (!hasValidAsset) {
    isValid = false;
    errors.push({
      field: 'patrimonio',
      message: 'Pelo menos um patrimônio é obrigatório'
    });
    
    // Show error on first asset field
    const firstAssetInput = assetInputs[0];
    if (firstAssetInput) {
      errorDisplay.showFieldError(firstAssetInput, 'Pelo menos um patrimônio é obrigatório');
    }
  }

  if (!isValid) {
    // Show summary error message
    errorDisplay.showError(`Formulário contém ${errors.length} erro(s). Corrija os campos destacados.`);
    
    // Scroll to first error
    const firstErrorField = form.querySelector('.invalid');
    if (firstErrorField) {
      firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    return false;
  }

  // If validation passes, proceed with form submission
  const button = event.target;
  button.classList.add('success');
  button.textContent = 'Enviando...';
  button.disabled = true;

  // Show spinner
  const successMessage = document.createElement('div');
  successMessage.className = 'success-message';
  successMessage.innerHTML = `
    <div class="spinner-container">
      <div class="spinner"></div>
    </div>
    <p>Montando seu documento...</p>
  `;
  document.body.appendChild(successMessage);
  successMessage.classList.add('show');

  function hideSpinner() {
    const spinner = document.querySelector('.success-message');
    if (spinner) spinner.remove();
  }

  // Submit the form
  form.submit();
  
  // Reset form after submission
  setTimeout(() => {
    // Reset all fields
    allInputs.forEach(input => {
      input.value = '';
      input.classList.remove('valid', 'invalid');
    });
    
    // Reset all Observação fields (including dynamically created ones)
    document.querySelectorAll('textarea[name="observacao[]"]')
      .forEach(textarea => { textarea.value = ''; });
    
    // Reset the 'Outro' field for função if present
    const outrosFuncao = document.getElementById('outrosFuncao');
    if (outrosFuncao) {
      outrosFuncao.value = '';
    }
    
    // Clear all errors
    errorDisplay.clearAllErrors();
    
    // Reset button
    button.classList.remove('success');
    button.textContent = 'Enviar';
    button.disabled = false;
  }, 1000);
}


// Função para atualizar a largura do formulário com base no número de fieldsets
function updateFormWidth(fieldsRow) {
  const additionalForm = document.getElementById('additional-form');
  const fieldsetCount = fieldsRow.children.length;
  
  // Base width for one fieldset
  const baseWidth = 350;
  
  // Calculate new width based on fieldset count with a reduced space increase
  // Each additional fieldset adds 150px to the width with no maximum limit
  let newWidth = baseWidth + ((fieldsetCount - 1) * 150);
  
  // Update the form width with a smooth transition
  additionalForm.style.transition = 'max-width 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
  additionalForm.style.maxWidth = `${newWidth}px`;
  additionalForm.style.minWidth = `${baseWidth}px`;
}

// Configura a funcionalidade do botão de adicionar formulário
function setupAddFormButton() {
  const addFormBtn = document.getElementById('add-form-btn');
  const formRow = document.querySelector('.form-row');
  
  // Create a function to handle the click event
  const handleAddFormClick = function() {
    // Remove the event listener temporarily to prevent multiple triggers
    addFormBtn.removeEventListener('click', handleAddFormClick);
    
    // Get the additional form
    const additionalForm = document.getElementById('additional-form');
    
    // Create a counter for the new field sets
    if (!additionalForm.dataset.fieldsetCounter) {
      additionalForm.dataset.fieldsetCounter = 1;
    } else {
      additionalForm.dataset.fieldsetCounter = parseInt(additionalForm.dataset.fieldsetCounter) + 1;
    }
    
    // Create a new field container
    const fieldsetId = additionalForm.dataset.fieldsetCounter;
    
    // Check if we already have a fields row container
    let fieldsRow = additionalForm.querySelector('.fields-row');
    
    // If not, create one and move the original fields into it
    if (!fieldsRow) {
      // Create the fields row container
      fieldsRow = document.createElement('div');
      fieldsRow.className = 'fields-row';
      
      // Get the original fields
      const originalPatrimonio = additionalForm.querySelector('input[placeholder="Patrimônio"]');
      const originalObservacao = additionalForm.querySelector('textarea[placeholder="Observação"]');
      
      // Create a container for the original fields
      const originalFieldset = document.createElement('div');
      originalFieldset.className = 'fieldset';
      
      // Only proceed if we found the original fields
      if (originalPatrimonio && originalObservacao) {
        // Clone the original fields to preserve any values and event listeners
        const clonedPatrimonio = originalPatrimonio.cloneNode(true);
        const clonedObservacao = originalObservacao.cloneNode(true);
        
        // Remove the original fields
        originalPatrimonio.parentNode.removeChild(originalPatrimonio);
        originalObservacao.parentNode.removeChild(originalObservacao);
        
        // Add the cloned fields to the original fieldset
        originalFieldset.appendChild(clonedPatrimonio);
        originalFieldset.appendChild(clonedObservacao);
        
        // Add the original fieldset to the fields row
        fieldsRow.appendChild(originalFieldset);
        
        // Insert the fields row before the add button
        additionalForm.insertBefore(fieldsRow, addFormBtn);
        
        // Setup input effects for the cloned fields
        setupInputEffects();
      }
    }
    
    // Create a new fieldset for the new fields
    const newFieldset = document.createElement('div');
    newFieldset.className = 'fieldset';
    newFieldset.id = `fieldset-${fieldsetId}`;
    
    // Set initial styles for animation
    newFieldset.style.opacity = '0';
    newFieldset.style.transform = 'translateX(10px)';
    
    // Add the same fields as the original
    newFieldset.innerHTML = `
      <button type="button" class="remove-fieldset-button" title="Remover campos">
        <span>×</span>
      </button>
      <input type="text" name="patrimonio[]" placeholder="Patrimônio" maxlength="50" />
      <textarea name="observacao[]" placeholder="Observação" maxlength="500"></textarea>
    `;
    
    // Add the new fieldset to the fields row
    fieldsRow.appendChild(newFieldset);
    
    // Adjust the form width based on the number of fieldsets
    updateFormWidth(fieldsRow);
    
    // Add animation
    setTimeout(() => {
      newFieldset.style.animation = 'fadeInRight 0.5s forwards';
    }, 10);
    
    // Setup input effects for the new fields
    setupInputEffects();
    
    // Setup remove button
    const removeBtn = newFieldset.querySelector('.remove-fieldset-button');
    removeBtn.addEventListener('click', () => {
      // Add fade out animation
      newFieldset.style.animation = 'fadeOutRight 0.5s forwards';
      
      // Remove after animation completes
      setTimeout(() => {
        fieldsRow.removeChild(newFieldset);
        
        // If this was the last additional fieldset, restore the original layout
        if (fieldsRow.children.length === 1) {
          const originalFieldset = fieldsRow.querySelector('.fieldset');
          const patrimonio = originalFieldset.querySelector('input[placeholder="Patrimônio"]');
          const observacao = originalFieldset.querySelector('textarea[placeholder="Observação"]');
          
          if (patrimonio && observacao) {
            // Move the fields back to the form
            additionalForm.insertBefore(patrimonio, fieldsRow);
            additionalForm.insertBefore(observacao, fieldsRow);
            
            // Remove the empty fields row
            additionalForm.removeChild(fieldsRow);
            
            // Reset the form width to its original size
            additionalForm.style.transition = 'max-width 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            additionalForm.style.maxWidth = '350px';
            additionalForm.style.minWidth = '350px';
          }
        } else {
          // Update the form width based on the remaining fieldsets
          updateFormWidth(fieldsRow);
        }
      }, 500);
    });
    
    // Re-attach the event listener to the button
    setTimeout(() => {
      addFormBtn.addEventListener('click', handleAddFormClick);
    }, 100);
  };
  
  // Initial event listener setup
  addFormBtn.addEventListener('click', handleAddFormClick);
}

// Adiciona a animação fadeOutDown ao CSS dinamicamente
function addFadeOutAnimation() {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeOutDown {
      from {
        opacity: 1;
        transform: translateY(0);
      }
      to {
        opacity: 0;
        transform: translateY(20px);
      }
    }
    
    .remove-form-button {
      position: absolute;
      top: 10px;
      right: 10px;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      padding: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #ef4444;
      box-shadow: var(--shadow);
      cursor: pointer;
      transition: var(--transition);
    }
    
    .remove-form-button span {
      font-size: 20px;
      line-height: 1;
      color: white;
    }
    
    .remove-form-button:hover {
      transform: scale(1.1);
      background-color: #dc2626;
    }
    
    .form-section {
      position: relative;
    }
  `;
  document.head.appendChild(style);
}

// Chama essa função quando o DOM está carregado
document.addEventListener('DOMContentLoaded', addFadeOutAnimation);

document.querySelector('form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Run client-side validation first
    const form = e.target;
    let isValid = true;
    const errors = [];

    // Clear all previous errors
    errorDisplay.clearAllErrors();

    // Validate all form fields
    const allInputs = form.querySelectorAll('input, textarea, select');
    
    allInputs.forEach(input => {
        const fieldName = input.name || input.id;
        const rules = VALIDATION_RULES[fieldName];
        
        if (rules) {
            // Special handling for 'outrosFuncao' - only validate if funcao is 'outros'
            if (fieldName === 'outrosFuncao') {
                const funcaoSelect = form.querySelector('select[name="funcao"]');
                if (funcaoSelect && funcaoSelect.value === 'outros') {
                    rules.required = true;
                } else {
                    rules.required = false;
                }
            }
            
            const result = FieldValidator.validateField(input, rules);
            
            if (!result.isValid) {
                isValid = false;
                errors.push({
                    field: fieldName,
                    message: result.message
                });
                errorDisplay.showFieldError(input, result.message);
            } else {
                input.classList.add('valid');
                input.classList.remove('invalid');
            }
        }
    });

    // Special validation for assets - at least one required
    const assetInputs = form.querySelectorAll('input[name="patrimonio[]"]');
    const hasValidAsset = Array.from(assetInputs).some(input => input.value.trim() !== '');
    
    if (!hasValidAsset) {
        isValid = false;
        errors.push({
            field: 'patrimonio',
            message: 'Pelo menos um patrimônio é obrigatório'
        });
        
        // Show error on first asset field
        const firstAssetInput = assetInputs[0];
        if (firstAssetInput) {
            errorDisplay.showFieldError(firstAssetInput, 'Pelo menos um patrimônio é obrigatório');
        }
    }

    if (!isValid) {
        // Show summary error message
        errorDisplay.showError(`Formulário contém ${errors.length} erro(s). Corrija os campos destacados.`);
        
        // Scroll to first error
        const firstErrorField = form.querySelector('.invalid');
        if (firstErrorField) {
            firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        
        return false;
    }

    // If client-side validation passes, proceed with server submission
    showGlobalSpinner();

    const loadingDiv = document.getElementById('loading-messages');
    let messageQueue = [];
    let isTransitioning = false;

    function showNextMessage() {
        if (messageQueue.length === 0) {
            isTransitioning = false;
            return;
        }
        isTransitioning = true;
        const nextMsg = messageQueue.shift();
        loadingDiv.classList.remove('visible');
        setTimeout(() => {
            loadingDiv.textContent = nextMsg;
            loadingDiv.classList.add('visible');
            setTimeout(() => {
                loadingDiv.classList.remove('visible');
                setTimeout(() => {
                    loadingDiv.textContent = "";
                    showNextMessage();
                }, 500); // match your CSS transition duration
            }, 1500); // how long the message stays visible
        }, 500); // match your CSS transition duration
    }

    const eventSource = new EventSource('/progress');
    eventSource.onmessage = function(event) {
        if (event.data.trim() === "DONE") {
            eventSource.close();
            return;
        }
        messageQueue.push(event.data);
        if (!isTransitioning) {
            showNextMessage();
        }
    };

    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/', {
            method: 'POST',
            body: formData
        });
        
        const contentType = response.headers.get('Content-Type');

        if (response.ok && contentType === 'application/pdf') {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            const nomeInput = e.target.querySelector('[name="nome"]');
            let nomeUser = nomeInput ? nomeInput.value.trim() : '';

            nomeUser = nomeUser.replace(/[^a-zA-Z0-9_\- ]/g, '').replace(/\s+/g, '_');

            if (!nomeUser) nomeUser = 'usuario';

            a.download = `Termo_de_entrega_${nomeUser}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();

            hideGlobalSpinner();
            showSuccessAndReset();

        } else {
            // Handle server-side validation errors
            let errorMessage = 'Erro desconhecido';
            
            try {
                const errorData = await response.json();
                
                if (errorData.validation_errors) {
                    // Handle validation errors from server
                    errorData.validation_errors.forEach(error => {
                        const field = form.querySelector(`[name="${error.field}"]`);
                        if (field) {
                            errorDisplay.showFieldError(field, error.message);
                        } else {
                            // Show general error if field not found
                            errorDisplay.showError(error.message);
                        }
                    });
                    
                    // Show summary error message
                    errorDisplay.showError(`Formulário contém ${errorData.validation_errors.length} erro(s). Corrija os campos destacados.`);
                    
                    // Scroll to first error
                    const firstErrorField = form.querySelector('.invalid');
                    if (firstErrorField) {
                        firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                } else {
                    errorMessage = errorData.error || 'Erro desconhecido';
                    errorDisplay.showError(`Erro ao gerar documento: ${errorMessage}`);
                }
            } catch (parseError) {
                // If response is not JSON, treat as text error
                try {
                    errorMessage = await response.text();
                } catch (textError) {
                    errorMessage = 'Erro na comunicação com o servidor';
                }
                errorDisplay.showError(`Erro ao gerar documento: ${errorMessage}`);
            }
            
            hideGlobalSpinner();
        }
    } catch (error) {
        console.error('Erro:', error);
        errorDisplay.showError('Erro na conexão com o servidor');
        hideGlobalSpinner();
    }
});
