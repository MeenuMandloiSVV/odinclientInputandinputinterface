# MongoDB Schema & Structure

Complete MongoDB setup guide for the Odin Trading Platform

---

## 📊 Database Architecture

```
[OdinApp Database]
├── User_Login_Response Collection
│   └── Stores login cache (auto-created)
│
[UserID Databases] (e.g., NR99, NR100, etc.)
├── Selected_Strategies_Inputs Collection
│   └── User's strategy configurations
│
└── [Future Collections for other data]
```

---

## 🔐 OdinApp Database

### Collection: `User_Login_Response`

**Purpose:** Cache login responses to skip re-login for same-day access

**Auto-created on first login**

**Example Document:**
```json
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "data": {
    "user_id": "NR99",
    "tenant_id": "TENANT_123",
    "login_time": "2024-Mar-07 09:30:00",
    "session_token": "abc123xyz",
    "account_info": {
      "balance": 100000,
      "margin_used": 25000
    }
  }
}
```

---

## 👤 User Database

### Database Name: Same as User ID

**Examples:**
- User NR99 → Database name: `NR99`
- User NR100 → Database name: `NR100`
- User AGENT_001 → Database name: `AGENT_001`

### Collection: `Selected_Strategies_Inputs`

**Purpose:** Store user's strategy configurations

**Documents are identified by StrategyID**

---

## 📋 Strategy Documents

### Straddle Shift (CST0005)

```json
{
  "_id": ObjectId("507f191e810c19729de860ea"),
  "StrategyID": "CST0005",
  "min_time": "09:15:00",
  "max_time": "15:30:00",
  "start_time": "09:15:00",
  "end_time": "15:15:00",
  "qty_per_leg": 100,
  "premium_threshold": 5.0,
  "enabled": true,
  "created_at": ISODate("2024-03-01T09:15:00.000Z"),
  "updated_at": ISODate("2024-03-07T10:30:00.000Z")
}
```

**Fields:**
| Field | Type | Description | Default |
|---|---|---|---|
| StrategyID | String | Strategy identifier | CST0005 |
| min_time | String | Market opening time | 09:15:00 |
| max_time | String | Market closing time | 15:30:00 |
| start_time | String | Strategy start time | 09:15:00 |
| end_time | String | Strategy end time | 15:15:00 |
| qty_per_leg | Number | Quantity per leg | 100 |
| premium_threshold | Number | Premium threshold % | 5.0 |
| enabled | Boolean | Enable strategy | true |
| created_at | Date | Creation timestamp | Auto |
| updated_at | Date | Last update timestamp | Auto |

---

### ATP Strategy (CST0003)

```json
{
  "_id": ObjectId("507f191e810c19729de860eb"),
  "StrategyID": "CST0003",
  "min_time": "09:15:00",
  "max_time": "15:30:00",
  "qty_per_trade": 50,
  "profit_target": 2.0,
  "stop_loss": 1.0,
  "enabled": true,
  "created_at": ISODate("2024-03-01T09:15:00.000Z"),
  "updated_at": ISODate("2024-03-07T10:30:00.000Z")
}
```

**Fields:**
| Field | Type | Description | Default |
|---|---|---|---|
| StrategyID | String | Strategy identifier | CST0003 |
| min_time | String | Market opening time | 09:15:00 |
| max_time | String | Market closing time | 15:30:00 |
| qty_per_trade | Number | Qty per trade | 50 |
| profit_target | Number | Profit target % | 2.0 |
| stop_loss | Number | Stop loss % | 1.0 |
| enabled | Boolean | Enable strategy | true |
| created_at | Date | Creation timestamp | Auto |
| updated_at | Date | Last update timestamp | Auto |

---

### Cash Profit Loop (CST0007)

```json
{
  "_id": ObjectId("507f191e810c19729de860ec"),
  "StrategyID": "CST0007",
  "min_time": "09:15:00",
  "max_time": "15:30:00",
  "lot_size": 1,
  "profit_target": 5000,
  "enabled": true,
  "created_at": ISODate("2024-03-01T09:15:00.000Z"),
  "updated_at": ISODate("2024-03-07T10:30:00.000Z")
}
```

**Fields:**
| Field | Type | Description | Default |
|---|---|---|---|
| StrategyID | String | Strategy identifier | CST0007 |
| min_time | String | Market opening time | 09:15:00 |
| max_time | String | Market closing time | 15:30:00 |
| lot_size | Number | Lot size | 1 |
| profit_target | Number | Daily profit target (₹) | 5000 |
| enabled | Boolean | Enable strategy | true |
| created_at | Date | Creation timestamp | Auto |
| updated_at | Date | Last update timestamp | Auto |

