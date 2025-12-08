# LAYER 5 DASHBOARD - SIMPLIFIED IMPLEMENTATION PLAN
## Two-Role System: Admin Dashboard + User Dashboard

---

## 1. USER ROLES

```yaml
ROLE 1: ADMIN (Internal Team)
  Access:
    - National indicators with charts
    - All business operational indicators (by industry)
    - All business insights (for all companies)
    - System health monitoring
  
  Use Case:
    - Monitor entire system
    - View economic/political indicators
    - Analyze industry trends
    - Review insights for any business

ROLE 2: USER (Business Clients)
  Access:
    - Own company profile management
    - Own business insights only
    - Own operational indicators only
    - Own alerts/notifications
  
  Use Case:
    - Enter business details
    - View personalized insights
    - Get risk/opportunity alerts
    - Generate reports for their business
```

---

## 2. ADMIN DASHBOARD COMPONENTS

### **Page 1: National Indicators Overview**

**What to Display:**
```yaml
Layout:
  - 20 National Indicators in cards
  - Each card shows:
    * Indicator name
    * Current value (0-100)
    * Trend arrow (↑↓→)
    * Visual gauge or progress bar
    * Icon representing category

Categories:
  Political (5 indicators):
    - Political Stability Index
    - Government Effectiveness
    - Policy Consistency
    - Regulatory Quality
    - Public Protests Level
  
  Economic (5 indicators):
    - Economic Health Index
    - Inflation Pressure
    - Currency Stability
    - Import Dependency
    - Business Confidence
  
  Social (5 indicators):
    - Social Unrest Index
    - Public Mood
    - Labor Market Health
    - Education Quality
    - Healthcare Access
  
  Infrastructure (5 indicators):
    - Transport Reliability
    - Power Availability
    - Communication Infrastructure
    - Supply Chain Health
    - Port/Customs Efficiency

Display Format:
  Card Example:
    ┌─────────────────────────┐
    │ 📊 Political Stability  │
    │                         │
    │     [Gauge: 72/100]     │
    │         GOOD ✅         │
    │      ↑ +3 this week     │
    └─────────────────────────┘

Chart Types:
  - Gauge charts for current values
  - Line charts for trends (last 30 days)
  - Color coding: Green (>70), Yellow (40-70), Red (<40)
```

**Data Source:**
```
Table: national_indicators
API: GET /api/admin/national-indicators
```

---

### **Page 2: Business Operations Indicators (All Industries)**

**What to Display:**
```yaml
Industry View:
  Filter by: [All Industries ▼] [Retail] [Manufacturing] [Logistics] etc.
  
  For each industry, show operational indicators:
  
  Example - Retail Industry:
    ┌─────────────────────────────────────┐
    │ Retail Industry - 45 businesses     │
    ├─────────────────────────────────────┤
    │ Supply Chain Health:      78/100 ✅ │
    │ Consumer Demand:          65/100 ⚠️ │
    │ Workforce Readiness:      82/100 ✅ │
    │ Financial Stability:      71/100 ✅ │
    │ Operational Readiness:    74/100 ✅ │
    └─────────────────────────────────────┘
  
  Drill-down:
    Click industry → See individual companies
    Click company → See their full dashboard

Aggregation:
  - Average indicators across all companies in industry
  - Show distribution (how many good vs poor)
  - Highlight outliers (companies doing very well/poorly)
```

**Data Source:**
```
Table: operational_indicator_values
  - Filtered by company.industry
  - Aggregated by industry

API: GET /api/admin/industry-indicators?industry={name}
```

---

### **Page 3: Business Insights (All Companies)**

**What to Display:**
```yaml
Company List View:
  ┌──────────────┬────────────┬──────────┬───────────┐
  │ Company      │ Industry   │ Risks    │ Health    │
  ├──────────────┼────────────┼──────────┼───────────┤
  │ ABC Retail   │ Retail     │ 2 High   │ 72 GOOD   │
  │ XYZ Mfg      │ Manufact.  │ 1 Crit.  │ 58 FAIR   │
  │ LMN Logistics│ Logistics  │ 0 Critical│ 85 EXCEL  │
  └──────────────┴────────────┴──────────┴───────────┘

Click Company → Full Insight View:
  - All risks for that company
  - All opportunities
  - Operational indicators
  - Recent alerts
  - Recommendations

Filters:
  - By industry
  - By risk level (show only critical)
  - By health score (show struggling companies)
```

