# Grade Translation System - User Guide

## Overview

The SEIM Grade Translation System enables international student exchange programs to work with different grading scales from around the world. Students can enter their grades in their home institution's grading system, and the system automatically converts them for comparison with program requirements.

## Features

- **Multiple Grading Scales**: Support for US GPA 4.0, ECTS, UK Classifications, German, French, Canadian, and more
- **Automatic Conversion**: Grades are automatically translated between different scales
- **Transparent Comparisons**: Students see both their original grade and the converted equivalent
- **Admin Management**: Administrators can add custom grading scales and translation mappings

## Supported Grade Scales

### Currently Available

1. **US GPA 4.0 Scale** - Standard US letter grades (A, B, C, D, F) with GPA equivalents
2. **ECTS** - European Credit Transfer System (A, B, C, D, E, FX, F)
3. **UK Degree Classification** - First Class, 2:1, 2:2, Third, Pass, Fail
4. **German Scale** - 1.0 to 5.0 (where 1.0 is best)
5. **French Scale** - 0 to 20 point system
6. **Canadian Percentage Scale** - Percentage-based with letter grade equivalents

## For Students

### Setting Your Grading Scale

1. **Navigate to Your Profile**
   - Click on your name in the top right
   - Select "Profile"

2. **Select Your Grade Scale**
   - In the "Academic Information" section
   - Choose your institution's grading scale from the dropdown
   - This tells SEIM which grading system your grades are in

3. **Enter Your GPA/Grade**
   - Enter your grade using your institution's scale
   - Example: If you're from Germany with a 1.3 grade, select "German Grading Scale" and enter 1.3
   - The system will automatically calculate your 4.0 GPA equivalent

### Viewing Grade Conversions

When you view program requirements:
- You'll see the minimum grade required in the program's scale
- If your grade is in a different scale, you'll see both:
  - Your grade in your scale
  - The equivalent in the program's scale
- Example: "Your grade: 1.3 (German) = 3.7 GPA (US)"

### Applying to Programs

When checking eligibility:
- The system automatically converts your grade to match the program's requirements
- You'll get clear feedback if your grade meets the minimum
- Example message: "GPA below program minimum. Your GPA equivalent: 3.20, Required: 3.50"

## For Coordinators

### Reviewing Applications

When reviewing student applications:
1. **View Original Grades**: See the student's grade in their original scale
2. **See Conversions**: View the converted equivalent for comparison
3. **Fair Comparison**: All students' grades are normalized to a common scale

### Setting Program Requirements

When creating or editing programs:
1. Set the minimum GPA/grade requirement
2. Optionally specify which grading scale the requirement is in
3. The system will compare applicants' grades fairly across different scales

## For Administrators

### Managing Grade Scales

**Access**: Admin Panel → Grade Translation System → Grade Scales

1. **View Existing Scales**
   - See all available grading scales
   - View grade values within each scale

2. **Add New Scale**
   - Click "Add Grade Scale"
   - Fill in:
     - Name: Display name (e.g., "Australian HD Scale")
     - Code: Unique identifier (e.g., "AUS_HD")
     - Country: Where this scale is used
     - Min/Max values: Range of the scale
     - Passing value: Minimum passing grade
     - Is Reverse Scale: Check if lower values are better (like German scale)

3. **Add Grade Values**
   - When creating/editing a scale, add individual grades
   - For each grade specify:
     - Label: How the grade appears (e.g., "HD", "A+", "1.0")
     - Numeric value: The grade's numeric representation
     - GPA Equivalent: What this translates to on a 4.0 scale
     - Percentage range (optional): Min/max percentages
     - Description: What the grade means

### Managing Translations

**Access**: Admin Panel → Grade Translation System → Grade Translations

1. **View Existing Translations**
   - See direct translation mappings between grades
   - View confidence levels

2. **Add Manual Translation**
   - Select source grade (from one scale)
   - Select target grade (from another scale)
   - Set confidence level (0.0 to 1.0)
   - Add notes explaining the translation rationale

3. **Automatic Translations**
   - If no direct translation exists, the system uses GPA equivalents
   - This provides a fallback for all scale pairs

### Seeding Grade Scales

To populate the database with common grade scales:

```bash
docker-compose exec web python manage.py seed_grade_scales
```

To replace existing scales:

```bash
docker-compose exec web python manage.py seed_grade_scales --clear
```

## API Usage

### For Developers

The grade translation system provides a REST API for programmatic access.

#### Translate a Grade

```http
POST /grades/api/translations/translate/
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "source_grade_value_id": "uuid-of-source-grade",
  "target_scale_id": "uuid-of-target-scale",
  "fallback_to_gpa": true
}
```

