# 📊 Logging & Auto-Login System

**Complete logging system with automatic daily login checking**

---

## 🎯 What's New

### ✅ Automatic Daily Login Check
- App auto-checks MongoDB on every session start
- If user logged in **today**, skips login page → goes to Strategy Selection
- If **no login today**, shows login page

### ✅ Comprehensive Logging
- **Every action logged** to both file and console
- Logs for:
  - Application start/stop
  - Login attempts (success/failure)
  - MongoDB operations
  - Odin authentication
  - Strategy selection/configuration
  - Data saves
  - Errors and exceptions

### ✅ Log Files
- Location: `logs/` directory
- Format: `app_YYYY-mm-dd.log`
- Each day gets a new log file
- Rotates: Max 5 files, 10MB each

---

## 📝 Auto-Login Flow

```
User Opens App
    ↓
🔍 Auto-Check Session Startup
    ├─ Connect to MongoDB
    ├─ Check if today's login exists for any user
    └─ Clear login_checked flag
    
IF login_checked = False:
    ↓
    ⏳ Performing Automatic Login Check
    ├─ Connect to MongoDB OdinApp database
    ├─ Verify connection
    └─ Mark check as complete
    
✅ Auto-Check Complete
    ↓
Show Home Page
    ├─ Not Logged In:
    │  └─ Show login message
    │     └─ User clicks "Login" → Login Page
    │        ├─ Check MongoDB for today's login
    │        ├─ If found: Use cached session → Strategy Selection
    │        └─ If not found: Show login form
    │
    └─ Logged In:
       └─ Show dashboard
          └─ User navigates to strategies
```

---

## 📂 Logs Directory Structure

```
logs/
├── app_2026-03-07.log     # Today's logs
├── app_2026-03-06.log     # Yesterday's logs
├── app_2026-03-05.log
├── app_2026-03-04.log
└── app_2026-03-03.log     # Auto-deletes after 5 days
```

---

## 🔍 Log Format

Each log entry contains:

```
2026-03-07 10:30:45 - module_name - DEBUG - [function_name:line_number] - Log message
2026-03-07 10:30:45 - app - INFO - [<module>:0] - 🚀 Odin Trading Platform - Application Started
2026-03-07 10:30:46 - app - INFO - [__init__:64] - 🔍 Auto-login check status: Not yet performed
2026-03-07 10:31:00 - pages.1_Login - INFO - [<module>:17] - 📄 LOGIN PAGE LOADED
2026-03-07 10:31:05 - pages.1_Login - INFO - [<module>:37] - 🔑 Retrieving secrets from configuration...
2026-03-07 10:31:05 - pages.1_Login - INFO - [<module>:41] - ✅ All secrets retrieved successfully
2026-03-07 10:31:06 - modules.logging_config - INFO - [get_mongo_handler:44] - 🔗 Initializing MongoDB handler...
2026-03-07 10:31:07 - modules.mongodb_handler - INFO - [_connect:25] - ✅ MongoDB connection successful
2026-03-07 10:31:08 - pages.1_Login - DEBUG - [<module>:?] - 🔐 LOGIN ATTEMPT INITIATED
2026-03-07 10:31:08 - pages.1_Login - DEBUG - [<module>:?] - User ID: NR99
2026-03-07 10:31:09 - modules.mongodb_handler - INFO - [check_login_today:39] - 🔍 Checking login record for user NR99...
2026-03-07 10:31:09 - modules.mongodb_handler - INFO - [check_login_today:42] - 📅 Checking for login on date: 2026-Mar-07
2026-03-07 10:31:10 - modules.mongodb_handler - INFO - [check_login_today:51] - ✅ Login found TODAY for user NR99
2026-03-07 10:31:10 - pages.1_Login - INFO - [<module>:?] - ✅ Today's login FOUND for user NR99
2026-03-07 10:31:12 - pages.1_Login - INFO - [<module>:?] - 🚀 Redirecting user NR99 to Strategy Selection page
```

---

## 🎯 What Gets Logged

### Application Level
```
✅ App starts
✅ Page loads
✅ Session initialization
✅ User logout
```

### Login Level
```
✅ Login page loaded
✅ Secrets retrieved
✅ Login form displayed
✅ Login button clicked
✅ MongoDB checked for daily login
✅ Odin API called
✅ Login success/failure
✅ Data saved to MongoDB
✅ Redirect to next page
```

### Database Level
```
✅ MongoDB connection start/success/failure
✅ Database queries
✅ Data inserts/updates
✅ Query results
```

### Odin API Level
```
✅ OdinAuth object creation
✅ TOTP generation
✅ API connection start
✅ API call made
✅ API response received
✅ Authentication success/failure
✅ Tenant ID assigned
```

