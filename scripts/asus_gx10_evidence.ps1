param(
  [string]$BackendUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

$baseUrl = $BackendUrl.TrimEnd("/")
$demoPrompt = "Plan my UCLA week. I want to reduce carbon emissions, but I had an emergency and took an Uber today. I also have class from 10 to 2 and homework tonight."

Write-Host "ASUS GX10 / Local-first evidence check"
Write-Host "Backend: $baseUrl"
Write-Host ""

$status = Invoke-RestMethod -Uri "$baseUrl/api/runtime/status" -Method Get

Write-Host "Runtime status"
Write-Host "  runtime mode: $($status.runtime_mode)"
Write-Host "  GX10 enabled: $($status.gx10_enabled)"
Write-Host "  GX10 available: $($status.gx10_available)"
Write-Host "  fallback enabled: $($status.fallback_enabled)"
Write-Host "  backend label: $($status.backend_label)"
Write-Host ""

$body = @{
  prompt = $demoPrompt
} | ConvertTo-Json

$plan = Invoke-RestMethod -Uri "$baseUrl/api/plan" -Method POST -ContentType "application/json" -Body $body
$router = $plan.metadata.runtime_router

Write-Host "Plan check"
Write-Host "  planner mode: $($plan.metadata.planner_mode)"
Write-Host "  selected backend: $($router.selected_backend)"
Write-Host "  GX10 attempted: $($router.gx10_attempted)"
Write-Host "  failover used: $($router.failover_used)"
Write-Host "  plan blocks: $($plan.plan_blocks.Count)"
Write-Host ""
Write-Host "Evidence check complete."
