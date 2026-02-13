# Q-Path Emergency Response Hub - Startup Script

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Q-Path Emergency Response Hub" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Dashboard:    http://localhost:5000" -ForegroundColor White
Write-Host "  Report Page:  http://localhost:5000/incident_report.html" -ForegroundColor White
Write-Host ""
Write-Host "Chatbot powered by Caramel AI is ready!" -ForegroundColor Magenta
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Start Flask application using the Python from venv
C:/Users/johan/Downloads/meow/.venv/Scripts/python.exe app.py