**Data Source:**
```
Table: business_insights
  - Join with companies table
  - Filter by company_id

API: GET /api/admin/all-insights
API: GET /api/admin/company-insights/:company_id
```

---

## 3. USER (BUSINESS CLIENT) DASHBOARD COMPONENTS

### **Page 1: Company Profile Entry**

**What to Collect:**
```yaml
Form Fields:
  Basic Info:
    - Company Name
    - Industry (dropdown)
    - Business Scale (Micro/Small/Medium/Large)
    - Location (Province + City)
    - Number of Employees
  
  Operational Profile:
    - Import Dependency (0-100% slider)
    - Fuel Dependency (Critical/High/Medium/Low)
    - Workforce Location (checkboxes for provinces)
    - Customer Base (B2C/B2B/Export/Government)
  
  Risk Sensitivity:
    - Currency Sensitivity (1-10 scale)
    - Power Cut Impact (Critical/High/Medium/Low)
    - Political Stability Impact (High/Medium/Low)

Storage:
  Table: companies
    - company_id (PK)
    - user_id (FK to users table)
    - company_name
    - industry
    - profile_data (JSONB)
    - created_at
    - updated_at

API: POST /api/user/company/profile
```

---

### **Page 2: Business Health Dashboard**

**What to Display:**
```yaml
Health Score Card:
  ┌─────────────────────────────┐
  │  Overall Health Score       │
  │      [Gauge: 72/100]        │
  │         GOOD ✅             │
  │    ↓ -5 from last week      │
  └─────────────────────────────┘

Operational Indicators:
  - Supply Chain Health: 85/100 ✅
  - Workforce Readiness: 68/100 ⚠️
  - Financial Stability: 74/100 ✅
  - Operational Readiness: 71/100 ✅
  - Market Conditions: 65/100 ⚠️

Recent Insights Feed:
  🔴 CRITICAL | 2 hours ago
  Fuel shortage expected - affects deliveries
  [View Details] [Take Action]
  
  ⚠️ HIGH | 5 hours ago
  Currency depreciation accelerating
  [View Details]
  
  💡 OPPORTUNITY | 1 day ago
  New export tax incentive available
  [View Details]
```

**Data Source:**
```
Tables:
  - operational_indicator_values (where company_id = current_user.company_id)
  - business_insights (where company_id = current_user.company_id)

API: GET /api/user/dashboard/home
Response:
  {
    "health_score": 72,
    "indicators": [...],
    "recent_insights": [...],
    "active_alerts": 3
  }
```

---

### **Page 3: Risks & Opportunities**

**What to Display:**
```yaml
Risks Tab:
  Filter: [All] [Critical] [High] [Medium]
  
  Risk Cards:
    🔴 CRITICAL | Supply Chain Disruption
    Fuel shortage expected in Western Province
    Probability: 85% | Impact: Critical
    [View Full Analysis] [Recommendations]

Opportunities Tab:
  Filter: [All] [High Value] [Medium Value]
  
  Opportunity Cards:
    💡 HIGH VALUE | Export Tax Incentive
    Government tax breaks for exporters
    Potential Value: 8.5/10 | Feasibility: 75%
    [View Details] [I'm Interested]
```

**Data Source:**
```
Table: business_insights
  WHERE company_id = current_user.company_id
  AND type = 'risk' | 'opportunity'
  AND active = true

API: GET /api/user/risks
API: GET /api/user/opportunities
```

---