---

## 🔍 MongoDB Queries

### Find all strategies for a user

```javascript
db.getDb("NR99").getCollection("Selected_Strategies_Inputs").find({})
```

### Find a specific strategy

```javascript
db.getDb("NR99").getCollection("Selected_Strategies_Inputs").find({"StrategyID": "CST0005"})
```

### Update a strategy

```javascript
db.getDb("NR99").getCollection("Selected_Strategies_Inputs").updateOne(
  {"StrategyID": "CST0005"},
  {$set: {"qty_per_leg": 200, "updated_at": new Date()}}
)
```

### Check login for a user

```javascript
db.getDb("OdinApp").getCollection("User_Login_Response").find({"data.user_id": "NR99"})
```

---

## 🚀 MongoDB Setup Instructions

### 1. Create OdinApp Database

```javascript
use OdinApp
db.createCollection("User_Login_Response")
```

### 2. Create User Database & Collection

```javascript
use NR99  // Create database with user ID as name
db.createCollection("Selected_Strategies_Inputs")
```

### 3. Insert Initial Strategy Documents

```javascript
use NR99

db.Selected_Strategies_Inputs.insertMany([
  {
    "StrategyID": "CST0005",
    "min_time": "09:15:00",
    "max_time": "15:30:00",
    "start_time": "09:15:00",
    "end_time": "15:15:00",
    "qty_per_leg": 100,
    "premium_threshold": 5.0,
    "enabled": true,
    "created_at": new Date(),
    "updated_at": new Date()
  },
  {
    "StrategyID": "CST0003",
    "min_time": "09:15:00",
    "max_time": "15:30:00",
    "qty_per_trade": 50,
    "profit_target": 2.0,
    "stop_loss": 1.0,
    "enabled": true,
    "created_at": new Date(),
    "updated_at": new Date()
  }
])
```

### 4. Verify Records Created

```javascript
db.Selected_Strategies_Inputs.find().pretty()
```

---

## 📈 Indexing (Optional but Recommended)

Add indexes for faster queries:

```javascript
use OdinApp
db.User_Login_Response.createIndex({"data.user_id": 1})
db.User_Login_Response.createIndex({"data.login_time": 1})

use NR99
db.Selected_Strategies_Inputs.createIndex({"StrategyID": 1})
```

---

## 🔄 Data Flow

```
Step 1: User Login
├─ Check OdinApp.User_Login_Response for today's login
└─ If not found → Authenticate with Odin → Save response

Step 2: Strategy Selection
├─ Read from {UserID}.Selected_Strategies_Inputs
└─ Get all documents with StrategyID field

Step 3: Strategy Configuration
├─ Find document matching selected StrategyID
└─ Load existing values
└─ User edits and saves
└─ Update document in MongoDB
```

---

## 🔐 Backup & Maintenance

### Export User Data

```bash
mongoexport --uri "mongodb+srv://user:pass@cluster.mongodb.net/NR99" \
  --collection Selected_Strategies_Inputs \
  --out NR99_backup.json
```

### Import User Data

```bash
mongoimport --uri "mongodb+srv://user:pass@cluster.mongodb.net/NR99" \
  --collection Selected_Strategies_Inputs \
  --file NR99_backup.json
```

---

## 📝 Adding New Users

For each new user (e.g., NR100):

1. Create database named after user ID: `NR100`
2. Create collection: `Selected_Strategies_Inputs`
3. Insert strategy documents with `StrategyID` field
4. User logs in → System reads from this database

---

## 🎯 Best Practices

✅ **Do:**
- Use StrategyID as unique identifier in documents
- Include `updated_at` timestamp for audit trail
- Keep login cache in separate OdinApp database
- Use database name = user ID for easy lookup

❌ **Don't:**
- Store passwords in MongoDB
- Mix different users' data in one collection
- Change StrategyID after document creation
- Store sensitive tokens (only session IDs)

---

## 📊 Schema Validation (Optional)

Add MongoDB schema validation for data integrity:

```javascript
use NR99
db.createCollection("Selected_Strategies_Inputs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["StrategyID"],
      properties: {
        _id: { bsonType: "objectId" },
        StrategyID: { bsonType: "string" },
        enabled: { bsonType: "bool" },
        created_at: { bsonType: "date" },
        updated_at: { bsonType: "date" }
      }
    }
  }
})
```

---

## 🔗 References

- MongoDB documentation: https://docs.mongodb.com
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas
- Shell commands: https://docs.mongodb.com/mongodb-shell/

---

**Need help?** Check the main README.md or MongoDB documentation
