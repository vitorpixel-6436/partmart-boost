#!/usr/bin/env python3
"""Input Validators

Version: 0.3.5j (package 3.9a, stage 7.7b/7.7)

Package 3.9a Stage 7.7b: Input validation.

Features:
- Type validation
- Range validation
- Format validation
- Collection validation
"""
from typing import Any, Optional, List, Type, Union
import re


class ValidationError(Exception):
    """Validation error exception"""
    pass


class Validator:
    """Input Validator
    
    v0.3.5j (package 3.9a, stage 7.7b/7.7)
    
    Usage:
        >>> Validator.validate_type(42, int)
        >>> Validator.validate_range(5, 0, 10)
        >>> Validator.validate_not_none(value, 'parameter_name')
    """
    
    @staticmethod
    def validate_type(value: Any, expected_type: Union[Type, tuple], param_name: str = 'value') -> None:
        """Validate type
        
        Args:
            value: Value to validate
            expected_type: Expected type or tuple of types
            param_name: Parameter name for error message
        
        Raises:
            ValidationError: If type is invalid
        """
        if not isinstance(value, expected_type):
            if isinstance(expected_type, tuple):
                types_str = ' or '.join(t.__name__ for t in expected_type)
            else:
                types_str = expected_type.__name__
            
            raise ValidationError(
                f"{param_name} must be {types_str}, got {type(value).__name__}"
            )
    
    @staticmethod
    def validate_range(
        value: Union[int, float],
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        param_name: str = 'value'
    ) -> None:
        """Validate numeric range
        
        Args:
            value: Value to validate
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)
            param_name: Parameter name
        
        Raises:
            ValidationError: If out of range
        """
        Validator.validate_type(value, (int, float), param_name)
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{param_name} must be >= {min_value}, got {value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{param_name} must be <= {max_value}, got {value}")
    
    @staticmethod
    def validate_not_none(value: Any, param_name: str = 'value') -> None:
        """Validate not None
        
        Args:
            value: Value to validate
            param_name: Parameter name
        
        Raises:
            ValidationError: If value is None
        """
        if value is None:
            raise ValidationError(f"{param_name} cannot be None")
    
    @staticmethod
    def validate_not_empty(value: Union[str, list, dict], param_name: str = 'value') -> None:
        """Validate not empty
        
        Args:
            value: Value to validate
            param_name: Parameter name
        
        Raises:
            ValidationError: If empty
        """
        Validator.validate_not_none(value, param_name)
        
        if len(value) == 0:
            raise ValidationError(f"{param_name} cannot be empty")
    
    @staticmethod
    def validate_choice(value: Any, choices: List[Any], param_name: str = 'value') -> None:
        """Validate value is in choices
        
        Args:
            value: Value to validate
            choices: Valid choices
            param_name: Parameter name
        
        Raises:
            ValidationError: If not in choices
        """
        if value not in choices:
            raise ValidationError(f"{param_name} must be one of {choices}, got {value}")
    
    @staticmethod
    def validate_string_length(
        value: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        param_name: str = 'value'
    ) -> None:
        """Validate string length
        
        Args:
            value: String to validate
            min_length: Minimum length
            max_length: Maximum length
            param_name: Parameter name
        
        Raises:
            ValidationError: If length invalid
        """
        Validator.validate_type(value, str, param_name)
        
        length = len(value)
        
        if min_length is not None and length < min_length:
            raise ValidationError(
                f"{param_name} length must be >= {min_length}, got {length}"
            )
        
        if max_length is not None and length > max_length:
            raise ValidationError(
                f"{param_name} length must be <= {max_length}, got {length}"
            )
    
    @staticmethod
    def validate_regex(value: str, pattern: str, param_name: str = 'value') -> None:
        """Validate string matches regex
        
        Args:
            value: String to validate
            pattern: Regex pattern
            param_name: Parameter name
        
        Raises:
            ValidationError: If doesn't match
        """
        Validator.validate_type(value, str, param_name)
        
        if not re.match(pattern, value):
            raise ValidationError(f"{param_name} doesn't match pattern {pattern}")
    
    @staticmethod
    def validate_positive(value: Union[int, float], param_name: str = 'value') -> None:
        """Validate positive number
        
        Args:
            value: Value to validate
            param_name: Parameter name
        
        Raises:
            ValidationError: If not positive
        """
        Validator.validate_type(value, (int, float), param_name)
        
        if value <= 0:
            raise ValidationError(f"{param_name} must be positive, got {value}")
    
    @staticmethod
    def validate_percentage(value: Union[int, float], param_name: str = 'value') -> None:
        """Validate percentage (0-100)
        
        Args:
            value: Value to validate
            param_name: Parameter name
        
        Raises:
            ValidationError: If not valid percentage
        """
        Validator.validate_range(value, 0, 100, param_name)
    
    @staticmethod
    def validate_dict_keys(
        value: dict,
        required_keys: List[str],
        param_name: str = 'value'
    ) -> None:
        """Validate dictionary has required keys
        
        Args:
            value: Dictionary to validate
            required_keys: Required keys
            param_name: Parameter name
        
        Raises:
            ValidationError: If keys missing
        """
        Validator.validate_type(value, dict, param_name)
        
        missing = set(required_keys) - set(value.keys())
        
        if missing:
            raise ValidationError(
                f"{param_name} missing required keys: {missing}"
            )
    
    @staticmethod
    def safe_validate(validator_func, *args, **kwargs) -> tuple[bool, Optional[str]]:
        """Safely run validator and return result
        
        Args:
            validator_func: Validator function
            *args: Arguments
            **kwargs: Keyword arguments
        
        Returns:
            (is_valid, error_message)
        """
        try:
            validator_func(*args, **kwargs)
            return True, None
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {e}"


# Testing
if __name__ == '__main__':
    print("="*60)
    print("Validator Test")
    print("="*60)
    print()
    
    # Test type validation
    print("Test 1: Type validation")
    try:
        Validator.validate_type(42, int)
        print("✅ Valid integer")
    except ValidationError as e:
        print(f"❌ {e}")
    
    try:
        Validator.validate_type("hello", int)
        print("❌ Should have failed")
    except ValidationError as e:
        print(f"✅ Caught: {e}")
    
    # Test range validation
    print("\nTest 2: Range validation")
    try:
        Validator.validate_range(5, 0, 10)
        print("✅ Valid range")
    except ValidationError as e:
        print(f"❌ {e}")
    
    try:
        Validator.validate_range(15, 0, 10)
        print("❌ Should have failed")
    except ValidationError as e:
        print(f"✅ Caught: {e}")
    
    # Test not empty
    print("\nTest 3: Not empty")
    try:
        Validator.validate_not_empty("hello")
        print("✅ Not empty")
    except ValidationError as e:
        print(f"❌ {e}")
    
    try:
        Validator.validate_not_empty("")
        print("❌ Should have failed")
    except ValidationError as e:
        print(f"✅ Caught: {e}")
    
    # Test safe validation
    print("\nTest 4: Safe validation")
    is_valid, error = Validator.safe_validate(Validator.validate_range, 5, 0, 10)
    print(f"Valid: {is_valid}, Error: {error}")
    
    is_valid, error = Validator.safe_validate(Validator.validate_range, 15, 0, 10)
    print(f"Valid: {is_valid}, Error: {error}")
    
    print("\n✅ Test completed!")