## 4. DATABASE SCHEMA

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'admin' or 'user'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Companies table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    company_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100),
    business_scale VARCHAR(50),
    location_province VARCHAR(100),
    location_city VARCHAR(100),
    num_employees INTEGER,
    profile_data JSONB,  -- All other profile fields
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- National indicators (from Layer 2)
CREATE TABLE national_indicators (
    id SERIAL PRIMARY KEY,
    indicator_name VARCHAR(100),
    category VARCHAR(50),  -- Political, Economic, Social, Infrastructure
    value FLOAT,  -- 0-100
    trend VARCHAR(10),  -- up, down, stable
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Operational indicators (from Layer 3)
CREATE TABLE operational_indicator_values (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    indicator_name VARCHAR(100),
    value FLOAT,  -- 0-100
    calculated_at TIMESTAMP DEFAULT NOW()
);

-- Business insights (from Layer 4)
CREATE TABLE business_insights (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id),
    type VARCHAR(50),  -- 'risk' or 'opportunity'
    severity VARCHAR(20),  -- critical, high, medium, low
    title VARCHAR(200),
    description TEXT,
    impact_score INTEGER,  -- 0-100
    probability INTEGER,  -- 0-100
    recommendations JSONB,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Dashboard access log
CREATE TABLE dashboard_access_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    page_accessed VARCHAR(100),
    accessed_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. API ENDPOINTS

### **Authentication APIs**

```yaml
POST /api/auth/login
  Body: {email, password}
  Response: {token, user: {id, email, role, company_id}}

POST /api/auth/register
  Body: {email, password, role}
  Response: {user_id, message}

GET /api/auth/me
  Headers: Authorization: Bearer {token}
  Response: {user: {id, email, role, company_id}}
```

---

### **Admin APIs**

```yaml
# National Indicators
GET /api/admin/national-indicators
  Response:
    {
      "indicators": [
        {
          "name": "Political Stability",
          "category": "Political",
          "value": 72,
          "trend": "up",
          "updated_at": "2025-12-08T10:00:00Z"
        }
      ]
    }

GET /api/admin/national-indicators/history
  Query: ?indicator={name}&days={30}
  Response: {data_points: [{date, value}]}

# Industry Indicators
GET /api/admin/industry-indicators
  Query: ?industry={name}
  Response:
    {
      "industry": "Retail",
      "company_count": 45,
      "avg_indicators": {
        "supply_chain_health": 78,
        "workforce_readiness": 82
      }
    }

# All Business Insights
GET /api/admin/all-insights
  Query: ?industry={name}&risk_level={critical}
  Response:
    {
      "insights": [
        {
          "company_id": 123,
          "company_name": "ABC Retail",
          "type": "risk",
          "severity": "high",
          "title": "...",
          "created_at": "..."
        }
      ]
    }

# Specific Company Insights
GET /api/admin/company-insights/:company_id
  Response: {company: {...}, insights: [...], indicators: [...]}
```

---

### **User APIs**

```yaml
# Company Profile
POST /api/user/company/profile
  Body:
    {
      "company_name": "ABC Retail",
      "industry": "Retail",
      "profile_data": {...}
    }
  Response: {company_id, message}

GET /api/user/company/profile
  Response: {company: {id, name, industry, profile_data}}

PUT /api/user/company/profile
  Body: {updated fields}
  Response: {success: true}

# Dashboard Home
GET /api/user/dashboard/home
  Response:
    {
      "health_score": 72,
      "indicators": [
        {"name": "Supply Chain", "value": 85, "trend": "up"}
      ],
      "recent_insights": [
        {"type": "risk", "severity": "critical", "title": "..."}
      ],
      "alert_count": 3
    }

# Risks
GET /api/user/risks
  Query: ?severity={critical}
  Response: {risks: [{id, title, severity, probability, impact}]}

GET /api/user/risks/:id
  Response: {risk: {full details, recommendations}}

# Opportunities
GET /api/user/opportunities
  Response: {opportunities: [{id, title, value, feasibility}]}

# Operational Indicators
GET /api/user/indicators
  Response:
    {
      "indicators": [
        {"name": "Supply Chain", "value": 85, "trend": "up"},
        {"name": "Workforce", "value": 68, "trend": "down"}
      ]
    }

GET /api/user/indicators/history
  Query: ?indicator={name}&days={30}
  Response: {data_points: [{date, value}]}
```

---

## 6. DATA FLOW ARCHITECTURE

```
┌─────────────────────────────────────────────────┐
│              LAYER 5: DASHBOARD                 │
│          (Frontend: React/Next.js)              │
└────────────┬────────────────────────────────────┘
             │
             │ HTTP Requests
             │
┌────────────▼────────────────────────────────────┐
│         API GATEWAY / BACKEND                   │
│         (FastAPI or Express.js)                 │
│                                                  │
│  ┌─────────────────────────────────────────┐   │
│  │  Authentication Middleware              │   │
│  │  - Verify JWT token                     │   │
│  │  - Check user role (admin/user)         │   │
│  │  - Attach user_id to request            │   │
│  └─────────────┬───────────────────────────┘   │
│                │                                 │
│  ┌─────────────▼───────────────────────────┐   │
│  │  Route Handlers                         │   │
│  │  - Admin routes (/api/admin/*)          │   │
│  │  - User routes (/api/user/*)            │   │
│  │  - Auth routes (/api/auth/*)            │   │
│  └─────────────┬───────────────────────────┘   │
│                │                                 │
│  ┌─────────────▼───────────────────────────┐   │
│  │  Business Logic Services                │   │
│  │  - IndicatorService                     │   │
│  │  - InsightService                       │   │
│  │  - CompanyService                       │   │
│  └─────────────┬───────────────────────────┘   │
└────────────────┼─────────────────────────────────┘
                 │
                 │ Database Queries
                 │
┌────────────────▼─────────────────────────────────┐
│           DATABASE LAYER                         │
│                                                   │
│  ┌──────────────────┐  ┌──────────────────┐     │
│  │   PostgreSQL     │  │    MongoDB       │     │
│  │                  │  │                  │     │
│  │ - users          │  │ - raw_articles   │     │
│  │ - companies      │  │ (Layer 1)        │     │
│  │ - national_ind.  │  │                  │     │
│  │   (Layer 2)      │  └──────────────────┘     │
│  │ - operational_   │                            │
│  │   indicators     │  ┌──────────────────┐     │
│  │   (Layer 3)      │  │     Redis        │     │
│  │ - business_      │  │                  │     │
│  │   insights       │  │ - Cache          │     │
│  │   (Layer 4)      │  │ - Sessions       │     │
│  └──────────────────┘  └──────────────────┘     │
└───────────────────────────────────────────────────┘
```

---

## 7. BACKEND CONFIGURATION

### **File Structure:**

```
layer5-backend/
├── server.py (or app.js)
├── config/
│   ├── database.py
│   ├── auth.py
│   └── settings.py
├── routes/
│   ├── admin_routes.py
│   ├── user_routes.py
│   └── auth_routes.py
├── services/
│   ├── indicator_service.py
│   ├── insight_service.py
│   └── company_service.py
├── middleware/
│   ├── auth_middleware.py
│   └── role_middleware.py
└── models/
    ├── user.py
    ├── company.py
    └── indicator.py
```

### **Configuration Settings:**

```yaml
# config/settings.py

DATABASE:
  host: localhost
  port: 5432
  name: bi_platform
  user: admin
  password: ${DB_PASSWORD}

JWT:
  secret_key: ${JWT_SECRET}
  algorithm: HS256
  expiry_hours: 24

API:
  host: 0.0.0.0
  port: 8000
  cors_origins:
    - http://localhost:3000
    - https://yourdashboard.com

REDIS:
  host: localhost
  port: 6379
  cache_ttl: 300  # 5 minutes
```

### **Authentication Middleware:**

```yaml
# Pseudo-code structure

def authenticate_request(request):
  1. Extract token from Authorization header
  2. Verify JWT token
  3. If valid:
     - Extract user_id and role
     - Attach to request.user
     - Continue to route handler
  4. If invalid:
     - Return 401 Unauthorized

def require_admin(request):
  1. Check if request.user.role == 'admin'
  2. If yes: Continue
  3. If no: Return 403 Forbidden

def require_user(request):
  1. Check if request.user.role == 'user'
  2. If yes: Continue
  3. If no: Return 403 Forbidden
```

---

## 8. DATA FETCHING & UPDATES

### **Admin Dashboard Data Flow:**

```yaml
National Indicators:
  Fetch From: national_indicators table (Layer 2 output)
  Update Frequency: Every 15 minutes (Layer 2 calculation)
  API Call: GET /api/admin/national-indicators
  Caching: Redis cache for 5 minutes
  
  Flow:
    1. Dashboard calls API
    2. Backend checks Redis cache
    3. If cache miss: Query PostgreSQL
    4. Return data to dashboard
    5. Dashboard updates charts

Industry Indicators:
  Fetch From: operational_indicator_values table (Layer 3 output)
  Aggregation: Group by industry, calculate averages
  API Call: GET /api/admin/industry-indicators?industry=Retail
  
  Flow:
    1. Dashboard selects industry
    2. Backend queries operational_indicator_values
    3. Filter by companies in that industry
    4. Calculate averages
    5. Return aggregated data

All Business Insights:
  Fetch From: business_insights table (Layer 4 output)
  Join With: companies table (for company names)
  API Call: GET /api/admin/all-insights
  
  Flow:
    1. Dashboard requests all insights
    2. Backend joins insights with companies
    3. Apply filters (industry, severity)
    4. Return paginated results
```

### **User Dashboard Data Flow:**

```yaml
Dashboard Home:
  Fetch From:
    - operational_indicator_values (WHERE company_id = user.company_id)
    - business_insights (WHERE company_id = user.company_id)
  
  API Call: GET /api/user/dashboard/home
  
  Flow:
    1. User logs in
    2. JWT token includes user_id
    3. Backend finds company_id from users table
    4. Query indicators for that company_id
    5. Query insights for that company_id
    6. Calculate health score from indicators
    7. Return complete dashboard data

Real-time Updates:
  Method: WebSocket or Polling
  
  WebSocket Flow:
    1. Dashboard connects to ws://backend/ws
    2. Send authentication token
    3. Backend subscribes to company-specific room
    4. When Layer 4 generates new insight:
       - Backend emits to that room
       - Dashboard receives event
       - Updates UI without refresh
  
  Polling Flow (simpler):
    1. Dashboard polls every 30 seconds
    2. Check for new insights
    3. Update if changes detected
```

---

## 9. LAYER INTEGRATION

### **How Layer 5 Connects to Other Layers:**

```
LAYER 1 (AI Agents - Data Collection)
    ↓
  Stores raw articles in PostgreSQL
    ↓
LAYER 2 (National Indicators)
    ↓
  Calculates 20 national indicators
  Stores in: national_indicators table
    ↓
LAYER 3 (Operational Indicators)
    ↓
  Takes national indicators + company profiles
  Calculates company-specific indicators
  Stores in: operational_indicator_values table
    ↓
LAYER 4 (Business Insights)
    ↓
  Takes operational indicators
  Generates risks & opportunities
  Stores in: business_insights table
    ↓
LAYER 5 (DASHBOARD) ← YOU ARE HERE
    ↓
  Reads from all tables:
  - national_indicators (for admin)
  - operational_indicator_values (for admin & users)
  - business_insights (for admin & users)
  - companies (for profiles)
```

### **Integration Requirements:**

```yaml
Layer 5 READS from:
  ✅ national_indicators (Layer 2 output)
  ✅ operational_indicator_values (Layer 3 output)
  ✅ business_insights (Layer 4 output)
  ✅ companies (Layer 5 manages this)

Layer 5 WRITES to:
  ✅ users (authentication)
  ✅ companies (profile management)
  ✅ dashboard_access_log (analytics)

Layer 5 does NOT modify:
  ❌ raw_articles (Layer 1 owns)
  ❌ processed_articles (Layer 2 owns)
  ❌ national_indicators (Layer 2 calculates)
  ❌ operational_indicator_values (Layer 3 calculates)
  ❌ business_insights (Layer 4 generates)

Database Access:
  - Same PostgreSQL instance as Layers 1-4
  - Read-only access to Layer 1-4 tables
  - Full access to Layer 5 tables (users, companies)
```

### **Simple Connection Steps:**

```yaml
1. Database Connection:
   - Use same connection string as Layers 1-4
   - Layer 5 backend connects to PostgreSQL
   - No changes needed to existing tables

2. Data Access:
   - Layer 5 queries existing tables directly
   - No API calls between layers needed
   - All layers share same database

3. Real-time Updates:
   - Option A: Polling (simple)
     * Dashboard checks for new data every 30s
   
   - Option B: Database triggers (advanced)
     * When Layer 4 inserts new insight
     * Trigger sends notification
     * Dashboard receives and updates

4. Testing Integration:
   - Run Layers 1-4 to generate data
   - Verify data in tables
   - Start Layer 5 backend
   - Dashboard should display the data
```

---

## 10. IMPLEMENTATION CHECKLIST

```yaml
Week 1: Setup
  ☐ Set up React/Next.js frontend
  ☐ Set up FastAPI/Express backend
  ☐ Configure database connection (same DB as Layers 1-4)
  ☐ Create users and companies tables
  ☐ Implement JWT authentication

Week 2: Admin Dashboard
  ☐ Build national indicators page
  ☐ Build industry indicators page
  ☐ Build all business insights page
  ☐ Implement admin APIs
  ☐ Test with real Layer 2-4 data

Week 3: User Dashboard
  ☐ Build company profile form
  ☐ Build dashboard home page
  ☐ Build risks & opportunities pages
  ☐ Implement user APIs
  ☐ Test end-to-end user flow

Week 4: Integration & Polish
  ☐ Connect to real-time updates
  ☐ Add charts and visualizations
  ☐ Implement caching (Redis)
  ☐ Performance optimization
  ☐ Security testing
  ☐ Deploy to production
```

---

**END OF DOCUMENT**

**Layer 5 is now fully specified with clear instructions for:**
- ✅ 2 roles (Admin & User)
- ✅ All dashboard components
- ✅ Complete API endpoints
- ✅ Database schemas
- ✅ Data flow architecture
- ✅ Integration with Layers 1-4

**AI coding agent can now build the entire dashboard system following these instructions!** 🚀
