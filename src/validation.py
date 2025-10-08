"""
Field validation utilities for TermoApp.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationRule:
    """Represents a validation rule with custom error message."""
    validator: callable # pyright: ignore[reportGeneralTypeIssues]
    error_message: str
    field_name: str

@dataclass
class ValidationResult:
    """Represents the result of a validation check."""
    is_valid: bool
    error_message: Optional[str] = None
    field_name: Optional[str] = None

class FieldValidator:
    """Handles field validation with custom error messages."""
    
    # Validation patterns
    PHONE_PATTERN = re.compile(r'^[\d\s\(\)\-\+]+$')
    NAME_PATTERN = re.compile(r'^[a-zA-ZÀ-ÿ\s]+$')
    
    @staticmethod
    def validate_required(value: str, field_name: str) -> ValidationResult:
        """Validate that a field is not empty."""
        if not value or not value.strip():
            field_display_names = {
                'nome': 'Nome',
                'funcao': 'Função',
                'departamento': 'Departamento',
                'telefone': 'Telefone',
                'empresa': 'Empresa',
                'patrimonio': 'Patrimônio',
                'outrosFuncao': 'Função específica'
            }
            display_name = field_display_names.get(field_name, field_name.title())
            return ValidationResult(
                is_valid=False,
                error_message=f"{display_name} é obrigatório",
                field_name=field_name
            )
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_name(value: str, field_name: str) -> ValidationResult:
        """Validate name field format."""
        if not value:
            return ValidationResult(is_valid=True)  # Let required validation handle empty
        
        # Check for minimum length
        if len(value.strip()) < 2:
            return ValidationResult(
                is_valid=False,
                error_message="Nome deve ter pelo menos 2 caracteres",
                field_name=field_name
            )
        
        # Check for maximum length
        if len(value.strip()) > 100:
            return ValidationResult(
                is_valid=False,
                error_message="Nome deve ter no máximo 100 caracteres",
                field_name=field_name
            )
        
        # Check for valid characters (letters, spaces, and accented characters)
        if not FieldValidator.NAME_PATTERN.match(value.strip()):
            return ValidationResult(
                is_valid=False,
                error_message="Nome deve conter apenas letras e espaços",
                field_name=field_name
            )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_phone(value: str, field_name: str) -> ValidationResult:
        """Validate phone number format."""
        if not value:
            return ValidationResult(is_valid=True)  # Let required validation handle empty
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', value)
        
        # Check if it's a valid Brazilian phone number (10 or 11 digits)
        if len(digits) < 10:
            return ValidationResult(
                is_valid=False,
                error_message="Telefone deve ter pelo menos 10 dígitos",
                field_name=field_name
            )
        
        if len(digits) > 11:
            return ValidationResult(
                is_valid=False,
                error_message="Telefone deve ter no máximo 11 dígitos",
                field_name=field_name
            )
        
        # Check if it's a valid Brazilian phone number (10 or 11 digits)
        if len(digits) < 10:
            return ValidationResult(
                is_valid=False,
                error_message="Telefone deve ter pelo menos 10 dígitos",
                field_name=field_name
            )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_function(value: str, field_name: str) -> ValidationResult:
        """Validate function field."""
        if not value:
            return ValidationResult(is_valid=True)  # Let required validation handle empty
        
        # Check for minimum length
        if len(value.strip()) < 3:
            return ValidationResult(
                is_valid=False,
                error_message="Função deve ter pelo menos 3 caracteres",
                field_name=field_name
            )
        
        # Check for maximum length
        if len(value.strip()) > 100:
            return ValidationResult(
                is_valid=False,
                error_message="Função deve ter no máximo 100 caracteres",
                field_name=field_name
            )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_asset(value: str, field_name: str) -> ValidationResult:
        """Validate asset/patrimonio field with specific format patterns."""
        if not value:
            return ValidationResult(is_valid=True)  # Let required validation handle empty
        
        patrimonio_limpo = value.strip().upper()
        
        # Define valid patrimônio patterns - must have at least 2 letters before numbers
        valid_patterns = [
            r'^CEL\d+$',      # CELxxx (CEL + números)
            r'^PC\d+$',       # PCxxx (PC + números)
            r'^FON\d+$',      # FONxxx (FON + números)
            r'^MO\d+$',       # MOxxx (MO + números)
            r'^NOT\d+$',      # NOTxxx (NOT + números)
            r'^IMP\d+$',      # IMPxxx (IMP + números)
            r'^FRAG\d+$',     # FRAGxxx (FRAG + números)
            r'^CAD\d+$'       # CADxxx (CAD + números)
        ]
        
        # Additional validation: must have at least 2 letters before numbers
        if not re.match(r'^[A-Z]{2,}\d+$', patrimonio_limpo):
            return ValidationResult(
                is_valid=False,
                error_message="Patrimônio deve ter pelo menos 2 letras seguidas de números",
                field_name=field_name
            )
        
        # Check if patrimonio matches any valid pattern
        for pattern in valid_patterns:
            if re.match(pattern, patrimonio_limpo):
                return ValidationResult(is_valid=True)
        
        # If no pattern matches, return error with valid examples
        valid_examples = "CEL001, PC123, FON456, MO789, NOT101, IMP202, FRAG303, CAD404"
        return ValidationResult(
            is_valid=False,
            error_message=f"Formato inválido. Use um destes formatos: {valid_examples}",
            field_name=field_name
        )
    
    @staticmethod
    def validate_observation(value: str, field_name: str) -> ValidationResult:
        """Validate observation field (optional)."""
        if not value:
            return ValidationResult(is_valid=True)  # Optional field
        
        # Check for maximum length
        if len(value.strip()) > 500:
            return ValidationResult(
                is_valid=False,
                error_message="Observação deve ter no máximo 500 caracteres",
                field_name=field_name
            )
        
        return ValidationResult(is_valid=True)
    
    @staticmethod
    def validate_select_field(value: str, field_name: str) -> ValidationResult:
        """Validate select fields (departamento, empresa, funcao)."""
        if not value or value == "":
            field_display_names = {
                'departamento': 'Departamento',
                'empresa': 'Empresa',
                'funcao': 'Função'
            }
            display_name = field_display_names.get(field_name, field_name.title())
            return ValidationResult(
                is_valid=False,
                error_message=f"{display_name} é obrigatório",
                field_name=field_name
            )
        
        return ValidationResult(is_valid=True)

class FormValidator:
    """Main form validator that orchestrates all field validations."""
    
    def __init__(self):
        self.validator = FieldValidator()
    
    def validate_form_data(self, form_data: Dict[str, str]) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Validate all form data and return validation results.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate required fields
        required_fields = ['nome', 'funcao', 'departamento', 'telefone', 'empresa']
        for field in required_fields:
            result = self.validator.validate_required(form_data.get(field, ''), field)
            if not result.is_valid:
                errors.append({
                    'field': result.field_name,
                    'message': result.error_message
                })
        
        # Validate specific field formats
        if form_data.get('nome'):
            result = self.validator.validate_name(form_data['nome'], 'nome')
            if not result.is_valid:
                errors.append({
                    'field': result.field_name,
                    'message': result.error_message
                })
        
        if form_data.get('telefone'):
            result = self.validator.validate_phone(form_data['telefone'], 'telefone')
            if not result.is_valid:
                errors.append({
                    'field': result.field_name,
                    'message': result.error_message
                })
        
        if form_data.get('funcao'):
            result = self.validator.validate_function(form_data['funcao'], 'funcao')
            if not result.is_valid:
                errors.append({
                    'field': result.field_name,
                    'message': result.error_message
                })
        
        # Validate 'outrosFuncao' if funcao is 'outros'
        if form_data.get('funcao') == 'outros':
            result = self.validator.validate_required(form_data.get('outrosFuncao', ''), 'outrosFuncao')
            if not result.is_valid:
                errors.append({
                    'field': result.field_name,
                    'message': result.error_message
                })
            elif form_data.get('outrosFuncao'):
                result = self.validator.validate_function(form_data['outrosFuncao'], 'outrosFuncao')
                if not result.is_valid:
                    errors.append({
                        'field': result.field_name,
                        'message': result.error_message
                    })
        
        # Validate assets
        assets = form_data.getlist('patrimonio[]') if hasattr(form_data, 'getlist') else form_data.get('patrimonio[]', []) # pyright: ignore[reportAttributeAccessIssue]
        if not assets or not any(asset.strip() for asset in assets):
            errors.append({
                'field': 'patrimonio',
                'message': 'Pelo menos um patrimônio é obrigatório'
            })
        else:
            for i, asset in enumerate(assets):
                if asset.strip():
                    result = self.validator.validate_asset(asset, f'patrimonio_{i}')
                    if not result.is_valid:
                        errors.append({
                            'field': f'patrimonio_{i}',
                            'message': result.error_message
                        })
        
        # Validate observations (optional)
        observations = form_data.getlist('observacao[]') if hasattr(form_data, 'getlist') else form_data.get('observacao[]', []) # pyright: ignore[reportAttributeAccessIssue]
        for i, observation in enumerate(observations):
            if observation.strip():
                result = self.validator.validate_observation(observation, f'observacao_{i}')
                if not result.is_valid:
                    errors.append({
                        'field': f'observacao_{i}',
                        'message': result.error_message
                    })
        
        return len(errors) == 0, errors 