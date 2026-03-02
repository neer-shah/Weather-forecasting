Write-Host "Starting backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
cd backend;
.\venv\Scripts\Activate.ps1;
uvicorn main:app --reload
"

Start-Sleep -Seconds 3

Write-Host "Starting frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
cd frontend;
npm run dev
"

Start-Sleep -Seconds 5

Write-Host "Opening browser..."
Start-Process "http://localhost:3000"