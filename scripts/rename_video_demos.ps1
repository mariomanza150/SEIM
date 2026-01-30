# Rename Video Demo Files to Human-Readable Names
# Maps hash-based Playwright video names to descriptive demo names

param(
    [switch]$DryRun = $false
)

Write-Host ""
Write-Host "Video Demo Renaming Script" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

$videosPath = "tests\e2e_playwright\videos"

if (-not (Test-Path $videosPath)) {
    Write-Host "ERROR: Videos directory not found: $videosPath" -ForegroundColor Red
    exit 1
}

# Map demo numbers to human-readable names based on test function names
$demoNames = @{
    1 = "demo_1_new_student_registration_first_application"
    2 = "demo_2_returning_student_check_status"
    3 = "demo_3_student_withdraw_draft"
    4 = "demo_4_coordinator_review_pending"
    5 = "demo_5_coordinator_request_resubmission"
    6 = "demo_6_coordinator_approve_application"
    7 = "demo_7_admin_create_program"
    8 = "demo_8_admin_manage_users"
    9 = "demo_9_admin_view_analytics"
    10 = "demo_10_admin_system_configuration"
    11 = "demo_11_complete_application_lifecycle"
    12 = "demo_12_multi_user_collaboration"
}

# Get all video files sorted by creation time (oldest first)
$videos = Get-ChildItem -Path $videosPath -Filter "*.webm" -ErrorAction SilentlyContinue | 
    Sort-Object CreationTime

if ($videos.Count -eq 0) {
    Write-Host "ERROR: No video files found in $videosPath" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($videos.Count) video file(s)" -ForegroundColor Green
Write-Host ""

if ($DryRun) {
    Write-Host "DRY RUN MODE - No files will be renamed" -ForegroundColor Yellow
    Write-Host ""
}

$renamedCount = 0
$skippedCount = 0

for ($i = 0; $i -lt $videos.Count; $i++) {
    $video = $videos[$i]
    $demoNumber = $i + 1
    
    if ($demoNumber -le $demoNames.Count) {
        $newName = "$($demoNames[$demoNumber]).webm"
        $newPath = Join-Path $videosPath $newName
        
        # Check if target file already exists
        if (Test-Path $newPath) {
            if ($video.FullName -eq $newPath) {
                Write-Host "[OK] Demo $demoNumber : Already named correctly" -ForegroundColor Green
                Write-Host "    $($video.Name)" -ForegroundColor Gray
                $skippedCount++
                continue
            } else {
                # Target exists but is different file - add timestamp
                $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
                $newName = "$($demoNames[$demoNumber])_$timestamp.webm"
                $newPath = Join-Path $videosPath $newName
            }
        }
        
        Write-Host "Demo $demoNumber : $($demoNames[$demoNumber])" -ForegroundColor Cyan
        Write-Host "    From: $($video.Name)" -ForegroundColor Gray
        Write-Host "    To:   $newName" -ForegroundColor Gray
        
        if (-not $DryRun) {
            try {
                Rename-Item -Path $video.FullName -NewName $newName -ErrorAction Stop
                Write-Host "    [OK] Renamed successfully" -ForegroundColor Green
                $renamedCount++
            } catch {
                Write-Host "    [ERROR] $_" -ForegroundColor Red
            }
        }
        Write-Host ""
    } else {
        Write-Host "[WARN] Extra video (no demo mapping): $($video.Name)" -ForegroundColor Yellow
        $skippedCount++
    }
}

Write-Host ""
Write-Host "Summary:" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "   Would rename: $renamedCount file(s)" -ForegroundColor Yellow
    Write-Host "   Would skip: $skippedCount file(s)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "TIP: Run without -DryRun to actually rename files" -ForegroundColor White
} else {
    Write-Host "   Renamed: $renamedCount file(s)" -ForegroundColor Green
    Write-Host "   Skipped: $skippedCount file(s)" -ForegroundColor Yellow
}

Write-Host ""

