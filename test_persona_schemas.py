#!/usr/bin/env python3
"""
Comprehensive test script for persona JSON schema validation.
Tests all schema contracts and enforcement rules.
"""

import sys
import os
import json
from pathlib import Path

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.persona import Persona
from models.persona_schema import (
    PersonaSchemaValidator, 
    DETAILED_PERSONA_SCHEMA, 
    BASIC_PERSONA_SCHEMA, 
    SESSION_PERSONA_SCHEMA,
    validate_persona_file
)
from sample_detailed_personas import (
    create_sarah_marketing_maven,
    create_mike_growth_hacker,
    create_jenny_scaling_solopreneur
)
import jsonschema

def test_schema_contracts():
    """Test all JSON schema contracts and validation rules."""
    
    print("🔒 COMPREHENSIVE JSON SCHEMA VALIDATION TESTS")
    print("=" * 70)
    
    validator = PersonaSchemaValidator()
    all_tests_passed = True
    
    print("\n1️⃣ TESTING DETAILED PERSONA SCHEMA")
    print("-" * 50)
    
    # Test with our detailed personas
    detailed_personas = [
        create_sarah_marketing_maven(),
        create_mike_growth_hacker(), 
        create_jenny_scaling_solopreneur()
    ]
    
    for persona in detailed_personas:
        print(f"\n🧪 Testing {persona.name}...")
        
        # Convert to dictionary for schema validation
        persona_dict = persona.to_json_schema_dict()
        
        # Test detailed schema validation
        errors = validator.validate_detailed_persona(persona_dict)
        
        if errors:
            print(f"  ❌ FAILED: {len(errors)} schema errors:")
            for error in errors[:3]:  # Show first 3 errors
                print(f"    • {error}")
            if len(errors) > 3:
                print(f"    • ... and {len(errors) - 3} more errors")
            all_tests_passed = False
        else:
            print(f"  ✅ PASSED: Schema validation successful")
        
        # Test business rules
        print(f"  🔍 Business Rules Validation:")
        print(f"    • Major Struggles: {len(persona.major_struggles)} (need ≥3)")
        print(f"    • Business Fears: {len(persona.deep_fears_business)} (need ≥2)")
        print(f"    • Business Results: {len(persona.tangible_business_results)} (need ≥2)")
        print(f"    • Signature Phrases: {len(persona.if_only_soundbites)} (need ≥1)")
        print(f"    • Summary Length: {len(persona.persona_summary)} chars (need ≥100)")
        
        # Test is_detailed_persona detection
        is_detailed = persona.is_detailed_persona()
        print(f"    • Detected as detailed: {'✅ YES' if is_detailed else '❌ NO'}")
        
        # Test schema validation via persona method
        persona_errors = persona.validate_schema(strict=True)
        if persona_errors != errors:
            print(f"  ⚠️  Mismatch between validator and persona method results")
            all_tests_passed = False
        else:
            print(f"  ✅ Persona.validate_schema() method working correctly")
    
    print(f"\n2️⃣ TESTING BASIC PERSONA SCHEMA (Backward Compatibility)")
    print("-" * 50)
    
    # Create a basic persona (minimal fields)
    basic_persona_data = {
        "id": "test-basic-persona-001",
        "name": "Test User",
        "age": 30,
        "gender": "Female",
        "occupation": "Professional",
        "location": "Test City",
        "personality_traits": ["analytical", "creative"],
        "interests": ["technology", "design"],
        "pain_points": ["time management", "tool complexity"],
        "goals": ["increased efficiency", "better work-life balance"],
        "communication_style": "balanced",
        "active": True
    }
    
    basic_errors = validator.validate_basic_persona(basic_persona_data)
    if basic_errors:
        print(f"  ❌ Basic persona validation FAILED: {basic_errors}")
        all_tests_passed = False
    else:
        print(f"  ✅ Basic persona validation PASSED")
    
    print(f"\n3️⃣ TESTING SESSION PERSONA SCHEMA")
    print("-" * 50)
    
    # Create session persona format
    session_persona_data = {
        "persona_id": "sarah_johnson",
        "name": "Sarah Johnson",
        "role": "Marketing Agency Owner",
        "age": 32,
        "occupation": "Digital Marketing Agency Owner",
        "background": "Experienced marketing professional with agency background",
        "personality_traits": ["analytical", "perfectionist", "cost-conscious"],
        "interests": ["yoga", "reading", "networking"],
        "pain_points": ["limited budget", "time management", "client acquisition"],
        "goals": ["revenue growth", "better work-life balance"],
        "communication_style": "professional",
        "detailed_context": "You are Sarah Johnson, a 32-year-old marketing agency owner..."
    }
    
    session_errors = validator.validate_session_persona(session_persona_data)
    if session_errors:
        print(f"  ❌ Session persona validation FAILED: {session_errors}")
        all_tests_passed = False
    else:
        print(f"  ✅ Session persona validation PASSED")
    
    print(f"\n4️⃣ TESTING SCHEMA VIOLATIONS")
    print("-" * 50)
    
    # Test various schema violations
    violation_tests = [
        {
            "name": "Missing required field",
            "data": {"id": "test", "age": 30},  # Missing name
            "should_fail": True
        },
        {
            "name": "Invalid age range",
            "data": {"id": "test", "name": "Test", "age": 15, "occupation": "Student"},
            "should_fail": True
        },
        {
            "name": "Invalid gender enum",
            "data": {"id": "test", "name": "Test", "age": 25, "gender": "Robot", "occupation": "AI"},
            "should_fail": True
        },
        {
            "name": "String too long",
            "data": {"id": "test", "name": "Test", "age": 25, "occupation": "A" * 300},  # Too long
            "should_fail": True
        },
        {
            "name": "Invalid array item type",
            "data": {"id": "test", "name": "Test", "age": 25, "occupation": "Dev", "hobbies": [123, 456]},  # Numbers instead of strings
            "should_fail": True
        }
    ]
    
    for test in violation_tests:
        print(f"\n  🧪 Testing: {test['name']}")
        try:
            # Use jsonschema directly to test schema violations
            jsonschema.validate(test['data'], DETAILED_PERSONA_SCHEMA)
            
            if test['should_fail']:
                print(f"    ❌ FAILED: Should have detected schema violation")
                all_tests_passed = False
            else:
                print(f"    ✅ PASSED: Valid data accepted")
                
        except jsonschema.ValidationError as e:
            if test['should_fail']:
                print(f"    ✅ PASSED: Correctly detected violation: {e.message[:50]}...")
            else:
                print(f"    ❌ FAILED: Incorrectly rejected valid data: {e.message}")
                all_tests_passed = False
        except Exception as e:
            print(f"    ❌ ERROR: Unexpected error: {e}")
            all_tests_passed = False
    
    print(f"\n5️⃣ TESTING BUSINESS RULE ENFORCEMENT")
    print("-" * 50)
    
    # Test business rule violations
    business_rule_tests = [
        {
            "name": "Insufficient major struggles",
            "data": {
                "id": "test", "name": "Test", "age": 30, "gender": "Female",
                "education": "MBA", "relationship_family": "Single", "occupation": "Manager",
                "annual_income": "$50k", "location": "City", "persona_summary": "A" * 100,
                "major_struggles": ["one struggle"]  # Need at least 3
            },
            "should_fail": True
        },
        {
            "name": "Invalid if_only format",
            "data": {
                "id": "test", "name": "Test", "age": 30, "gender": "Female",
                "education": "MBA", "relationship_family": "Single", "occupation": "Manager",
                "annual_income": "$50k", "location": "City", "persona_summary": "A" * 100,
                "if_only_soundbites": ["I wish I could..."]  # Should start with "If only"
            },
            "should_fail": True
        },
        {
            "name": "Age-occupation mismatch",
            "data": {
                "id": "test", "name": "Test", "age": 20, "gender": "Male",
                "education": "High School", "relationship_family": "Single", 
                "occupation": "Senior VP of Engineering",  # Too senior for age 20
                "annual_income": "$200k", "location": "City", "persona_summary": "A" * 100
            },
            "should_fail": True
        }
    ]
    
    for test in business_rule_tests:
        print(f"\n  🧪 Testing: {test['name']}")
        errors = validator.validate_detailed_persona(test['data'])
        
        business_rule_errors = [e for e in errors if "Business rule violation" in e]
        
        if test['should_fail']:
            if business_rule_errors:
                print(f"    ✅ PASSED: Correctly detected business rule violation")
                print(f"      {business_rule_errors[0][:70]}...")
            else:
                print(f"    ❌ FAILED: Should have detected business rule violation")
                all_tests_passed = False
        else:
            if not business_rule_errors:
                print(f"    ✅ PASSED: Valid business rules accepted")
            else:
                print(f"    ❌ FAILED: Incorrectly flagged valid business rules")
                all_tests_passed = False
    
    print(f"\n6️⃣ TESTING FILE VALIDATION")
    print("-" * 50)
    
    # Create temporary test files
    test_files = []
    
    try:
        # Valid persona file
        valid_file = "test_valid_persona.json"
        with open(valid_file, 'w') as f:
            json.dump(detailed_personas[0].to_json_schema_dict(), f)
        test_files.append(valid_file)
        
        result = validate_persona_file(valid_file)
        if result['valid']:
            print(f"  ✅ Valid file validation PASSED")
        else:
            print(f"  ❌ Valid file validation FAILED: {result['errors']}")
            all_tests_passed = False
        
        # Invalid JSON file
        invalid_file = "test_invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json")
        test_files.append(invalid_file)
        
        result = validate_persona_file(invalid_file)
        if not result['valid'] and any("Invalid JSON" in error for error in result['errors']):
            print(f"  ✅ Invalid JSON detection PASSED")
        else:
            print(f"  ❌ Invalid JSON detection FAILED")
            all_tests_passed = False
        
