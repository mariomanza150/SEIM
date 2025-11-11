# Grade Translation System Design

## Overview

The grade translation system enables SEIM to support international student exchanges by providing conversion between different grading scales used worldwide.

## Requirements

### Functional Requirements
1. Support multiple grading scales (US GPA 4.0, ECTS, UK classifications, German scale, etc.)
2. Define grade values within each scale with numeric equivalents
3. Translate grades between any two scales
4. Associate student profiles with their institution's grading scale
5. Convert student grades to program requirements' scale for eligibility checking
6. Provide admin interface for managing scales and translations
7. Support both direct and intermediate conversions (via GPA equivalent)

### Non-Functional Requirements
1. Maintain data integrity with proper validation
2. Provide clear audit trail for grade translations
3. Handle edge cases gracefully (no direct translation available)
4. Ensure performance with caching where appropriate

## Data Model

### GradeScale
Represents a grading system used by an institution or country.

**Fields:**
- `id` (UUID): Primary key
- `name` (CharField): Display name (e.g., "US GPA 4.0 Scale")
- `code` (CharField): Unique code (e.g., "US_GPA_4", "ECTS", "UK_CLASS")
- `description` (TextField): Detailed description
- `country` (CharField): Country/region where used
- `min_value` (FloatField): Minimum possible grade value
- `max_value` (FloatField): Maximum possible grade value
- `passing_value` (FloatField): Minimum passing grade
- `is_active` (BooleanField): Whether scale is currently in use
- `created_at`, `updated_at` (DateTimeField): Timestamps

### GradeValue
Individual grade values within a scale with their numeric equivalents.

**Fields:**
- `id` (UUID): Primary key
- `grade_scale` (ForeignKey): Reference to GradeScale
- `label` (CharField): Grade label (e.g., "A", "1.0", "First Class")
- `numeric_value` (FloatField): Numeric representation within scale
- `gpa_equivalent` (FloatField): Normalized 4.0 GPA equivalent for cross-scale comparison
- `min_percentage` (FloatField, optional): Minimum percentage for this grade
- `max_percentage` (FloatField, optional): Maximum percentage for this grade
- `description` (TextField, optional): Description of what this grade means
- `order` (PositiveIntegerField): Display order
- `created_at`, `updated_at` (DateTimeField): Timestamps

### GradeTranslation
Direct translation mappings between specific grades in different scales.

**Fields:**
- `id` (UUID): Primary key
- `source_grade` (ForeignKey): GradeValue in source scale
- `target_grade` (ForeignKey): GradeValue in target scale
- `notes` (TextField, optional): Translation notes/rationale
- `created_at`, `updated_at` (DateTimeField): Timestamps

**Unique Constraint:** (source_grade, target_grade)

## Common Grade Scales

### 1. US GPA 4.0 Scale
- A (4.0), A- (3.7), B+ (3.3), B (3.0), B- (2.7), C+ (2.3), C (2.0), C- (1.7), D+ (1.3), D (1.0), F (0.0)
- Passing: 2.0

### 2. ECTS (European Credit Transfer System)
- A (4.0), B (3.5), C (3.0), D (2.5), E (2.0), FX (1.0), F (0.0)
- Passing: 2.0 (E)

### 3. UK Classification
- First Class (4.0), Upper Second (3.5), Lower Second (3.0), Third Class (2.0), Pass (1.5), Fail (0.0)
- Passing: 2.0

### 4. German Scale (1.0-5.0, lower is better)
- 1.0 (4.0 GPA), 1.3 (3.7), 1.7 (3.3), 2.0 (3.0), 2.3 (2.7), 2.7 (2.3), 3.0 (2.0), 3.3 (1.7), 3.7 (1.3), 4.0 (1.0), 5.0 (0.0)
- Passing: 4.0

## Translation Logic

### Direct Translation
1. Check if direct translation exists in GradeTranslation table
2. Return target grade if found

### GPA Equivalent Translation (Fallback)
1. Get GPA equivalent of source grade
2. Find closest GPA equivalent in target scale
3. Return corresponding target grade

### Percentage-based Translation (Secondary Fallback)
1. Get percentage range of source grade
2. Find target grade with overlapping percentage range
3. Return corresponding target grade

## Services

### GradeTranslationService

**Methods:**
- `translate_grade(source_grade_value_id, target_scale_id)`: Translate a grade to target scale
- `get_gpa_equivalent(grade_value_id)`: Get 4.0 GPA equivalent of any grade
- `check_eligibility_with_translation(student_profile, program)`: Check eligibility with grade translation
- `convert_gpa_to_scale(gpa_value, target_scale_id)`: Convert numeric GPA to target scale grade
- `get_available_translations(grade_value_id)`: Get all available translations for a grade
- `suggest_translation(source_grade_id, target_grade_id)`: Create suggested translation mapping

## UI/UX Considerations

### Admin Interface
1. Manage grade scales (CRUD operations)
2. Manage grade values within each scale
3. Create/edit translation mappings
4. Import/export grade scales and translations
5. Preview translations before saving

### Student Profile
1. Select institutional grade scale
2. Enter grade in native scale
3. View GPA equivalent automatically

### Program Configuration
1. Specify grade scale for requirements
2. Set minimum grade in that scale
3. View converted requirements in other scales

## Migration Strategy

1. Create new models with migrations
2. Add grade_scale foreign key to Profile (nullable initially)
3. Create management command to seed common scales
4. Migrate existing GPA values to US 4.0 scale
5. Update services to use grade translation
6. Add UI for scale management

## Testing Strategy

1. Unit tests for each model's validation logic
2. Unit tests for translation service methods
3. Integration tests for eligibility checking with translation
4. Admin interface tests
5. API endpoint tests
6. Edge case testing (missing translations, invalid scales)

## Performance Considerations

1. Cache frequently used translations
2. Index foreign keys and lookup fields
3. Preload grade values when loading scales
4. Consider materialized views for complex conversions

## Future Enhancements

1. Machine learning-based translation suggestions
2. Transcript upload with automatic grade recognition
3. Bulk grade translation for entire transcripts
4. Historical grade scale versions (for retired scales)
5. Weighted GPA calculations (credit hours)
6. Institution-specific grade scale customizations

