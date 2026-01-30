# Switch MCP Profile Script
# Switches the active MCP configuration to a specified profile

param(
    [Parameter(Mandatory=$true)]
    [string]$ProfileName
)

$ErrorActionPreference = "Stop"

# Define profile configurations
$profiles = @{
    "minimal" = @{
        "mcpServers" = @{
            "filesystem" = @{
                "command" = "npx"
                "args" = @("-y", "--package=@modelcontextprotocol/server-filesystem", "filesystem", $env:USERPROFILE)
            }
            "github" = @{
                "command" = "npx"
                "args" = @("-y", "--package=@modelcontextprotocol/server-github", "github")
                "env" = @{
                    "GITHUB_PERSONAL_ACCESS_TOKEN" = $env:GITHUB_PERSONAL_ACCESS_TOKEN
                }
            }
        }
    }
    "full" = @{
        "mcpServers" = @{
            "filesystem" = @{
                "command" = "npx"
                "args" = @("-y", "--package=@modelcontextprotocol/server-filesystem", "filesystem", $env:USERPROFILE)
            }
            "github" = @{
                "command" = "npx"
                "args" = @("-y", "--package=@modelcontextprotocol/server-github", "github")
                "env" = @{
                    "GITHUB_PERSONAL_ACCESS_TOKEN" = $env:GITHUB_PERSONAL_ACCESS_TOKEN
                }
            }
            "postgres" = @{
                "command" = "npx"
                "args" = @("-y", "--package=@modelcontextprotocol/server-postgres", "postgres")
                "env" = @{
                    "POSTGRES_CONNECTION_STRING" = $env:POSTGRES_CONNECTION_STRING
                }
            }
        }
    }
    "bmad" = @{
        "mcpServers" = @{
            "filesystem" = @{
                "command" = "npx"
                "args" = @("-y", "--package=@modelcontextprotocol/server-filesystem", "filesystem", $env:USERPROFILE)
            }
            "postgres" = @{
                "command" = "npx"
                "args" = @("-y", "--package=@modelcontextprotocol/server-postgres", "postgres")
                "env" = @{
                    "POSTGRES_CONNECTION_STRING" = $env:POSTGRES_CONNECTION_STRING
                }
            }
        }
    }
    "seim" = @{
        "mcpServers" = @{
            "filesystem" = @{
                "command" = "npx"
                "args" = @("-y", "--package=@modelcontextprotocol/server-filesystem", "filesystem", $env:USERPROFILE)
            }
        }
    }
}

# Paths
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$mcpConfigPath = Join-Path $projectRoot ".mcp.json"
$backupPath = Join-Path $projectRoot ".mcp.json.backup"

# Validate profile exists
if (-not $profiles.ContainsKey($ProfileName)) {
    Write-Host "❌ Error: Profile '$ProfileName' not found" -ForegroundColor Red
    Write-Host "Available profiles: $($profiles.Keys -join ', ')" -ForegroundColor Yellow
    exit 1
}

# Backup current configuration
if (Test-Path $mcpConfigPath) {
    Copy-Item $mcpConfigPath $backupPath -Force
    Write-Host "✅ Backed up current configuration to .mcp.json.backup" -ForegroundColor Green
}

# Get selected profile
$selectedProfile = $profiles[$ProfileName]

# Expand environment variables in profile
function Expand-EnvVars {
    param($obj)
    
    if ($obj -is [Hashtable]) {
        $result = @{}
        foreach ($key in $obj.Keys) {
            if ($key -eq "env" -and $obj[$key] -is [Hashtable]) {
                $result[$key] = @{}
                foreach ($envKey in $obj[$key].Keys) {
                    $envValue = $obj[$key][$envKey]
                    if ($envValue -match '\$\{env:(\w+)\}') {
                        $varName = $matches[1]
                        $result[$key][$envKey] = [Environment]::GetEnvironmentVariable($varName)
                    } else {
                        $result[$key][$envKey] = $envValue
                    }
                }
            } else {
                $result[$key] = Expand-EnvVars $obj[$key]
            }
        }
        return $result
    } elseif ($obj -is [Array]) {
        return $obj | ForEach-Object { Expand-EnvVars $_ }
    } else {
        return $obj
    }
}

$expandedProfile = Expand-EnvVars $selectedProfile

# Convert to JSON and write
$json = $expandedProfile | ConvertTo-Json -Depth 10
$json | Out-File -FilePath $mcpConfigPath -Encoding UTF8 -NoNewline

Write-Host "✅ Switched to '$ProfileName' profile" -ForegroundColor Green
Write-Host "📊 Active MCP servers: $($expandedProfile.mcpServers.Keys.Count)" -ForegroundColor Cyan
Write-Host "   Servers: $($expandedProfile.mcpServers.Keys -join ', ')" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  IMPORTANT: Restart Cursor IDE for changes to take effect" -ForegroundColor Yellow
