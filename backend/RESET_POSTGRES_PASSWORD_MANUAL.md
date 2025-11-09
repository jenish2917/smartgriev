# Manual PostgreSQL Password Reset

## Step 1: Open Services
1. Press `Win + R`
2. Type `services.msc` and press Enter
3. Find **postgresql-x64-15** in the list
4. Right-click → **Stop**

## Step 2: Edit Configuration File
1. Open File Explorer
2. Navigate to: `C:\Program Files\PostgreSQL\15\data`
3. Right-click `pg_hba.conf` → Open with → Notepad (Run as Administrator)
4. Find these two lines (around line 87-89):
   ```
   host    all             all             127.0.0.1/32            scram-sha-256
   host    all             all             ::1/128                 scram-sha-256
   ```
5. Change **both** `scram-sha-256` to `trust`
6. Save and close

## Step 3: Start PostgreSQL
1. Go back to Services (services.msc)
2. Find **postgresql-x64-15**
3. Right-click → **Start**
4. Wait 5 seconds

## Step 4: Reset Password (Run in Admin PowerShell)
```powershell
cd d:\SmartGriev\backend
$env:PGPASSWORD=""
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -h localhost -c "ALTER USER postgres WITH PASSWORD 'smartgriev2025';"
```

## Step 5: Restore Security
1. Go back to Notepad with `pg_hba.conf`
2. Change **both** `trust` back to `scram-sha-256`
3. Save and close

## Step 6: Restart PostgreSQL
1. Go back to Services (services.msc)
2. Find **postgresql-x64-15**
3. Right-click → **Restart**

## Step 7: Test Connection
```powershell
$env:PGPASSWORD="smartgriev2025"
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -h localhost -c "SELECT version();"
```

If this works, you'll see PostgreSQL version info!

---

**Your new password is: smartgriev2025**
**Username: postgres**
**Host: localhost**
**Port: 5432**
