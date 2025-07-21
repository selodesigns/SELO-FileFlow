# PowerShell script to set up SELO FileFlow as a file watcher service
# This creates a scheduled task that runs whenever a new file is created in the downloads folder

$taskName = "SELOFileFlow"
$pythonExe = "python"
$workingDir = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$configPath = Join-Path $workingDir "config\settings.yaml"
$downloadDir = [Environment]::GetFolderPath("UserProfile") + "\Downloads"
$useUI = $true # Set to $true to use the graphical interface, $false to use command-line version

# Try to read the config file to get the download directory
try {
    $configContent = Get-Content -Path $configPath -Raw
    # Simple regex parsing to extract source_directory since powershell-yaml might not be available
    if ($configContent -match "source_directory:\s*(.+)\s*") {
        $sourceDir = $matches[1].Trim() -replace '~', $env:USERPROFILE
        if ($sourceDir -match '^[A-Za-z]:\\') {
            # It's already an absolute path
            $downloadDir = $sourceDir
        }
    }
} catch {
    Write-Warning "Could not parse configuration. Using default Downloads folder: $downloadDir"
}

Write-Host "Setting up FileFlow as a file-triggered service..."
Write-Host "Monitoring directory: $downloadDir"

# Create the scheduled task action
if ($useUI) {
    # UI version with minimized flag
    $taskAction = New-ScheduledTaskAction -Execute $pythonExe -Argument "run_organizer.py --ui --minimized --config `"$configPath`"" -WorkingDirectory $workingDir
} else {
    # CLI version with process-once flag
    $taskAction = New-ScheduledTaskAction -Execute $pythonExe -Argument "run_organizer.py --process-once --config `"$configPath`"" -WorkingDirectory $workingDir
}

# Create task settings
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Use a simple trigger that runs periodically to check for new files
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    # Update existing task
    Set-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $trigger -Settings $settings
    Write-Host "Updated existing scheduled task: $taskName"
} else {
    # Create new task
    Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $trigger -Settings $settings -Description "Automatically organizes downloaded files into appropriate folders"
    Write-Host "Created new scheduled task: $taskName"
}

Write-Host "Service setup complete! FileFlow will run automatically at logon."
Write-Host "You can manually start it now by running: Start-ScheduledTask -TaskName $taskName"
