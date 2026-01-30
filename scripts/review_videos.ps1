# Video Review Helper Script
# Opens the videos folder and displays video information

Write-Host "`n🎬 Video Demo Review Helper" -ForegroundColor Cyan
Write-Host "========================`n" -ForegroundColor Cyan

$videosPath = "tests\e2e_playwright\videos"

if (-not (Test-Path $videosPath)) {
    Write-Host "❌ Videos directory not found: $videosPath" -ForegroundColor Red
    exit 1
}

$videos = Get-ChildItem -Path $videosPath -Filter "*.webm" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime

if ($videos.Count -eq 0) {
    Write-Host "❌ No video files found in $videosPath" -ForegroundColor Red
    exit 1
}

Write-Host "📊 Video Summary:" -ForegroundColor Green
Write-Host "   Total Videos: $($videos.Count)" -ForegroundColor White
$totalSize = ($videos | Measure-Object -Property Length -Sum).Sum
Write-Host "   Total Size: $([math]::Round($totalSize / 1MB, 2)) MB" -ForegroundColor White
Write-Host ""

Write-Host "📹 Videos (sorted by creation time):" -ForegroundColor Green
Write-Host ""

$demoNumber = 1
$demoNames = @(
    "New Student Registration & First Application",
    "Returning Student - Check Status & Update",
    "Student - Withdraw Draft Application",
    "Coordinator - Review Pending Applications",
    "Coordinator - Request Document Resubmission",
    "Coordinator - Approve Application",
    "Admin - Create New Exchange Program",
    "Admin - Manage Users & Roles",
    "Admin - View Analytics & Reports",
    "Admin - System Configuration",
    "Complete Application Lifecycle",
    "Multi-User Collaboration"
)

foreach ($video in $videos) {
    $sizeMB = [math]::Round($video.Length / 1MB, 2)
    $time = $video.LastWriteTime.ToString("hh:mm:ss tt")
    
    if ($demoNumber -le $demoNames.Count) {
        Write-Host "   Demo $demoNumber`: $($demoNames[$demoNumber - 1])" -ForegroundColor Cyan
        Write-Host "      File: $($video.Name)" -ForegroundColor Gray
        Write-Host "      Size: $sizeMB MB | Created: $time" -ForegroundColor Gray
        Write-Host ""
        $demoNumber++
    } else {
        Write-Host "   Extra: $($video.Name) ($sizeMB MB, $time)" -ForegroundColor Yellow
    }
}

Write-Host "`n💡 Tips:" -ForegroundColor Yellow
Write-Host "   • Use VLC Media Player for best WebM compatibility" -ForegroundColor White
Write-Host "   • Videos are silent (no audio)" -ForegroundColor White
Write-Host "   • Check VIDEO_REVIEW_CHECKLIST.md for detailed review guide" -ForegroundColor White
Write-Host ""

# Ask if user wants to open the folder
$openFolder = Read-Host "Open videos folder? (Y/N)"
if ($openFolder -eq "Y" -or $openFolder -eq "y") {
    Write-Host "`n📂 Opening videos folder..." -ForegroundColor Green
    Start-Process explorer.exe -ArgumentList (Resolve-Path $videosPath)
}

Write-Host "`n✅ Ready for review!" -ForegroundColor Green
Write-Host ""

