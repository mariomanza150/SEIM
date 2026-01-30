# Visual Testing Guide - New Admin Features

**Date**: October 18, 2025  
**Features to Test**: 7 (3 Backend + 4 Admin UI)

---

## 🚀 Quick Start

### Access the Admin Interface

**URL**: http://localhost:8000/admin/

**Login Credentials**:
- **Username**: `admin`
- **Password**: `admin123` (or your admin password)

**If you need to create an admin user**:
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## ✅ Visual Testing Checklist

### 🔷 Test 1: Program List Display

**Navigate to**: http://localhost:8000/admin/exchange/program/

**What to Look For**:
- [ ] **Eligibility Criteria** column shows:
  - 📊 GPA requirements (e.g., "GPA ≥3.5")
  - 🗣️ Language requirements (e.g., "English (B2+)")
  - 🎂 Age requirements (e.g., "18-30 years")
  - ⚡ Lightning bolt if auto-reject enabled
  - Icons display correctly
  - Text is readable and formatted

- [ ] **Applications** column shows:
  - Number of applications (e.g., "5 applications")
  - Link is clickable
  - Clicking filters to that program's applications

**Expected View**:
```
┌─────────────────────────────────────────────────────────────────────┐
│ Name              | Start Date | End Date | Active | Eligibility   │
├─────────────────────────────────────────────────────────────────────┤
│ Erasmus 2025      | 2025-09-01 | 2026-01-31 | ✓   | 📊 GPA ≥3.5 | │
│                   |            |            |      | 🗣️ English    │
│                   |            |            |      | (B2+) |      │
│                   |            |            |      | 🎂 18-30      │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 🔷 Test 2: Program Cloning

**Steps**:
1. On the program list page
2. Check the box next to one or more programs
3. From the "Action" dropdown, select **"🔄 Clone selected programs"**
4. Click **"Go"** button

**What to Verify**:
- [ ] Success message appears: "Successfully cloned X program(s). Clones are inactive by default."
- [ ] New program(s) appear in list with " (Copy)" suffix
- [ ] Cloned programs have `is_active` = **False** (unchecked)
- [ ] Click on cloned program to verify:
  - [ ] All fields copied correctly (description, dates, GPA, language, etc.)
  - [ ] Min language level copied
  - [ ] Age requirements copied
  - [ ] Auto-reject setting copied

**Expected**: Instant cloning, all fields preserved

---

### 🔷 Test 3: Bulk Activate/Deactivate

**Test Activation**:
1. Find or create inactive programs (look for cloned ones)
2. Select multiple inactive programs
3. Choose **"✅ Activate selected programs"**
4. Click "Go"

**Verify**:
- [ ] Success message: "Successfully activated X program(s)."
- [ ] Programs now show Active = ✓ (checked)
- [ ] Changes persist on page refresh

**Test Deactivation**:
1. Select active programs
2. Choose **"❌ Deactivate selected programs"**
3. Click "Go"

**Verify**:
- [ ] Success message: "Successfully deactivated X program(s)."
- [ ] Programs now show Active = ✗ (unchecked)

---

### 🔷 Test 4: Program Detail View - Enhanced Fieldsets

**Navigate to**: Click on any program in the list

**What to Look For**:
- [ ] **Organized Sections** (should see 7 sections):
  1. Basic Information (Name, Description, Active, Recurring)
  2. Dates (Start Date, End Date)
  3. Academic Requirements (Min GPA, Application Form)
  4. **Language Requirements** (collapsible)
     - Required Language dropdown
     - Min Language Level dropdown (A1-C2)
     - Helpful description text
  5. **Age Requirements** (collapsible)
     - Min Age field
     - Max Age field
     - Helpful description text
  6. **Automation** (collapsible)
     - Auto-reject ineligible checkbox
     - Helpful description text
  7. Audit (Created, Updated, Application count)

- [ ] Collapsible sections can be expanded/collapsed
- [ ] All fields editable
- [ ] Save works correctly

**Test Edit**:
1. Click on a program
2. Expand "Language Requirements"
3. Set "Required Language" = "English"
4. Set "Min Language Level" = "B2"
5. Click "Save"
6. **Verify**: Changes saved, eligibility summary updated in list

---

### 🔷 Test 5: Filters and Search

**On Program List**:

**Test Filters** (right sidebar):
- [ ] **Active**: Filter by Yes/No
- [ ] **Recurring**: Filter recurring programs
- [ ] **Auto-reject Ineligible**: Filter by automation
- [ ] **Required Language**: Filter by language
- [ ] **Min Language Level**: Filter by CEFR level

**Test Search**:
- [ ] Type program name in search box
- [ ] Results filter instantly
- [ ] Search works on description too

---

### 🔷 Test 6: Application List Display

**Navigate to**: http://localhost:8000/admin/exchange/application/

**What to Look For**:
- [ ] **Eligibility** column shows:
  - ✓ Green checkmark with "Eligible"
  - ✗ Red X with "Ineligible"
  - ? Gray question mark for "Unknown"

- [ ] Hover over red X:
  - [ ] Tooltip shows failure reasons
  - [ ] Clear, readable text

**Expected View**:
```
┌──────────────────────────────────────────────────────────────────┐
│ ID    | Student | Program  | Status | Eligibility | Submitted   │
├──────────────────────────────────────────────────────────────────┤
│ abc-1 | john@.. | Erasmus  | Draft  | ✓ Eligible  | 2025-10-15  │
│ abc-2 | jane@.. | Study    | Draft  | ✗ Ineligible| -           │
└──────────────────────────────────────────────────────────────────┘
```

---

### 🔷 Test 7: Application Detail - Eligibility Check

**Steps**:
1. Click on any application in the list
2. Scroll to **"Eligibility"** section
3. Expand if collapsed

**For Eligible Application**:
- [ ] Green background box
- [ ] Checkmark ✓ at top
- [ ] Text: "Student meets all eligibility requirements"
- [ ] Bulleted list showing:
  - GPA comparison (student vs required)
  - Language match
  - Language level comparison
  - Age verification (if applicable)

**Expected**:
```
┌─────────────────────────────────────────────────────────┐
│ ✓ Student meets all eligibility requirements           │
│                                                         │
│  • GPA: 3.7 (required: ≥3.5)                          │
│  • Language: English (required: English)               │
│  • Language Level: B2 (required: B1+)                  │
│  • Age: 25 years (required: 18-30)                    │
└─────────────────────────────────────────────────────────┘
```

**For Ineligible Application**:
- [ ] Red background box
- [ ] X ✗ at top
- [ ] Text: "Student does not meet eligibility requirements"
- [ ] List of specific failures

---

### 🔷 Test 8: Bulk Eligibility Check

**On Application List**:
1. Select multiple applications (checkbox)
2. From Actions dropdown: **"🔍 Check eligibility for selected applications"**
3. Click "Go"

**Verify**:
- [ ] Info message appears: "Eligibility check complete: X eligible, Y ineligible"
- [ ] Numbers are accurate
- [ ] Action completes quickly

---

### 🔷 Test 9: Application Filters

**Test New Filters**:
- [ ] Filter by Status
- [ ] Filter by Withdrawn (Yes/No)
- [ ] Filter by Program Language Requirement

**Verify**: Filters work and results update correctly

---

### 🔷 Test 10: API Endpoints (Optional)

**Test Program Clone API**:
```bash
# Get auth token first (replace with your token)
curl -X POST http://localhost:8000/api/programs/{PROGRAM_ID}/clone/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response**:
```json
{
  "status": "Program cloned successfully",
  "program": {
    "id": "new-uuid",
    "name": "Original Name (Copy)",
    "is_active": false,
    ...
  }
}
```