**Response:**
```json
{
  "source_grade": {
    "id": "...",
    "label": "A",
    "gpa_equivalent": 4.0,
    "grade_scale_code": "US_GPA_4"
  },
  "target_grade": {
    "id": "...",
    "label": "A",
    "gpa_equivalent": 4.0,
    "grade_scale_code": "ECTS"
  },
  "translation_method": "direct",
  "confidence": 1.0
}
```

#### Convert GPA to Grade

```http
POST /grades/api/translations/convert_gpa/
Content-Type: application/json

{
  "gpa_value": 3.5,
  "target_scale_id": "uuid-of-scale"
}
```

#### Check Eligibility

```http
POST /grades/api/translations/check_eligibility/
Content-Type: application/json

{
  "student_gpa": 1.3,
  "student_scale_id": "uuid-of-german-scale",
  "required_gpa": 3.5,
  "required_scale_id": "uuid-of-us-scale"
}
```

**Response:**
```json
{
  "eligible": true,
  "student_grade": "1.3",
  "student_gpa_equivalent": 3.7,
  "required_grade": "B+",
  "required_gpa_equivalent": 3.5,
  "reason": "Meets requirement"
}
```

#### List Grade Scales

```http
GET /grades/api/scales/
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Get Grade Values for a Scale

```http
GET /grades/api/values/by_scale/?grade_scale=uuid-of-scale
Authorization: Bearer YOUR_JWT_TOKEN
```

## Translation Logic

### How Grades Are Converted

1. **Direct Translation** (Preferred)
   - If a manual translation mapping exists, it's used
   - Example: US "A" → ECTS "A" (confidence 100%)

2. **GPA Equivalent** (Fallback)
   - Each grade has a normalized 4.0 GPA equivalent
   - The system finds the closest matching grade in the target scale
   - Example: German 1.3 (GPA 3.7) → US "A-" (GPA 3.7)

3. **Percentage-Based** (Future)
   - Uses percentage ranges for additional accuracy
   - Currently in development

### Confidence Levels

- **1.0 (100%)**: Exact or highly confident match
- **0.8-0.9**: Good match with minor differences
- **0.6-0.7**: Reasonable match but some uncertainty
- **< 0.6**: Poor match, review recommended

## Best Practices

### For Students
- ✅ Always select your correct grading scale
- ✅ Enter grades exactly as they appear on your transcript
- ✅ Verify the converted GPA equivalent makes sense
- ❌ Don't manually convert grades yourself

### For Coordinators
- ✅ Review the grading scale each student uses
- ✅ Consider context when borderline cases arise
- ✅ Document any manual overrides
- ❌ Don't rely solely on automated conversions for final decisions

### For Administrators
- ✅ Regularly review and update translation mappings
- ✅ Add institution-specific scales when needed
- ✅ Document the rationale for custom translations
- ✅ Test new scales thoroughly before activating

## Troubleshooting

### Student's Grade Not Converting Correctly

1. **Check the grade scale**: Ensure the correct scale is selected
2. **Verify the grade value**: Make sure the exact grade value exists in the scale
3. **Review the GPA equivalent**: Check if the grade value has the correct GPA mapping

### Missing Grade Scale

1. **Check available scales**: View all scales in the admin panel
2. **Add custom scale**: If needed, administrators can add institution-specific scales
3. **Contact support**: For commonly used scales not yet in the system

### Unexpected Eligibility Result

1. **View the conversion details**: Check both the original and converted grades
2. **Verify program requirements**: Ensure the minimum GPA is set correctly
3. **Review grade scale settings**: Confirm reverse scales are properly marked

## FAQ

**Q: Can I change my grading scale after creating my profile?**  
A: Yes, you can update your grading scale in your profile settings at any time.

**Q: What happens if my institution uses a scale not in the system?**  
A: Contact your coordinator or administrator to request the scale be added.

**Q: Are grade conversions always accurate?**  
A: Conversions are based on standardized equivalents, but grading systems vary. Use them as a guide, not an absolute measure.

**Q: Can I see how my grade compares in different scales?**  
A: Currently, you see conversions when applying to programs. A comparison tool is planned for future releases.

**Q: Who determines the GPA equivalents?**  
A: Equivalents are based on standard academic conversion tables and can be customized by administrators.

**Q: What if two scales have the same code?**  
A: Each scale code must be unique. The system enforces this constraint.

## Future Enhancements

- 🔜 Weighted GPA calculations (considering credit hours)
- 🔜 Transcript upload with automatic grade recognition
- 🔜 Historical grade scale versions
- 🔜 Machine learning-based translation suggestions
- 🔜 Bulk student import with grade conversion
- 🔜 Grade comparison visualization tools

## Support

For questions or issues with the grade translation system:
- **Students**: Contact your program coordinator
- **Coordinators**: Contact system administrators
- **Administrators**: Refer to the technical documentation in `grade_translation_design.md`

---

**Last Updated**: {{ current_date }}  
**Version**: 1.0  
**System**: SEIM Grade Translation Module