### Strategy Selection Level
```
✅ Strategies loaded from MongoDB
✅ Strategy count
✅ Strategy names/IDs
✅ Strategy selected
✅ Configuration loaded
```

### Error Level
```
✅ Connection errors
✅ Authentication errors
✅ Database errors
✅ Exception stacktraces
```

---

## 📖 How to Read Logs

### Locating Your Logs
```bash
# Windows
dir logs\

# Mac/Linux
ls -la logs/
```

### View Current Day Logs
```bash
# Windows
type logs\app_2026-03-07.log

# Mac/Linux
cat logs/app_2026-03-07.log
```

### View Last 50 Lines
```bash
# Windows PowerShell
Get-Content logs\app_2026-03-07.log -Tail 50

# Mac/Linux
tail -50 logs/app_2026-03-07.log
```

### Follow Logs Live (watch streaming)
```bash
# Mac/Linux
tail -f logs/app_2026-03-07.log

# Windows PowerShell
Get-Content -Path logs\app_2026-03-07.log -Wait -Tail 0
```

### Search Logs for Errors
```bash
# Windows
findstr /I "ERROR" logs\app_2026-03-07.log

# Mac/Linux
grep -i "error" logs/app_2026-03-07.log
```

### Search for User Activity
```bash
# Find all logins for user NR99
findstr "NR99" logs\app_2026-03-07.log

# Find all failed attempts
findstr "FAILED" logs\app_2026-03-07.log

# Find all MongoDB operations
findstr "MongoDB" logs\app_2026-03-07.log
```

---

## 🔐 Log Levels Explained

| Level | Symbol | Used For | Example |
|---|---|---|---|
| **DEBUG** | 🐛 | Detailed debugging info | Variable values, function calls |
| **INFO** | ℹ️ | General information | Login success, data saved |
| **WARNING** | ⚠️ | Warning conditions | No login found, incomplete data |
| **ERROR** | ❌ | Error events | Connection failed, bad credentials |
| **CRITICAL** | 🚨 | Critical errors | System shutdown needed |

---

## 📊 Log Examples

### Successful Login on First Day
```
🚀 Odin Trading Platform - Application Started
🔐 Session State: Initializing as NOT logged in
🔍 Auto-login check status: Not yet performed
========================================
📄 LOGIN PAGE LOADED
🔑 Retrieving secrets from configuration...
✅ All secrets retrieved successfully
🔗 Initializing MongoDB handler...
✅ MongoDB handler initialized successfully
📝 Displaying login form
🔐 LOGIN ATTEMPT INITIATED
User ID: NR99
🔍 **STEP 1:** Checking MongoDB for today's login...
📊 MongoDB check result: Login exists today = False
⚠️ No login found today for user NR99 - proceeding with Odin authentication
🔐 **STEP 2:** Authenticating with Odin platform...
🔑 OdinAuth object created for user NR99
🔢 Generating TOTP...
✅ TOTP generated: 123456
🔗 Initializing IBTConnect with API URL: ...
✅ IBTConnect initialized
🔓 Calling Odin login API for user NR99...
📡 Odin API response received
✅ Odin authentication SUCCESSFUL for user NR99
💾 **STEP 3:** Saving login to MongoDB...
💾 MongoDB save result: True
✅ Login SUCCESSFULLY saved to MongoDB for user NR99
📝 Session state updated - All fields set for user NR99
🚀 Login complete - Redirecting user NR99 to Strategy Selection
```

### Successful Login on Same Day (Using Cache)
```
🚀 Odin Trading Platform - Application Started
🔍 Auto-login check status: Not yet performed
========================================
📄 LOGIN PAGE LOADED
✅ All secrets retrieved successfully
✅ MongoDB handler initialized successfully
📝 Displaying login form
🔐 LOGIN ATTEMPT INITIATED
User ID: NR99
🔍 **STEP 1:** Checking MongoDB for today's login...
📊 MongoDB check result: Login exists today = True
✅ Today's login FOUND for user NR99 - using cached session
📝 Session state updated - logged_in=True, user_id=NR99
✅ Cached login data loaded for user NR99
✅ Last refresh timestamp set: 2026-03-07 14:45:30
🚀 Redirecting user NR99 to Strategy Selection page
```

### Failed Authentication
```
🔐 LOGIN ATTEMPT INITIATED
User ID: NR99
🔍 **STEP 1:** Checking MongoDB for today's login...
📊 MongoDB check result: Login exists today = False
⚠️ No login found today for user NR99
🔐 **STEP 2:** Authenticating with Odin platform...
🔑 OdinAuth object created for user NR99
🔢 Generating TOTP...
✅ TOTP generated: 654321
🔗 Initializing IBTConnect...
✅ IBTConnect initialized
🔓 Calling Odin login API for user NR99...
📡 Odin API response received
❌ Odin authentication FAILED for user NR99: Invalid credentials
```

