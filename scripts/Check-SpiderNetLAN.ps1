# Spider Net LAN diagnostic (read-only)
# Run in PowerShell on the Windows 11 laptop that may host Jellyfin.
# This script DOES NOT edit services, firewall, networking, registry, or MikroTik.
$ErrorActionPreference = 'SilentlyContinue'

Write-Host ''
Write-Host 'SPIDER NET - LAN DIAGNOSTIC (READ ONLY)' -ForegroundColor Cyan
Write-Host 'No settings will be changed. Do not paste passwords or tokens into reports.' -ForegroundColor Yellow
Write-Host ''

Write-Host '--- Network profiles ---' -ForegroundColor Cyan
try {
    Get-NetConnectionProfile |
        Select-Object Name, InterfaceAlias, NetworkCategory, IPv4Connectivity |
        Format-Table -AutoSize
} catch {
    Write-Host 'Could not query network profiles.' -ForegroundColor Yellow
}

Write-Host '--- Local IPv4 addresses (ignore APIPA 169.254.x.x) ---' -ForegroundColor Cyan
try {
    Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object {
            $_.IPAddress -notlike '127.*' -and
            $_.IPAddress -notlike '169.254.*' -and
            $_.AddressState -eq 'Preferred' -and
            -not $_.SkipAsSource
        } |
        Select-Object InterfaceAlias, IPAddress, PrefixLength, AddressState |
        Sort-Object InterfaceAlias, IPAddress |
        Format-Table -AutoSize
} catch {
    Write-Host 'Could not query IPv4 addresses.' -ForegroundColor Yellow
}

Write-Host '--- Jellyfin process/service ---' -ForegroundColor Cyan
$services = Get-Service -Name 'Jellyfin*'
if ($services) {
    $services | Select-Object Name, Status, StartType | Format-Table -AutoSize
} else {
    Write-Host 'No Jellyfin Windows service found. A tray-mode process may still be used, or Jellyfin may not be installed.' -ForegroundColor Yellow
}
$processes = Get-Process -Name 'jellyfin*'
if ($processes) {
    $processes | Select-Object Name, Id, CPU, WorkingSet64 | Format-Table -AutoSize
} else {
    Write-Host 'No Jellyfin process found.' -ForegroundColor Yellow
}

Write-Host '--- TCP listener on default port 8096 ---' -ForegroundColor Cyan
$listeners = Get-NetTCPConnection -State Listen -LocalPort 8096 |
    Select-Object LocalAddress, LocalPort, OwningProcess
if ($listeners) {
    $listeners | Sort-Object LocalAddress -Unique | Format-Table -AutoSize
} else {
    Write-Host 'Nothing is listening on TCP 8096. Jellyfin may be stopped or configured for another port.' -ForegroundColor Yellow
}

Write-Host '--- Local HTTP probe ---' -ForegroundColor Cyan
try {
    $reachable = Test-NetConnection -ComputerName '127.0.0.1' -Port 8096 -InformationLevel Quiet -WarningAction SilentlyContinue
    Write-Host ('127.0.0.1:8096 reachable: ' + [bool]$reachable)
} catch {
    Write-Host 'Could not perform the local port probe.' -ForegroundColor Yellow
}

Write-Host '--- Windows Firewall profile state (read-only) ---' -ForegroundColor Cyan
try {
    Get-NetFirewallProfile |
        Select-Object Name, Enabled, DefaultInboundAction |
        Format-Table -AutoSize
} catch {
    Write-Host 'Could not query Windows Firewall profiles.' -ForegroundColor Yellow
}

Write-Host ''
Write-Host 'Diagnostic finished. No configuration was modified.' -ForegroundColor Green
Write-Host 'For phone access, test from a device on the intended LAN; this script cannot prove VLAN routing or Wi-Fi client isolation.' -ForegroundColor Yellow
