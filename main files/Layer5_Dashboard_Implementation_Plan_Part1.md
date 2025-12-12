# LAYER 5: INTELLIGENT DASHBOARD SYSTEM
## Comprehensive Implementation Plan - PART 1

---

## TABLE OF CONTENTS - PART 1

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Two-Iteration Development Strategy](#two-iteration-strategy)
4. [Dashboard Types & User Roles](#dashboard-types)
5. [Iteration 1: Fundamental Components](#iteration-1)
6. [Admin Dashboard - Complete Specification](#admin-dashboard)
7. [Business User Dashboard - Complete Specification](#business-user-dashboard)
8. [Data Flow & Integration](#data-flow)
9. [Technology Stack Recommendations](#tech-stack)

---

## 1. EXECUTIVE SUMMARY {#executive-summary}

### **Project Goal:**
Build a dual-purpose dashboard system:
1. **Admin Dashboard** - Monitor entire pipeline health, agent performance, system metrics
2. **Business Dashboard** - Display actionable business insights, risks, opportunities

### **Development Approach:**
- **Iteration 1** (7 days): Core functionality, essential features, working MVP
- **Iteration 2** (7 days): Advanced features, optimizations, polish

### **Key Requirements:**
- Real-time data updates
- High performance (load <2 seconds)
- Mobile-responsive design
- Role-based access control
- Secure authentication
- Scalable architecture

---

## 2. SYSTEM ARCHITECTURE {#system-architecture}

### **High-Level Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 5: DASHBOARD                        │
│                     (Frontend + Backend)                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   ADMIN DASHBOARD    │         │  BUSINESS DASHBOARD  │
│   (Internal Users)   │         │  (External Clients)  │
└──────────┬───────────┘         └──────────┬───────────┘
           │                                │
           └────────────┬───────────────────┘
                        │
           ┌────────────▼────────────┐
           │   Frontend Application  │
           │   (React/Next.js)       │
           └────────────┬────────────┘
                        │
           ┌────────────▼────────────┐
           │   API Gateway           │
           │   (FastAPI/Express)     │
           └────────────┬────────────┘
                        │
                ┌───────┴────────┐
                │                │
     ┌──────────▼─────┐   ┌─────▼──────────┐
     │  Authentication │   │  Authorization │
     │  Service        │   │  Service       │
     └──────────┬─────┘   └─────┬──────────┘
                │                │
                └────────┬───────┘
                         │
           ┌─────────────▼──────────────┐
           │   Backend API Services     │
           ├────────────────────────────┤
           │ - Admin Data Service       │
           │ - Business Data Service    │
           │ - Analytics Service        │
           │ - Real-time Service        │
           └─────────────┬──────────────┘
                         │
           ┌─────────────▼──────────────┐
           │   Database Layer           │
           ├────────────────────────────┤
           │ - PostgreSQL (Layer 1-3)   │
           │ - TimescaleDB (metrics)    │
           │ - MongoDB (Layer 4)        │
           │ - Redis (cache/realtime)   │
           └────────────────────────────┘
```

### **Component Breakdown:**

```yaml
Frontend:
  Framework: React with Next.js
  UI Library: Tailwind CSS + shadcn/ui
  Charts: Recharts / Chart.js
  State Management: React Query + Zustand
  Real-time: Socket.io-client
  
Backend:
  API: FastAPI (Python) or Express.js (Node.js)
  Authentication: JWT + OAuth2
  Real-time: Socket.io / WebSockets
  Caching: Redis
  Rate Limiting: Redis-based
  
Database Access:
  Layer 1-3 Data: PostgreSQL queries
  Layer 4 Data: MongoDB queries
  Metrics: TimescaleDB queries
  Cache: Redis GET/SET
```

---

## 3. TWO-ITERATION DEVELOPMENT STRATEGY {#two-iteration-strategy}

### **ITERATION 1: FUNDAMENTALS (Days 1-7)** ⭐ PRIORITY

**Goal:** Working dashboard with core features

**Admin Dashboard - Iteration 1:**
```
✅ System Health Overview
✅ Pipeline Status Monitor
✅ Agent Performance Metrics
✅ Recent Activity Log
✅ Basic Error Tracking
✅ Data Collection Statistics
```

**Business Dashboard - Iteration 1:**
```
✅ Company Onboarding Form
✅ Current Risk Overview
✅ Top Opportunities Display
✅ Operational Indicators Summary
✅ Recent Insights Feed
✅ Basic Alert Notifications
```

**Shared Features - Iteration 1:**
```
✅ User Authentication (Login/Logout)
✅ Basic Role Management (Admin vs Business User)
✅ Responsive Layout (Desktop + Mobile)
✅ Real-time Data Updates (every 30 seconds)
✅ Simple Navigation
```

---

### **ITERATION 2: ADVANCED FEATURES (Days 8-14)** 🚀 ENHANCEMENT

**Admin Dashboard - Iteration 2:**
```
🔹 Advanced Analytics & Trends
🔹 Agent Decision Review System
🔹 Cost Tracking Dashboard
🔹 Performance Benchmarking
🔹 Automated Reporting
🔹 System Configuration Panel
🔹 Bulk Operations Management
```

**Business Dashboard - Iteration 2:**
```
🔹 Interactive Risk Analysis
🔹 Scenario Simulation Tool
🔹 Custom Report Generation
🔹 Historical Trend Analysis
🔹 Competitive Intelligence View
🔹 Export Functionality (PDF/CSV)
🔹 Email/SMS Alert Configuration
🔹 Recommendation Tracking System
```

**Shared Features - Iteration 2:**
```
🔹 Advanced Search & Filtering
🔹 Custom Dashboard Widgets
🔹 Dark Mode Toggle
🔹 Multi-language Support (Sinhala/Tamil/English)
🔹 Advanced Analytics
🔹 Audit Logging
🔹 Performance Optimization
```

---

## 4. DASHBOARD TYPES & USER ROLES {#dashboard-types}

### **User Roles & Permissions:**

```yaml
Role 1: SUPER_ADMIN
  Access: Full system access
  Permissions:
    - View all admin dashboards
    - View all business dashboards
    - Manage users and permissions
    - Configure system settings
    - Access raw database
    - Export all data
  Use Case: System administrators, developers

Role 2: ADMIN
  Access: Admin dashboard only
  Permissions:
    - View pipeline health
    - Monitor agent performance
    - Review errors and logs
    - Generate reports
    - View aggregated statistics
  Use Case: Operations team, analysts

Role 3: BUSINESS_USER
  Access: Business dashboard for their company only
  Permissions:
    - View own company insights
    - Configure company profile
    - Receive alerts
    - Export own reports
    - Manage company users
  Use Case: Business owners, managers

Role 4: BUSINESS_VIEWER
  Access: Read-only business dashboard
  Permissions:
    - View insights (read-only)
    - Receive alerts
    - Export reports
  Use Case: Team members, stakeholders
```

### **Access Control Matrix:**

| Feature | SUPER_ADMIN | ADMIN | BUSINESS_USER | BUSINESS_VIEWER |
|---------|-------------|-------|---------------|-----------------|
| Admin Dashboard | ✅ | ✅ | ❌ | ❌ |
| All Business Dashboards | ✅ | ✅ | ❌ | ❌ |
| Own Business Dashboard | ✅ | ✅ | ✅ | ✅ |
| Edit Company Profile | ✅ | ✅ | ✅ | ❌ |
| Configure Alerts | ✅ | ✅ | ✅ | ❌ |
| View System Metrics | ✅ | ✅ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ✅ (own company) | ❌ |
| Export Data | ✅ | ✅ | ✅ (own data) | ✅ (own data) |
| System Configuration | ✅ | ❌ | ❌ | ❌ |

---

## 5. ITERATION 1: FUNDAMENTAL COMPONENTS {#iteration-1}

### **Shared Components (Both Dashboards):**

#### **Component 1: Authentication System**

**Purpose:** Secure login and session management

**Features:**
- Email/password authentication
- JWT token-based sessions
- "Remember me" functionality
- Password reset flow
- Session timeout (30 minutes inactivity)
- Multi-device login support

**Implementation Requirements:**
```yaml
Login Page:
  Fields:
    - Email input (validation)
    - Password input (masked)
    - Remember me checkbox
    - Forgot password link
  
  Validation:
    - Email format validation
    - Password minimum 8 characters
    - Rate limiting (5 attempts per 15 min)
  
  Success Flow:
    1. Validate credentials against database
    2. Generate JWT token (24 hour expiry)
    3. Store token in httpOnly cookie
    4. Redirect based on role:
       - Admin → Admin Dashboard
       - Business User → Business Dashboard
  
  Error Handling:
    - Invalid credentials → Show error message
    - Account locked → Show contact admin message
    - Server error → Show retry option
```

**Database Schema:**
```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,  -- SUPER_ADMIN, ADMIN, BUSINESS_USER, BUSINESS_VIEWER
    company_id INTEGER REFERENCES companies(id),  -- NULL for admins
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sessions table (for tracking active sessions)
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    token_hash VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

#### **Component 2: Navigation Layout**

**Purpose:** Consistent navigation across dashboard

**Desktop Layout:**
```
┌────────────────────────────────────────────────┐
│  Logo    Dashboard Name       User Menu  🔔   │  ← Header (60px)
├────────────────────────────────────────────────┤
│ [Nav] │                                        │
│ Links │         Main Content Area              │
│       │                                        │
│ [📊]  │                                        │
│ [📈]  │         (Dynamic content)              │
│ [⚙️]  │                                        │
│ [📄]  │                                        │
│       │                                        │
│ 200px │              Responsive                │
└───────┴────────────────────────────────────────┘
  Sidebar       Main Content
```

**Mobile Layout:**
```
┌──────────────────────────────┐
│ ☰  Dashboard Name    User 🔔│  ← Header
├──────────────────────────────┤
│                              │
│      Main Content            │
│      (Full width)            │
│                              │
│                              │
└──────────────────────────────┘
│ [Home] [Alerts] [Profile]   │  ← Bottom Nav
└──────────────────────────────┘
```

**Navigation Structure:**

**Admin Sidebar:**
```
📊 Overview
📈 Pipeline Status
🤖 Agent Performance
📋 Activity Logs
⚠️ Errors & Issues
📊 Data Statistics
👥 User Management (SUPER_ADMIN only)
⚙️ Settings
```

**Business User Sidebar:**
```
🏠 Dashboard Home
⚠️ Risk Overview
💡 Opportunities
📊 Indicators
🔔 Alerts
📄 Reports
⚙️ Company Settings
👥 Team Management
```

---

#### **Component 3: Real-time Update System**

**Purpose:** Keep dashboard data fresh without manual refresh

**Implementation Strategy:**

**Option 1: WebSocket (Recommended for real-time)**
```yaml
Technology: Socket.io
Update Frequency: Instant (push-based)
Use Cases:
  - Critical alerts (immediate)
  - Pipeline status changes
  - New insights generated
  - System health changes

Connection Flow:
  1. Client connects on dashboard load
  2. Server authenticates connection
  3. Server subscribes client to relevant rooms:
     - Admins: "admin-room"
     - Business Users: "company-{id}-room"
  4. Server pushes updates to rooms
  5. Client updates UI without refresh
```

**Option 2: Polling (Simpler fallback)**
```yaml
Technology: React Query with refetch
Update Frequency: 30 seconds
Use Cases:
  - Non-critical data updates
  - Fallback when WebSocket unavailable

Implementation:
  - Auto-refetch every 30 seconds
  - Invalidate cache on user action
  - Show "updated X seconds ago" indicator
```

**Hybrid Approach (RECOMMENDED):**
```
Critical Data (WebSocket):
├── New critical alerts
├── System down/up notifications
├── Breaking news events
└── Pipeline failures

Regular Data (Polling):
├── Statistics and metrics
├── Historical data
├── Chart data
└── List updates
```

---

## 6. ADMIN DASHBOARD - COMPLETE SPECIFICATION {#admin-dashboard}

### **Page 1: System Overview (Home)**

**Purpose:** High-level health check of entire system at a glance

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  System Overview - Real-time Status                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ System      │ │ Pipeline    │ │ Active      │  ← Cards  │
│  │ Status: ✅  │ │ Status: ✅  │ │ Users: 127  │           │
│  │ Healthy     │ │ Running     │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Sources     │ │ Articles    │ │ Insights    │           │
│  │ Active:     │ │ Today:      │ │ Generated:  │           │
│  │ 24/26       │ │ 487         │ │ 156         │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Pipeline Health Timeline (Last 24 Hours)        │       │
│  │  [Line chart showing uptime %]                   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Quick Actions                                   │       │
│  │  [Refresh All] [View Errors] [Export Logs]      │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Components:**

**1. Status Cards (6 cards):**
```yaml
Card 1: System Status
  Data Source: System health check endpoint
  Display:
    - Status indicator (Green/Yellow/Red)
    - Text: "Healthy" / "Degraded" / "Down"
    - Last checked timestamp
  Update: Real-time (WebSocket)
  Click Action: Navigate to detailed system page

Card 2: Pipeline Status
  Data Source: Orchestrator status from database
  Display:
    - Status indicator
    - Current state: "Running" / "Paused" / "Error"
    - Last successful run timestamp
  Update: Real-time
  Click Action: Navigate to pipeline details

Card 3: Active Users
  Data Source: user_sessions table
  Display:
    - Count of active sessions (last 30 min)
    - Breakdown: X admins, Y business users
  Update: Every 30 seconds
  Click Action: Navigate to user management

Card 4: Active Sources
  Data Source: scraping_schedule table
  Display:
    - Active sources / Total sources (e.g., 24/26)
    - List of inactive sources on hover
  Update: Every minute
  Click Action: Navigate to source management

Card 5: Articles Today
  Data Source: raw_articles table
  Query: COUNT(*) WHERE DATE(scraped_at) = TODAY
  Display:
    - Total article count
    - Trend indicator (↑15% vs yesterday)
  Update: Every 5 minutes

Card 6: Insights Generated
  Data Source: business_insights table (Layer 4)
  Query: COUNT(*) WHERE DATE(generated_at) = TODAY
  Display:
    - Total insights
    - Critical insights count (in red)
  Update: Real-time
```

**2. Pipeline Health Timeline Chart:**
```yaml
Chart Type: Line chart
Time Range: Last 24 hours
Data Points: One per hour (24 points)
Metrics Displayed:
  - System uptime % (green line)
  - Articles processed per hour (blue bars)
  - Errors per hour (red line)

Data Source:
  Query: agent_metrics table grouped by hour
  
Interactions:
  - Hover: Show exact values
  - Click point: Show details for that hour
  - Zoom: Last 6 hours / 24 hours / 7 days
```

**3. Quick Actions Bar:**
```yaml
Button 1: Refresh All
  Action: Manually trigger full data refresh
  Icon: 🔄
  Confirmation: None (safe action)

Button 2: View Errors
  Action: Navigate to errors page with today filter
  Icon: ⚠️
  Badge: Show error count if > 0

Button 3: Export Logs
  Action: Download system logs as CSV
  Icon: 📥
  Options: Last hour / Today / Last 7 days
```

---

### **Page 2: Pipeline Status Monitor**

**Purpose:** Detailed view of Layer 1-4 pipeline execution

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Pipeline Status Monitor                    [Pause] [Restart]│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Current Cycle Status                              │     │
│  │  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐        │     │
│  │  │Layer1│ → │Layer2│ → │Layer3│ → │Layer4│        │     │
│  │  │ ✅   │   │ ⏳   │   │ ⏸️   │   │ ⏸️   │        │     │
│  │  │ Done │   │Active│   │Queued│   │Queued│        │     │
│  │  └──────┘   └──────┘   └──────┘   └──────┘        │     │
│  │                                                     │     │
│  │  Started: 10:30:00 | Elapsed: 2m 15s               │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Layer 1: Data Collection                          │     │
│  │  Status: Completed ✅                               │     │
│  │  Sources Scraped: 18/26                            │     │
│  │  Articles Collected: 43                            │     │
│  │  Duration: 1m 30s                                  │     │
│  │  [View Details]                                    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Layer 2: National Indicators                      │     │
│  │  Status: Processing... ⏳ 65%                      │     │
│  │  Indicators Calculated: 13/20                      │     │
│  │  Current: Economic Health Index                    │     │
│  │  [View Details]                                    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  [Layer 3 and Layer 4 sections follow same pattern]        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Recent Pipeline Runs (Last 10)                    │     │
│  │  ┌──────────┬─────────┬────────┬─────────┐        │     │
│  │  │ Time     │ Status  │ Duration│ Articles│        │     │
│  │  ├──────────┼─────────┼────────┼─────────┤        │     │
│  │  │ 10:15 AM │ ✅      │ 4m 22s │ 38      │        │     │
│  │  │ 10:00 AM │ ✅      │ 3m 55s │ 41      │        │     │
│  │  │ 09:45 AM │ ⚠️      │ 5m 12s │ 35      │        │     │
│  │  │ ...      │ ...     │ ...    │ ...     │        │     │
│  │  └──────────┴─────────┴────────┴─────────┘        │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

**Data Sources:**

```yaml
Current Cycle Status:
  Source: Redis (real-time state)
  Key: "pipeline:current_cycle"
  Update: Real-time WebSocket

Layer Status Cards:
  Source: PostgreSQL + MongoDB
  Tables:
    - Layer 1: scraping_schedule, raw_articles
    - Layer 2: national_indicators
    - Layer 3: operational_indicator_values
    - Layer 4: business_insights
  Update: Every 5 seconds during active run

Recent Runs Table:
  Source: PostgreSQL
  Table: pipeline_execution_history
  Query: Last 10 runs ordered by timestamp DESC
  Update: After each run completes
```

**Interactive Features:**

```yaml
Layer Detail View:
  Click Action: Expand to show:
    - Individual step progress
    - Any errors/warnings
    - Resource usage (CPU, memory)
    - Agent decisions (for AI-powered steps)

Pause/Restart Controls:
  Pause:
    - Action: Set pipeline state to "paused"
    - Effect: Completes current step, then pauses
    - Confirmation: "Are you sure?"
  
  Restart:
    - Action: Trigger new pipeline cycle immediately
    - Confirmation: Only if last run < 5 min ago
```

---

### **Page 3: Agent Performance Dashboard**

**Purpose:** Monitor AI agent decisions, costs, and effectiveness

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Agent Performance Dashboard                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Agent Activity Summary (Today)                     │    │
│  │                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │    │
│  │  │ Total        │  │ Groq         │  │ Avg       │ │    │
│  │  │ Decisions:   │  │ Requests:    │  │ Latency:  │ │    │
│  │  │ 487          │  │ 382/14,400   │  │ 1.2s      │ │    │
│  │  └──────────────┘  └──────────────┘  └───────────┘ │    │
│  │                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │    │
│  │  │ Success      │  │ Total        │  │ Tokens    │ │    │
│  │  │ Rate:        │  │ Cost:        │  │ Used:     │ │    │
│  │  │ 98.3%        │  │ $0.00 ✅     │  │ 1.2M      │ │    │
│  │  └──────────────┘  └──────────────┘  └───────────┘ │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Agent Performance Breakdown                        │    │
│  │  ┌────────────────────────────────────────────┐     │    │
│  │  │ Agent Name          Calls  Success  Latency│     │    │
│  │  ├────────────────────────────────────────────┤     │    │
│  │  │ Source Monitor      127    100%    0.8s    │     │    │
│  │  │ Processing Agent    243    99%     0.5s    │     │    │
│  │  │ Priority Detection   89    98%     1.1s    │     │    │
│  │  │ Validation Agent    198    97%     0.6s    │     │    │
│  │  │ Scheduler Agent       3    100%    2.3s    │     │    │
│  │  └────────────────────────────────────────────┘     │    │
│  │  [View Details for Each Agent]                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Recent Agent Decisions (Last 20)                   │    │
│  │  [Filterable by agent, status, time]                │    │
│  │                                                      │    │
│  │  ┌──────┬─────────┬──────────┬────────┬─────────┐  │    │
│  │  │ Time │ Agent   │ Decision │ Result │ Details │  │    │
│  │  ├──────┼─────────┼──────────┼────────┼─────────┤  │    │
│  │  │10:32 │ Monitor │ Scrape DM│ ✅     │ [View]  │  │    │
│  │  │10:31 │ Process │ Classify │ ✅     │ [View]  │  │    │
│  │  │10:30 │ Priority│ High     │ ✅     │ [View]  │  │    │
│  │  │ ...  │ ...     │ ...      │ ...    │ ...     │  │    │
│  │  └──────┴─────────┴──────────┴────────┴─────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Components:**

**1. Summary Metrics:**
```yaml
Total Decisions:
  Source: agent_decisions table
  Query: COUNT(*) WHERE DATE(timestamp) = TODAY
  Display: Number with trend vs yesterday

Groq Requests:
  Source: agent_decisions table
  Query: COUNT(*) WHERE provider = 'ChatGroq' AND DATE = TODAY
  Display: "Used / Daily Limit" with progress bar
  Alert: Show warning if > 12,000 (80% of limit)

Average Latency:
  Source: agent_decisions table
  Query: AVG(latency_ms) / 1000
  Display: Seconds with 1 decimal
  Color: Green <2s, Yellow 2-5s, Red >5s

Success Rate:
  Source: agent_decisions table
  Query: (Successful decisions / Total decisions) * 100
  Display: Percentage
  Color: Green >95%, Yellow 90-95%, Red <90%

Total Cost:
  Source: agent_decisions table
  Query: SUM(cost_usd)
  Display: Currency with FREE badge if $0
  Color: Green if $0, Yellow if <$10, Red if >$10

Tokens Used:
  Source: agent_decisions table
  Query: SUM(tokens_used)
  Display: Million tokens (e.g., 1.2M)
```

**2. Agent Performance Table:**
```yaml
Data Source: agent_decisions table grouped by agent_name
Columns:
  - Agent Name
  - Total Calls (today)
  - Success Rate (%)
  - Average Latency (seconds)
  - [View Details] button

Sorting: Default by total calls DESC
Filtering: None (all agents shown)

Click Action: Navigate to agent detail page showing:
  - All decisions by this agent
  - Trend over time
  - Common failure patterns
  - Token usage breakdown
```

**3. Recent Decisions Table:**
```yaml
Data Source: agent_decisions table
Columns:
  - Timestamp (HH:MM format)
  - Agent Name
  - Decision Made (summarized)
  - Result (✅ success, ❌ failure, ⚠️ warning)
  - [View Details] button

Limit: 20 most recent
Update: Real-time (WebSocket for new decisions)
Pagination: Load more on scroll

Filters:
  - Agent dropdown (all agents)
  - Status dropdown (all, success, failure, warning)
  - Time range (last hour, today, last 7 days)

Details Modal:
  Click [View Details] shows:
  - Full input data
  - Complete output/decision
  - Reasoning provided by LLM
  - Tokens used
  - Latency
  - Timestamp
```

---

### **Page 4: Activity Logs**

**Purpose:** Searchable, filterable log of all system activities

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Activity Logs                                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Filters                                            │    │
│  │  [Time Range ▼] [Level ▼] [Component ▼] [Search]   │    │
│  │  [Apply Filters] [Reset]                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Log Entries (Newest First)                         │    │
│  │                                                      │    │
│  │  ⚠️ 10:35:42 | Layer1 | WARNING                     │    │
│  │  Source "Hiru News" failed to scrape (timeout)      │    │
│  │  [View Details] [Retry]                             │    │
│  │  ─────────────────────────────────────────────────  │    │
│  │  ✅ 10:35:15 | Layer2 | INFO                        │    │
│  │  Classification completed: 43 articles processed    │    │
│  │  [View Details]                                     │    │
│  │  ─────────────────────────────────────────────────  │    │
│  │  ❌ 10:34:58 | Layer1 | ERROR                       │    │
│  │  Database connection lost, retrying...              │    │
│  │  [View Details] [View Stack Trace]                 │    │
│  │  ─────────────────────────────────────────────────  │    │
│  │  ℹ️ 10:34:30 | Auth | INFO                         │    │
│  │  User admin@example.com logged in                  │    │
│  │  [View Details]                                     │    │
│  │  ─────────────────────────────────────────────────  │    │
│  │  [Load More (50 per page)]                         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  [Export Logs as CSV] [Export Filtered Logs]                │
└─────────────────────────────────────────────────────────────┘
```

**Features:**

```yaml
Filters:
  Time Range:
    - Last hour
    - Last 6 hours
    - Today
    - Last 7 days
    - Custom date range
  
  Level:
    - All levels
    - INFO (ℹ️)
    - WARNING (⚠️)
    - ERROR (❌)
    - CRITICAL (🔥)
  
  Component:
    - All components
    - Layer 1
    - Layer 2
    - Layer 3
    - Layer 4
    - Authentication
    - Database
    - API
    - Agents
  
  Search:
    - Free text search across message
    - Searches: message, source, user, error type

Log Entry Display:
  Format: [Icon] [Time] | [Component] | [Level]
  Message: First line of log message
  Actions: Context-dependent buttons
  
  Click to Expand:
    - Full log message
    - Stack trace (if error)
    - Context data (JSON)
    - Related logs (same request ID)

Real-time Updates:
  New logs appear at top with highlight
  Auto-scroll option (toggle)
  Sound notification for errors (toggle)

Export:
  Format: CSV
  Includes: Timestamp, Level, Component, Message, Context
  Options: Current view or apply filters
```

---

### **Page 5: Data Collection Statistics**

**Purpose:** Monitor data collection performance and source health

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Data Collection Statistics                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Collection Summary (Last 24 Hours)                 │    │
│  │                                                      │    │
│  │  Total Articles: 1,247                              │    │
│  │  Unique Articles: 1,089 (87% dedup rate)            │    │
│  │  Average Per Hour: 52                               │    │
│  │  Peak Hour: 10:00 AM (127 articles)                 │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Source Health Status                               │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │ Source          Status  Success  Avg Time  │    │    │
│  │  ├─────────────────────────────────────────────┤    │    │
│  │  │ Daily Mirror    ✅      100%     2.3s      │    │    │
│  │  │ Hiru News       ⚠️      87%      5.1s      │    │    │
│  │  │ Ada Derana      ✅      98%      1.8s      │    │    │
│  │  │ DMC Alerts      ✅      100%     0.5s      │    │    │
│  │  │ Weather Dept    ✅      100%     1.2s      │    │    │
│  │  │ Central Bank    ❌      0%       timeout   │    │    │
│  │  │ ... (20 more sources)                      │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │  [View All Sources] [Configure]                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Articles by Category (Today)                       │    │
│  │  [Pie Chart]                                        │    │
│  │  - Political: 35%                                   │    │
│  │  - Economic: 28%                                    │    │
│  │  - Social: 15%                                      │    │
│  │  - Environmental: 12%                               │    │
│  │  - Legal: 7%                                        │    │
│  │  - Technological: 3%                                │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Collection Trend (Last 7 Days)                     │    │
│  │  [Line Chart: Articles collected per day]           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Data Sources:**

```yaml
Collection Summary:
  Source: raw_articles table
  Queries:
    Total: COUNT(*) WHERE scraped_at >= NOW() - INTERVAL '24 hours'
    Unique: COUNT(DISTINCT content_hash)
    Per Hour: Total / 24
    Peak Hour: GROUP BY HOUR(scraped_at) ORDER BY COUNT(*) DESC LIMIT 1

Source Health Table:
  Source: scraping_schedule + agent_decisions
  Columns:
    - Source name
    - Status: Based on last scrape success
    - Success rate: Last 10 scrape attempts
    - Avg time: Average scraping duration
  
  Status Logic:
    ✅ Green: Success rate > 95%, last scrape successful
    ⚠️ Yellow: Success rate 80-95% OR last scrape failed
    ❌ Red: Success rate < 80% OR down for 1+ hour

Category Chart:
  Source: processed_articles table (Layer 2)
  Query: GROUP BY primary_category
  Chart: Pie chart or donut chart
  Interactive: Click slice to filter article list

Trend Chart:
  Source: raw_articles table
  Query: GROUP BY DATE(scraped_at) for last 7 days
  Chart: Line chart with data points
  Interactive: Hover to see exact count
```

---

## 7. BUSINESS USER DASHBOARD - COMPLETE SPECIFICATION {#business-user-dashboard}

### **Page 1: Company Onboarding Form**

**Purpose:** Collect business profile information for accurate insights

**When Shown:** 
- First login (company profile incomplete)
- Accessible from Settings > Company Profile

**Form Sections:**

**Section 1: Basic Information**
```yaml
Fields:
  Company Name:
    Type: Text
    Required: Yes
    Validation: 3-100 characters
    Example: "ABC Retail Pvt Ltd"
  
  Industry:
    Type: Dropdown
    Required: Yes
    Options: 
      - Retail & E-commerce
      - Manufacturing
      - Logistics & Transportation
      - Hospitality & Tourism
      - Agriculture
      - Construction
      - Healthcare
      - Financial Services
      - Technology
      - Other (specify)
    
  Business Scale:
    Type: Dropdown
    Required: Yes
    Options:
      - Micro (1-10 employees)
      - Small (11-50 employees)
      - Medium (51-250 employees)
      - Large (250+ employees)
  
  Location:
    Type: Dropdown + Text
    Required: Yes
    Options: 
      - Primary province (dropdown)
      - City/Town (text input)
    Example: Western Province, Colombo
  
  Number of Employees:
    Type: Number
    Required: Yes
    Validation: 1-100,000
  
  Annual Revenue (LKR):
    Type: Dropdown
    Required: No
    Options:
      - Below 10M
      - 10M - 50M
      - 50M - 100M
      - 100M - 500M
      - 500M - 1B
      - Above 1B
```

**Section 2: Operational Profile**
```yaml
Import Dependency:
  Question: "What percentage of your supplies/materials are imported?"
  Type: Slider (0-100%)
  Default: 50%
  
Critical Suppliers:
  Question: "How many critical suppliers do you depend on?"
  Type: Dropdown
  Options: 1-5 / 6-10 / 11-20 / 20+
  
Fuel Dependency:
  Question: "How dependent is your operation on fuel/energy?"
  Type: Radio
  Options: 
    - Critical (operations stop without it)
    - High (major disruptions)
    - Medium (some impact)
    - Low (minimal impact)

Workforce Distribution:
  Question: "Where are your employees located?"
  Type: Multi-select checkboxes
  Options: All provinces + major cities
  
Customer Base:
  Question: "Who are your primary customers?"
  Type: Checkboxes (multiple)
  Options:
    - Local consumers (B2C)
    - Local businesses (B2B)
    - Export markets
    - Government contracts
    - Other
```

**Section 3: Risk Sensitivity**
```yaml
Currency Sensitivity:
  Question: "How sensitive is your business to currency fluctuations?"
  Type: Scale 1-10
  Display: Slider with labels
  
Supply Chain Complexity:
  Question: "How complex is your supply chain?"
  Type: Dropdown
  Options:
    - Simple (1-2 suppliers, local)
    - Moderate (multiple suppliers, regional)
    - Complex (international, many dependencies)
    - Very Complex (global, highly dependent)

Power Cut Impact:
  Question: "How do power cuts affect your operations?"
  Type: Dropdown
  Options:
    - Critical (operations stop)
    - Severe (major delays/losses)
    - Moderate (some disruption)
    - Minimal (backup power available)

Political Stability Impact:
  Question: "How do political events affect your business?"
  Type: Dropdown
  Options:
    - High (policy changes directly impact us)
    - Medium (indirect effects)
    - Low (minimal impact)
```

**Section 4: Notification Preferences**
```yaml
Alert Channels:
  Question: "How should we send critical alerts?"
  Type: Checkboxes (multiple)
  Options:
    - Dashboard notifications (always on)
    - Email
    - SMS
    - WhatsApp (future)
  
Alert Frequency:
  Question: "How often should we send insight summaries?"
  Type: Radio
  Options:
    - Real-time (as they happen)
    - Hourly digest
    - Daily summary (morning)
    - Weekly report
  
Minimum Alert Severity:
  Question: "Minimum severity level for notifications"
  Type: Dropdown
  Options:
    - All alerts
    - Medium and above
    - High and above
    - Critical only
```

**Form Submission:**
```yaml
Validation:
  - All required fields completed
  - Logical consistency (e.g., employees match scale)
  - Email format valid (for notifications)

On Submit:
  1. Save to company_profiles table
  2. Create/update sensitivity_config (Layer 3)
  3. Trigger initial indicator calculation
  4. Redirect to dashboard home
  5. Show "Profile Complete ✅" message

Progress Saving:
  - Auto-save every 30 seconds to draft
  - "Save Draft" button
  - Resume from draft on return
```

---

### **Page 2: Dashboard Home (Business User)**

**Purpose:** At-a-glance view of current business situation

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Good Morning, [Company Name] 👋                             │
│  Last updated: 2 minutes ago                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Overall Business Health Score                   │       │
│  │                                                   │       │
│  │  ┌─────────────────────────────────────────┐     │       │
│  │  │         [Circular gauge: 72/100]        │     │       │
│  │  │              GOOD                       │     │       │
│  │  │         ↓ 5 points from last week       │     │       │
│  │  └─────────────────────────────────────────┘     │       │
│  │                                                   │       │
│  │  Contributing factors:                            │       │
│  │  ✅ Economic stability improving                  │       │
│  │  ⚠️ Supply chain pressure increasing             │       │
│  │  ⚠️ Currency volatility elevated                 │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ 🔴 CRITICAL │ │ ⚠️ HIGH     │ │ 💡 OPPORTUN │  ← Cards  │
│  │ RISKS       │ │ RISKS       │ │ -ITIES      │           │
│  │     2       │ │     5       │ │     3       │           │
│  │ [View All]  │ │ [View All]  │ │ [View All]  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Recent Insights (Last 24 Hours)                 │       │
│  │                                                   │       │
│  │  🔴 CRITICAL | 2 hours ago                        │       │
│  │  Fuel shortage expected in Western Province      │       │
│  │  Impact: HIGH | Confidence: 85%                  │       │
│  │  [View Details] [Take Action]                    │       │
│  │  ──────────────────────────────────────────────  │       │
│  │  ⚠️ HIGH | 5 hours ago                           │       │
│  │  Currency depreciation accelerating              │       │
│  │  Impact: MEDIUM | Confidence: 78%                │       │
│  │  [View Details] [Dismiss]                        │       │
│  │  ──────────────────────────────────────────────  │       │
│  │  💡 OPPORTUNITY | 8 hours ago                    │       │
│  │  Government tax incentive for exports            │       │
│  │  Potential Value: HIGH | Feasibility: 75%        │       │
│  │  [View Details] [Interested]                     │       │
│  │  ──────────────────────────────────────────────  │       │
│  │  [View All Insights]                             │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Quick Actions                                   │       │
│  │  [Generate Report] [Contact Support] [Settings]  │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**Components:**

**1. Health Score Gauge:**
```yaml
Data Source: 
  - Calculated from all operational indicators (Layer 3)
  - Weighted by company profile sensitivities
  
Calculation:
  health_score = Weighted average of:
    - Supply chain stability (30%)
    - Operational readiness (25%)
    - Financial health (20%)
    - Market conditions (15%)
    - Regulatory compliance (10%)
  
  Score ranges:
    80-100: Excellent (Green)
    60-79: Good (Light green)
    40-59: Fair (Yellow)
    20-39: Poor (Orange)
    0-19: Critical (Red)

Display:
  - Large circular gauge (animated)
  - Numerical score out of 100
  - Text label (Excellent/Good/Fair/Poor/Critical)
  - Trend indicator (↑↓ X points from last week)
  - Top 3 contributing factors (good and bad)

Update: Every 15 minutes
```

**2. Risk/Opportunity Summary Cards:**
```yaml
Critical Risks Card:
  Data Source: business_insights table
  Query: WHERE company_id = X AND type = 'risk' 
         AND severity = 'critical' AND active = true
  Display:
    - Count of critical risks
    - Red background
    - Pulsing animation if count > 0
  Click: Navigate to Risk Overview page filtered to critical

High Risks Card:
  Same as above but severity = 'high'
  Yellow/orange background

Opportunities Card:
  Data Source: business_insights table
  Query: WHERE company_id = X AND type = 'opportunity' 
         AND active = true
  Display:
    - Count of active opportunities
    - Green background with lightbulb icon
  Click: Navigate to Opportunities page
```

**3. Recent Insights Feed:**
```yaml
Data Source: business_insights table
Query: Latest 5 insights ordered by created_at DESC
Filters: Active insights only

Display Format per Insight:
  Header:
    - Severity icon (🔴⚠️💡)
    - Severity level text
    - Time ago (e.g., "2 hours ago")
  
  Content:
    - Insight title (one line, truncated)
    - Impact level + Confidence score
  
  Actions:
    - [View Details]: Open insight detail modal
    - [Take Action]: Open recommendations
    - [Dismiss]: Mark as read/acknowledged

Update: Real-time WebSocket for new insights
Empty State: "No new insights. System is monitoring..."
```

---

This completes PART 1 of the Layer 5 Dashboard Implementation Plan.

**PART 1 Summary:**
- ✅ System architecture defined
- ✅ Two-iteration strategy outlined
- ✅ User roles and permissions specified
- ✅ Admin dashboard (5 pages) fully detailed
- ✅ Business user dashboard (onboarding + home) specified
- ✅ Data sources and update frequencies documented

**PART 2 will cover:**
- Business User Dashboard remaining pages (Risks, Opportunities, Indicators, Alerts, Reports, Settings)
- Data flow and API specifications
- Frontend-backend integration
- Performance optimization strategies
- Testing and deployment guide
- Security implementation

Would you like me to create PART 2 now?