**Test Eligibility Check API**:
```bash
curl http://localhost:8000/api/programs/{PROGRAM_ID}/check_eligibility/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected Response** (eligible):
```json
{
  "eligible": true,
  "message": "All eligibility requirements met",
  "checks_passed": [...]
}
```

**Expected Response** (ineligible):
```json
{
  "eligible": false,
  "message": "Eligibility requirements not met:\n- GPA below...",
  "program": {...}
}
```

---

## 🎯 Testing Scenarios

### Scenario 1: Semester Rotation
**Goal**: Clone 10 programs for next semester

1. Go to program list
2. Select 10 programs from Fall 2025
3. Action: "🔄 Clone selected programs"
4. Go
5. **Verify**: 10 new programs with "(Copy)" suffix, all inactive
6. **Edit one**: Update dates to Spring 2026
7. **Activate**: Use bulk activate
8. **Result**: Ready for new semester in minutes

**Expected Time**: 2-3 minutes (vs 100+ minutes manually)

---

### Scenario 2: Eligibility Review
**Goal**: Review 20 applications for eligibility

1. Go to application list
2. Look at Eligibility column
3. **Observe**:
   - Green ✓ for eligible students
   - Red ✗ for ineligible students
4. **Hover** over red X to see reasons
5. **Click** on one ineligible application
6. **View** detailed eligibility section
7. **Understand** exactly why student doesn't qualify

**Expected Time**: 5-10 seconds per app (vs 2-3 minutes manually)

---

### Scenario 3: Program Setup
**Goal**: Create new program with eligibility criteria

1. Click "Add Program"
2. Fill basic info
3. **Expand "Language Requirements"**:
   - Select "English"
   - Select "B2" minimum level
4. **Expand "Age Requirements"**:
   - Set min_age = 18
   - Set max_age = 30
5. **Expand "Automation"**:
   - Check "Auto-reject ineligible"
6. Save

7. **Verify** in list:
   - Eligibility summary shows all criteria
   - Icons and formatting correct

---

## 🎨 What You Should See

### Program List Enhancements
✅ **New Columns**:
- Eligibility Criteria (with icons)
- Applications (with counts and links)

✅ **New Actions** (dropdown):
- 🔄 Clone selected programs
- ✅ Activate selected programs  
- ❌ Deactivate selected programs

✅ **New Filters** (sidebar):
- Required Language
- Min Language Level
- Auto-reject Ineligible
- (Plus existing filters)

### Application List Enhancements
✅ **New Column**:
- Eligibility (✓✗? indicators with colors)

✅ **New Actions**:
- 🔍 Check eligibility for selected applications
- 🚫 Mark selected as withdrawn

### Application Detail Enhancements
✅ **New Section**:
- Eligibility (color-coded, detailed breakdown)

---

## 📸 Expected Screenshots (Descriptions)

### Program List
```
Actions: [🔄 Clone selected programs ▼]