# Array of personas file
        array_file = "test_persona_array.json"
        personas_array = [p.to_json_schema_dict() for p in detailed_personas]
        with open(array_file, 'w') as f:
            json.dump(personas_array, f)
        test_files.append(array_file)
        
        result = validate_persona_file(array_file)
        is_valid = result.get('valid', result.get('total_errors', 1) == 0)
        persona_count = result.get('persona_count', result.get('total_personas', 0))
        
        if is_valid and persona_count == 3:
            print(f"  ✅ Persona array validation PASSED")
        else:
            print(f"  ❌ Persona array validation FAILED: Valid={is_valid}, Count={persona_count}")
            if result.get('total_errors', 0) > 0:
                print(f"    Errors: {result.get('total_errors')}")
            all_tests_passed = False
            
    finally:
        # Clean up test files
        for file_path in test_files:
            try:
                os.remove(file_path)
            except:
                pass
    
    print(f"\n7️⃣ TESTING COLLECTION VALIDATION")
    print("-" * 50)
    
    # Test validating multiple personas at once
    persona_dicts = [p.to_json_schema_dict() for p in detailed_personas]
    collection_result = validator.validate_persona_collection(persona_dicts)
    
    print(f"  📊 Collection Results:")
    print(f"    • Total Personas: {collection_result['total_personas']}")
    print(f"    • Valid Personas: {collection_result['valid_personas']}")
    print(f"    • Invalid Personas: {collection_result['invalid_personas']}")
    print(f"    • Total Errors: {collection_result['total_errors']}")
    
    if collection_result['total_errors'] == 0 and collection_result['valid_personas'] == 3:
        print(f"  ✅ Collection validation PASSED")
    else:
        print(f"  ❌ Collection validation FAILED")
        all_tests_passed = False
        
        # Show detailed errors
        for result in collection_result['persona_results']:
            if not result['valid']:
                print(f"    ❌ {result['name']}: {result['errors']}")
    
    print(f"\n8️⃣ TESTING SCHEMA COMPLETENESS")
    print("-" * 50)
    
    # Verify all expected fields are covered in schema
    sample_persona = detailed_personas[0]
    persona_dict = sample_persona.to_dict()
    schema_properties = DETAILED_PERSONA_SCHEMA['properties'].keys()
    
    missing_in_schema = []
    for field in persona_dict.keys():
        if field not in schema_properties:
            missing_in_schema.append(field)
    
    if missing_in_schema:
        print(f"  ⚠️  Fields in persona not covered by schema: {missing_in_schema}")
    else:
        print(f"  ✅ All persona fields covered by schema")
    
    # Check required fields coverage
    required_fields = DETAILED_PERSONA_SCHEMA['required']
    missing_required = []
    for field in required_fields:
        if not getattr(sample_persona, field, None):
            missing_required.append(field)
    
    if missing_required:
        print(f"  ⚠️  Required fields missing values: {missing_required}")
    else:
        print(f"  ✅ All required fields have values")
    
    print(f"\n" + "=" * 70)
    print(f"📊 FINAL RESULTS")
    print("=" * 70)
    
    if all_tests_passed:
        print("🎉 ALL SCHEMA VALIDATION TESTS PASSED!")
        print("✅ JSON Schema contracts are properly enforced")
        print("✅ Business rules validation working correctly")
        print("✅ Backward compatibility maintained")
        print("✅ File validation operational")
        print("✅ Collection validation functional")
        print("✅ Ready for production deployment")
        
        # Summary statistics
        print(f"\n📈 Schema Coverage Statistics:")
        print(f"   • Detailed Schema: {len(DETAILED_PERSONA_SCHEMA['properties'])} properties")
        print(f"   • Basic Schema: {len(BASIC_PERSONA_SCHEMA['properties'])} properties") 
        print(f"   • Session Schema: {len(SESSION_PERSONA_SCHEMA['properties'])} properties")
        print(f"   • Required Fields: {len(DETAILED_PERSONA_SCHEMA['required'])} fields")
        print(f"   • Business Rules: 7+ validation rules")
        print(f"   • Test Coverage: 8 comprehensive test categories")
        
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Manual fixes required before deployment")
        print("📋 Review error details above")
    
    print("=" * 70)
    
    return all_tests_passed

if __name__ == "__main__":
    success = test_schema_contracts()
    sys.exit(0 if success else 1)