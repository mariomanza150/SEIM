# Root Directory Cleanup Plan

## 📋 Files to Move from Root

### Status Reports → `docs/status/`
1. **E2E_EXPANSION_PROGRESS.md** → `docs/status/e2e-expansion-progress.md`
   - Status: Progress report (90% complete)
   - Already referenced in `docs/index.md` as `./status/e2e-expansion-progress.md`

2. **TEST_COVERAGE_IMPROVEMENTS.md** → `docs/status/test-coverage-improvements.md`
   - Status: Test coverage summary (COMPLETE)
   - Already referenced in `docs/index.md` as `./status/test-coverage-improvements.md`

3. **VIDEO_DEMOS_READY.md** → `docs/status/video-demos-ready.md`
   - Status: Implementation complete notification
   - New file (not yet in index.md)

### Guides → `docs/guides/`
1. **E2E_QUICK_FIX_GUIDE.md** → `docs/guides/e2e-quick-fix-guide.md`
   - Guide: E2E test setup troubleshooting
   - Already referenced in `docs/index.md` as `./guides/e2e-quick-fix-guide.md`

2. **VIDEO_DEMOS_GUIDE.md** → `docs/guides/video-demos-guide.md`
   - Guide: How to generate video demos
   - Already referenced in `docs/index.md` as `./guides/video-demos-guide.md`

3. **VIDEO_REVIEW_CHECKLIST.md** → `docs/guides/video-review-checklist.md`
   - Guide: Video review checklist
   - Already referenced in `docs/index.md` as `./guides/video-review-checklist.md`

## 📁 Directories to Create
- `docs/status/` (referenced but missing)
- `docs/guides/` (referenced but missing)

## ✅ Files to Keep in Root
- **README.md** (standard project README - should stay)

## 🔍 Additional Cleanup Opportunities

### In `docs/` directory (already there, but could be organized):
- Many status reports mixed with guides
- Consider moving more files to `status/` or `guides/` subdirectories

### Potential duplicates or outdated files:
- Check for duplicate content between root files and docs/ files
- Archive old session summaries if they exist

## 📝 Action Items
1. Create `docs/status/` directory
2. Create `docs/guides/` directory
3. Move 6 markdown files from root to appropriate subdirectories
4. Update any broken references (if any)
5. Verify `docs/index.md` links work after move
6. Consider adding `VIDEO_DEMOS_READY.md` to index.md if needed
