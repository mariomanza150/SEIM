# Remaining Test Fixes - Comprehensive Plan

**Date**: October 18, 2025  
**Current Status**: 525/535 tests passing (10 remaining)

---

## 🎯 Objective

Fix all 10 remaining test failures systematically and verify 100% test pass rate.

---

## 📋 Remaining Failures Inventory

### Category A: Application Submission Workflow (5 tests)
**File**: `tests/unit/exchange/test_application_submission.py`

1. ❌ `test_student_cannot_modify_submitted_application` - Student tries to change status back to draft
2. ❌ `test_comment_creation_on_application` - Creating comments on applications
3. ❌ `test_can_submit_application` - Service method test
4. ❌ `test_can_withdraw_application` - Service method test
5. ❌ `test_get_application_status_history` - Getting status history

**Likely Root Causes**:
- Permission issues (students editing submitted apps)
- Service method signatures or logic changes
- Test expectations vs actual behavior

---

### Category B: Virus Scanner (3 tests)
**File**: `tests/unit/documents/test_virus_scanner.py`

1. ❌ `test_scan_file_for_viruses_infected` - Expects ValidationError when virus detected
2. ❌ `test_document_service_virus_scan_error` - Error handling in document service
3. ❌ `test_document_service_virus_scan_infected` - Infected file rejection

**Likely Root Cause**:
- Virus scanner is a stub that doesn't raise ValidationError
- Tests expect actual virus scanning behavior

---

### Category C: Form Builder (2 tests)
**File**: `tests/test_form_builder_integration.py`

1. ❌ `test_form_builder_urls_accessible` - Form builder URL routing (404 error)
2. ❌ `test_multiple_forms_available_for_selection` - FormType model issue (unexpected keyword 'code')

**Likely Root Causes**:
- URL routing not set up for form builder
- FormType model schema mismatch

---

## 🔍 Investigation Strategy

### Phase 1: Detailed Investigation (15-20 min)
For each category:
1. Run failing test with verbose output
2. Capture exact error message and stack trace
3. Identify root cause
4. Document required fix

### Phase 2: Fix Prioritization (5 min)
Order fixes by:
1. **Complexity** (simple → complex)
2. **Risk** (low risk → high risk)
3. **Dependencies** (independent → dependent)

### Phase 3: Systematic Execution (60-90 min)
1. Fix one category at a time
2. Verify fix doesn't break other tests
3. Commit logical changes together
4. Document each fix

---

## 📊 Execution Plan

### Step 1: Investigate All Failures (20 min)
Run each test individually with full error details

### Step 2: Fix Category B - Virus Scanner (15 min)
**Why First?**: 
- Likely simple fix (make stub raise ValidationError)
- Self-contained, low risk
- No dependencies on other fixes

**Approach**:
1. Check virus_scanner.py stub implementation
2. Make it raise ValidationError for infected files
3. Update document service integration

### Step 3: Fix Category A - Application Submission (30 min)
**Why Second?**:
- Related to our recent serializer changes
- Medium complexity
- May need permission or service logic adjustments

**Approach**:
1. Fix permission checks for submitted applications
2. Update service method tests
3. Fix comment creation integration

### Step 4: Fix Category C - Form Builder (20 min)
**Why Last?**:
- May require URL configuration
- May need model schema investigation
- Potentially higher risk

**Approach**:
1. Check URL routing configuration
2. Investigate FormType model schema
3. Update test or fix routing/model

---

## ✅ Success Criteria

1. **All 535 tests passing** (0 failures)
2. **No regressions** (all previously passing tests still pass)
3. **Fixes are minimal** (no over-engineering)
4. **Code quality maintained** (proper error handling, clear logic)

---

## 📝 Documentation Requirements

For each fix:
- Document the error
- Explain root cause
- Describe solution
- Note any side effects

---

## 🎯 Expected Completion

- **Investigation**: 20 minutes
- **Virus Scanner Fixes**: 15 minutes
- **Application Service Fixes**: 30 minutes
- **Form Builder Fixes**: 20 minutes
- **Final Verification**: 10 minutes

**Total**: ~95 minutes (1.6 hours)

---

**Status**: Ready to Execute  
**Next Action**: Begin Phase 1 - Detailed Investigation