[✓] Erasmus 2025    | 2025-09-01 | ... | ✓ | 📊 GPA ≥3.5 | 🗣️ English (B2+) | 15 apps
[✓] Study Abroad    | 2025-09-01 | ... | ✗ | 📊 GPA ≥3.0 | 🎂 18-25 years   | 8 apps
[ ] Test (Copy)     | 2025-09-01 | ... | ✗ | No criteria                    | 0 apps

Filters:              
  Active: All ▼       
  Recurring: All ▼    
  Language: English ▼ 
  Level: B2 ▼         
```

### Application Detail
```
Program: Erasmus 2025
Student: john@university.edu
Status: Draft

┌─ Eligibility ──────────────────────────────────────────┐
│                                                        │
│  ✓ Student meets all eligibility requirements         │
│                                                        │
│   • GPA: 3.7 (required: ≥3.5)                        │
│   • Language: English (required: English)             │
│   • Language Level: B2 (required: B1+)                │
│   • Age: 25 years (required: 18-30)                  │
│                                                        │
└────────────────────────────────────────────────────────┘

[Save and continue] [Save] [Delete]
```

---

## 🧪 Interactive Testing Steps

### Step-by-Step: Clone a Program

1. **Open**: http://localhost:8000/admin/exchange/program/
2. **Find**: "Erasmus Exchange 2025" (or any program)
3. **Check**: Checkbox next to the program
4. **Select**: "🔄 Clone selected programs" from Actions
5. **Click**: "Go" button
6. **Observe**: 
   - Green success message at top
   - New program "Erasmus Exchange 2025 (Copy)" in list
   - Clone is inactive (unchecked Active column)
7. **Click**: On the cloned program
8. **Verify**: All fields match original
9. **Edit**: Change name to "Spring 2026 Erasmus"
10. **Save**: Click "Save"
11. **Result**: Program ready for next semester! 🎉

**Time**: ~30 seconds (vs 10-15 minutes manually)

---

### Step-by-Step: Check Eligibility

1. **Open**: http://localhost:8000/admin/exchange/application/
2. **Look**: At "Eligibility" column
3. **Observe**:
   - Green ✓ for eligible students
   - Red ✗ for ineligible students
4. **Hover**: Over a red ✗
5. **See**: Tooltip with failure reasons
6. **Click**: On an application with red ✗
7. **Scroll**: To "Eligibility" section
8. **Expand**: If collapsed
9. **Read**: Detailed breakdown with all criteria
10. **Understand**: Exactly why student doesn't qualify

**Time**: ~5 seconds per application (vs 2-3 minutes manually)

---

### Step-by-Step: Bulk Operations

1. **Open**: http://localhost:8000/admin/exchange/program/
2. **Find**: Inactive programs (unchecked Active column)
3. **Select**: Check boxes for 5-10 inactive programs
4. **Action**: "✅ Activate selected programs"
5. **Go**: Click button
6. **Observe**: Success message, all selected now active
7. **Repeat**: Select same programs
8. **Action**: "❌ Deactivate selected programs"
9. **Go**: Click button
10. **Verify**: All now inactive

**Time**: ~10 seconds (vs minutes of individual updates)

---

## 🎨 UI Elements to Verify

### Icons
- [ ] 📊 (Chart) for GPA
- [ ] 🗣️ (Speaking) for Language
- [ ] 🎂 (Birthday cake) for Age
- [ ] ⚡ (Lightning) for Auto-reject
- [ ] ✓ (Green checkmark) for Eligible
- [ ] ✗ (Red X) for Ineligible
- [ ] 🔄 (Recycle) for Clone action
- [ ] ✅ (White checkmark) for Activate
- [ ] ❌ (Red X) for Deactivate
- [ ] 🔍 (Magnifying glass) for Check eligibility

### Colors
- [ ] **Green** (#d4edda) for eligible status
- [ ] **Red** (#f8d7da) for ineligible status
- [ ] **Gray** (#999) for "No criteria" text
- [ ] **Standard blue** for clickable links

### Formatting
- [ ] Eligibility criteria on one line with separators (|)
- [ ] Font size readable (0.9em for summary)
- [ ] Hover tooltips work
- [ ] HTML renders without escaped characters

---

## 🐛 Common Issues to Watch For

### If Eligibility Shows as Ineligible When It Shouldn't
**Cause**: Profile may not have required fields set  
**Fix**: Edit student profile, add:
- GPA
- Language
- Language Level
- Date of Birth

### If Clone Doesn't Copy All Fields
**Expected**: This shouldn't happen (all verified)  
**If it does**: Report as bug

### If Icons Don't Display
**Cause**: Browser encoding issue  
**Fix**: Check browser supports UTF-8

### If Actions Don't Appear in Dropdown
**Cause**: Permission issue  
**Fix**: Ensure logged in as staff/admin user

---

## 📊 Performance to Expect

| Operation | Expected Time |
|-----------|---------------|
| Clone 1 program | < 1 second |
| Clone 10 programs | < 3 seconds |
| Bulk activate 50 programs | < 2 seconds |
| Eligibility check display | Instant |
| Filter applications | < 1 second |

---

## ✅ Success Criteria

### Minimum
- [ ] Can access admin interface
- [ ] Can see new columns
- [ ] Can clone at least one program
- [ ] Eligibility summary displays

### Ideal
- [ ] All icons display correctly
- [ ] All actions work smoothly
- [ ] Bulk operations feel instant
- [ ] Eligibility checks are accurate
- [ ] UI is intuitive and clear

### Excellence
- [ ] Admins excited about time savings
- [ ] No confusion about features
- [ ] Want to use features immediately
- [ ] Report improved workflow

---

## 🎯 Focus Areas for Testing

### High Priority
1. **Program Cloning** - Most impactful feature
2. **Eligibility Display** - Most used feature
3. **Bulk Operations** - Biggest time saver

### Medium Priority
4. Filters work correctly
5. Fieldsets organized well
6. Links navigate properly

### Low Priority  
7. Icon appearance
8. Color schemes
9. Tooltips

---

## 📝 Feedback to Collect

### During Testing
- Is the UI intuitive?
- Are the icons helpful or distracting?
- Is the eligibility summary clear?
- Are the actions easy to find?
- Do bulk operations feel fast?

### After Testing
- Would you use these features regularly?
- What would make them better?
- Any confusing aspects?
- Missing any important info?

---

## 🚀 Next Steps After Visual Testing

### If Everything Looks Good
1. ✅ Mark as approved
2. 📊 Collect usage metrics
3. 🚀 Deploy to production
4. 📢 Announce to users

### If Issues Found
1. 🐛 Document issues
2. 🔧 Prioritize fixes
3. ✅ Retest after fixes
4. ✅ Then deploy

---

## 🎉 Expected Outcome

After visual testing, you should have:

- ✅ Confirmed all features work as designed
- ✅ Verified UI is clean and intuitive
- ✅ Tested performance is acceptable
- ✅ Identified any minor tweaks needed
- ✅ Confidence to deploy

**The admin interface should feel significantly more powerful and user-friendly!**

---

## 📞 Support

**If you encounter any issues**:
1. Check this guide's "Common Issues" section
2. Review `documentation/archive/session_2025_10_18/ADMIN_UI_ENHANCEMENTS.md`
3. Run the verification script: `docker-compose exec web python scripts/test_admin_features.py`
4. Check server logs: `docker-compose logs web`

---

**Visual Testing Guide**  
**Version**: 1.0  
**Features**: 7 enhancements  
**Status**: Ready for testing ✅  
**Admin URL**: http://localhost:8000/admin/

**Happy Testing!** 🎉