### MongoDB Connection Error
```
🔑 Retrieving secrets from configuration...
✅ All secrets retrieved successfully
🔗 Initializing MongoDB handler...
❌ MongoDB connection failed: [Errno -2] Name or service not known
```

---

##🛠️ Logging Configuration

**File:** `modules/logging_config.py`

**Settings:**
- Log file location: `logs/` directory
- Log rotation: 5 MB per file, max 5 files
- Format: `YYYY-MM-DD HH:MM:SS - MODULE - LEVEL - [FUNCTION:LINE] - MESSAGE`
- Console output: INFO+ level
- File output: DEBUG+ level (all details)

**Customize Logging:**

Edit `modules/logging_config.py`:

```python
# Change log file size
maxBytes=10*1024*1024,  # 10 MB → Change to your preferred size

# Change number of backup files
backupCount=5,  # Max 5 → Change to your preferred count

# Change log level
console_handler.setLevel(logging.INFO)  # Change to DEBUG for more detail
file_handler.setLevel(logging.DEBUG)
```

---

## 🔄 Auto-Login Feature

**How it Works:**

1. **Every time the app starts**:
   - Check if `login_checked` flag is False
   - If False, initialize MongoDB connection
   - Set `login_checked` to True
   - System is ready

2. **When user tries to login**:
   - Connect to MongoDB OdinApp database
   - Search for login record matching today's date
   - If found: Use cached session (instant login ✅)
   - If not found: Show login form (ask for credentials)

3. **After login**:
   - Save login response to MongoDB
   - Use cached version for rest of day
   - Tomorrow, ask for credentials again

**Benefits:**
- ✅ Faster login (no Odin API call if already logged in)
- ✅ Server load reduction
- ✅ Better user experience
- ✅ Automatic daily security reset

---

## 📋 Log Cleanup

Logs auto-cleanup:
- Keeps max 5 log files
- Each file max 10 MB
- Files older than 5 days auto-deleted
- No manual cleanup needed

---

## 🐛 Troubleshooting with Logs

### "Login keeps failing"
Search logs for:
```bash
findstr "FAILED" logs\app_*.log
findstr "ERROR" logs\app_*.log
```

### "Can't connect to MongoDB"
Look for:
```bash
findstr "MongoDB connection" logs\app_*.log
findstr "connection timeout" logs\app_*.log
```

### "User not found in strategy selection"
Search for:
```bash
findstr "get_user_strategies" logs\app_*.log
findstr "strategies" logs\app_*.log
```

### "App crashes"
Look for:
```bash
findstr "EXCEPTION" logs\app_*.log
findstr "Traceback" logs\app_*.log
```

---

## 📊 Log Analysis

### Count login attempts for a user
```bash
findstr /C:"NR99" logs\app_2026-03-07.log | find /C "LOGIN ATTEMPT"
```

### Find all successful logins
```bash
findstr "authentication SUCCESSFUL" logs\app_2026-03-07.log
```

### Find all database operations
```bash
findstr "MongoDB" logs\app_2026-03-07.log
```

### Count errors for the day
```bash
findstr /C:"ERROR" logs\app_2026-03-07.log | find /C /V "?"
```

---

## ✅ Verification Checklist

- [x] Logging module created (`modules/logging_config.py`)
- [x] All pages have logging imports
- [x] Login page logs all steps
- [x] MongoDB handler logs operations
- [x] Odin auth logs authentication
- [x] Auto-login check implemented
- [x] Auto-redirect to strategy selection (if logged in today)
- [x] Logs saved to `logs/` directory
- [x] Log rotation configured
- [x] Console and file logging working

---

## 🚀 Next Steps

1. **Start the app**:
   ```bash
   streamlit run app.py
   ```

2. **Try logging in** - Check logs for detailed information

3. **View logs**:
   ```bash
   # Windows
   Get-Content logs\app_2026-03-07.log -Tail 20
   
   # Mac/Linux
   tail -20 logs/app_2026-03-07.log
   ```

4. **Test auto-login** - Refresh browser, should skip login page

5. **Monitor logs** - Watch real-time logs while testing:
   ```bash
   # Mac/Linux
   tail -f logs/app_2026-03-07.log
   
   # Windows PowerShell
   Get-Content logs\app_2026-03-07.log -Wait
   ```

---

## 📞 Support

**Find logs at:** `d:\LoginClientCodex\logs\`

**Current logs:** `logs\app_YYYY-MM-DD.log`

**All logs include:**
- Timestamp
- Module name
- Log level
- Function name and line number
- Detailed message

---

**Complete logging system implemented! 🎉**

Every action is logged. Monitor your system in real-time!
