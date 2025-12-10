# LAYER 5: INTELLIGENT DASHBOARD SYSTEM
## Comprehensive Implementation Plan - PART 2

---

## TABLE OF CONTENTS - PART 2

8. [Business Dashboard Remaining Pages](#business-pages)
9. [API Specifications](#api-specs)
10. [Frontend-Backend Integration](#integration)
11. [Performance Optimization](#performance)
12. [Security Implementation](#security)
13. [Testing Strategy](#testing)
14. [Deployment Guide](#deployment)
15. [Iteration Roadmap](#roadmap)

---

## 8. BUSINESS DASHBOARD REMAINING PAGES {#business-pages}

### **Page 3: Risk Overview**

**Purpose:** Detailed view of all identified risks with filtering and sorting

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Risk Overview                                    [Export]   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Risk Summary                                       │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│  │  │ Critical │ │ High     │ │ Medium   │            │    │
│  │  │    2     │ │    5     │ │    8     │            │    │
│  │  └──────────┘ └──────────┘ └──────────┘            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Filters & Sort                                     │    │
│  │  [Severity ▼] [Category ▼] [Time ▼] [Search...]    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Active Risks (15)                                  │    │
│  │                                                      │    │
│  │  ┌────────────────────────────────────────────┐     │    │
│  │  │ 🔴 CRITICAL | Supply Chain Disruption      │     │    │
│  │  │                                             │     │    │
│  │  │ Fuel shortage expected in Western Province │     │    │
│  │  │ affecting deliveries and operations         │     │    │
│  │  │                                             │     │    │
│  │  │ Probability: 85% | Impact: CRITICAL         │     │    │
│  │  │ Time Horizon: 24-48 hours                   │     │    │
│  │  │ Confidence: 82%                             │     │    │
│  │  │                                             │     │    │
│  │  │ Affected Operations:                        │     │    │
│  │  │ • Deliveries (critical impact)              │     │    │
│  │  │ • Warehouse operations (high impact)        │     │    │
│  │  │ • Customer service (medium impact)          │     │    │
│  │  │                                             │     │    │
│  │  │ [View Full Analysis] [See Recommendations]  │     │    │
│  │  │ [Mark as Acknowledged] [Not Applicable]     │     │    │
│  │  └────────────────────────────────────────────┘     │    │
│  │                                                      │    │
│  │  ┌────────────────────────────────────────────┐     │    │
│  │  │ ⚠️ HIGH | Currency Volatility Risk         │     │    │
│  │  │                                             │     │    │
│  │  │ LKR depreciation accelerating, affecting   │     │    │
│  │  │ import costs for raw materials              │     │    │
│  │  │                                             │     │    │
│  │  │ Probability: 78% | Impact: HIGH             │     │    │
│  │  │ Time Horizon: This week                     │     │    │
│  │  │ Confidence: 75%                             │     │    │
│  │  │                                             │     │    │
│  │  │ Financial Impact Estimate: +15-20% costs    │     │    │
│  │  │                                             │     │    │
│  │  │ [View Full Analysis] [See Recommendations]  │     │    │
│  │  └────────────────────────────────────────────┘     │    │
│  │                                                      │    │
│  │  [... More risks ...]                               │    │
│  │  [Load More]                                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Risk Card Components:**

```yaml
Risk Display:
  Header:
    - Severity badge (color-coded)
    - Risk name (bold, clickable)
  
  Description:
    - 2-3 sentence summary
    - Easy to scan
  
  Metrics:
    - Probability: 0-100%
    - Impact: Low/Medium/High/Critical
    - Time Horizon: When it might occur
    - Confidence: How sure we are (0-100%)
  
  Additional Info:
    - Affected Operations (if applicable)
    - Financial Impact (if quantifiable)
    - Related indicators that triggered this
  
  Actions:
    - View Full Analysis: Open detail modal
    - See Recommendations: Jump to action plan
    - Mark as Acknowledged: User awareness tracking
    - Not Applicable: Dismiss if irrelevant

Filtering Options:
  Severity:
    - All
    - Critical only
    - High and above
    - Medium and above
  
  Category:
    - All categories
    - Operational
    - Financial
    - Competitive
    - Regulatory
    - Strategic
  
  Time Range:
    - Active now
    - Last 24 hours
    - Last 7 days
    - Last 30 days
    - Custom range
  
  Search:
    - Free text across risk name and description

Sorting Options:
  - Severity (default)
  - Probability (high to low)
  - Impact (high to low)
  - Time (newest first)
  - Confidence (high to low)
```

**Risk Detail Modal:**

```yaml
When Opened: Click "View Full Analysis"

Layout:
  Header:
    - Risk name
    - Severity badge
    - Close button
  
  Tabs:
    1. Overview
    2. Recommendations
    3. History
  
  Tab 1 - Overview:
    - Complete description (full LLM output)
    - All metrics with explanations
    - Root cause analysis
    - Affected operations breakdown
    - Similar historical events (if any)
  
  Tab 2 - Recommendations:
    - Immediate actions (24 hours)
    - Short-term actions (this week)
    - Medium-term actions (this month)
    - Each action with:
      * Task description
      * Responsible person/role
      * Time required
      * Cost estimate
      * Expected outcome
  
  Tab 3 - History:
    - When risk was first detected
    - How probability/impact changed over time
    - User actions taken
    - Outcome (if resolved)

Actions in Modal:
  - Mark as High Priority
  - Assign to team member
  - Add to report
  - Export as PDF
  - Share via email
```

---

### **Page 4: Opportunities**

**Purpose:** Display business opportunities detected by system

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Business Opportunities                        [Export]      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Opportunity Summary                                │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│  │  │ High     │ │ Medium   │ │ Total    │            │    │
│  │  │ Value    │ │ Value    │ │ Active   │            │    │
│  │  │    3     │ │    5     │ │    11    │            │    │
│  │  └──────────┘ └──────────┘ └──────────┘            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Filters                                            │    │
│  │  [Value ▼] [Category ▼] [Feasibility ▼]            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Active Opportunities (11)                          │    │
│  │                                                      │    │
│  │  ┌────────────────────────────────────────────┐     │    │
│  │  │ 💡 HIGH VALUE | Export Tax Incentive       │     │    │
│  │  │                                             │     │    │
│  │  │ Government announced new tax breaks for    │     │    │
│  │  │ export-oriented businesses in your sector  │     │    │
│  │  │                                             │     │    │
│  │  │ Potential Value: 8.5/10 | Feasibility: 75% │     │    │
│  │  │ Strategic Fit: 85% | Timing: Next 2 weeks  │     │    │
│  │  │                                             │     │    │
│  │  │ Why Now:                                    │     │    │
│  │  │ Registration deadline in 15 days, early     │     │    │
│  │  │ applicants get priority processing          │     │    │
│  │  │                                             │     │    │
│  │  │ Requirements:                               │     │    │
│  │  │ • Export documentation (have)               │     │    │
│  │  │ • Registration fee: LKR 50,000              │     │    │
│  │  │ • Processing time: 2-3 weeks                │     │    │
│  │  │                                             │     │    │
│  │  │ [View Full Details] [I'm Interested]        │     │    │
│  │  │ [Not Relevant] [Remind Me Later]            │     │    │
│  │  └────────────────────────────────────────────┘     │    │
│  │                                                      │    │
│  │  ┌────────────────────────────────────────────┐     │    │
│  │  │ 💡 MEDIUM VALUE | Supplier Diversification │     │    │
│  │  │                                             │     │    │
│  │  │ Multiple new suppliers entering market     │     │    │
│  │  │ with competitive pricing                    │     │    │
│  │  │                                             │     │    │
│  │  │ Potential Value: 6.5/10 | Feasibility: 90% │     │    │
│  │  │ Cost Savings Estimate: 10-15%               │     │    │
│  │  │                                             │     │    │
│  │  │ [View Full Details] [I'm Interested]        │     │    │
│  │  └────────────────────────────────────────────┘     │    │
│  │                                                      │    │
│  │  [... More opportunities ...]                       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Opportunity Card Features:**

```yaml
Display Components:
  Header:
    - Value indicator (High/Medium/Low)
    - Opportunity title
  
  Description:
    - Clear explanation of opportunity
    - Why it's relevant to this business
  
  Metrics:
    - Potential Value: 0-10 scale
    - Feasibility: 0-100%
    - Strategic Fit: 0-100%
    - Timing: Window of opportunity
  
  Context:
    - "Why Now" explanation
    - Requirements to capture
    - Estimated costs/resources
  
  Actions:
    - I'm Interested: Track intent, show action plan
    - View Full Details: Open modal with complete analysis
    - Not Relevant: Dismiss and learn preferences
    - Remind Me Later: Snooze for X days

User Engagement Tracking:
  - Track which opportunities clicked
  - Track "interested" vs "not relevant" patterns
  - Learn user preferences over time
  - Improve future opportunity relevance
```

---

### **Page 5: Operational Indicators**

**Purpose:** Show current state of all operational health metrics

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Operational Health Indicators                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Overall Status: GOOD (72/100)                      │    │
│  │  ↓ 5 points from last week                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Indicator Categories                               │    │
│  │  [All] [Improving] [Declining] [Stable]            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Supply Chain Health                        85/100  │    │
│  │  ████████████████████████░░░░░               ✅     │    │
│  │  ↑ Improving | Last 7 days                          │    │
│  │                                                      │    │
│  │  Contributing Factors:                              │    │
│  │  • Supplier Reliability: 90/100 (↑)                 │    │
│  │  • Import Clearance Time: 78/100 (→)                │    │
│  │  • Transport Availability: 88/100 (↑)               │    │
│  │  [View Details]                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Workforce Readiness                        68/100  │    │
│  │  ████████████████████░░░░░░░░░               ⚠️     │    │
│  │  ↓ Declining | Last 7 days                          │    │
│  │                                                      │    │
│  │  Contributing Factors:                              │    │
│  │  • Transport Accessibility: 55/100 (↓)              │    │
│  │  • Power Availability: 72/100 (↓)                   │    │
│  │  • Safety Conditions: 85/100 (→)                    │    │
│  │  [View Details]                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Financial Stability                        74/100  │    │
│  │  █████████████████████░░░░░░░░               ✅     │    │
│  │  → Stable | Last 7 days                             │    │
│  │  [View Details]                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  [... More indicator categories ...]                        │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Trend Over Time (Last 30 Days)                     │    │
│  │  [Multi-line chart showing all categories]          │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Indicator Display Features:**

```yaml
Indicator Card:
  Header:
    - Category name
    - Current score (0-100)
    - Status icon (✅⚠️❌)
  
  Progress Bar:
    - Visual score representation
    - Color-coded (green/yellow/red)
  
  Trend:
    - Trend direction (↑↓→)
    - Time context (last 7 days)
  
  Contributing Factors:
    - 3-5 sub-indicators
    - Each with own score and trend
    - Shows what's driving overall score
  
  Details Button:
    - Opens modal with:
      * Historical trend chart
      * Detailed breakdown
      * What affects this indicator
      * Related risks/opportunities

Filtering:
  All: Show all indicators
  Improving: Only indicators trending up
  Declining: Only indicators trending down
  Stable: Only stable indicators

Trend Chart:
  Type: Multi-line chart
  Lines: One per major category (5-7 lines)
  Time Range: Last 30 days
  Interactions:
    - Hover: Show exact values
    - Click legend: Toggle line visibility
    - Zoom: Adjustable time range
```

---

### **Page 6: Alerts & Notifications**

**Purpose:** Centralized view of all alerts, both active and historical

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Alerts & Notifications              [Mark All as Read]     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Active Alerts (8)                                  │    │
│  │  [All] [Unread (5)] [Critical (2)] [High (3)]      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  🔴 CRITICAL | 2 hours ago                UNREAD   │    │
│  │                                                      │    │
│  │  Fuel Shortage Alert                                │    │
│  │  Critical fuel shortage detected in Western Province│    │
│  │  affecting your delivery operations.                │    │
│  │                                                      │    │
│  │  Recommended Actions:                               │    │
│  │  1. Postpone non-urgent deliveries                  │    │
│  │  2. Notify customers of potential delays            │    │
│  │  3. Coordinate with alternative suppliers           │    │
│  │                                                      │    │
│  │  [View Full Details] [Mark as Read] [Dismiss]       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  ⚠️ HIGH | 5 hours ago                   READ      │    │
│  │                                                      │    │
│  │  Currency Volatility Warning                        │    │
│  │  LKR depreciation accelerating...                   │    │
│  │                                                      │    │
│  │  [View Details] [Dismiss]                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  [... More alerts ...]                                      │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Alert History                                      │    │
│  │  [Last 7 days ▼]                                    │    │
│  │                                                      │    │
│  │  Resolved Alerts: 23                                │    │
│  │  Dismissed Alerts: 12                               │    │
│  │  [View History]                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Notification Settings                              │    │
│  │  [Configure Alert Preferences]                      │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Alert Management Features:**

```yaml
Alert Card:
  Header:
    - Severity icon and level
    - Time received
    - Read/Unread badge
  
  Content:
    - Alert title (bold)
    - Summary (2-3 sentences)
    - Recommended actions (if available)
  
  Actions:
    - View Full Details: Open complete analysis
    - Mark as Read: Update status
    - Dismiss: Archive alert
  
  Visual States:
    - Unread: Bold text, highlighted background
    - Read: Normal text, standard background
    - Dismissed: Grayed out, moved to history

Filtering:
  By Status:
    - All alerts
    - Unread only
    - Read only
  
  By Severity:
    - All
    - Critical
    - High
    - Medium
  
  By Time:
    - Today
    - Last 7 days
    - Last 30 days
    - Custom range

Notification Settings:
  Channels:
    - Email: On/Off + Frequency
    - SMS: On/Off + Minimum severity
    - Dashboard: Always on
  
  Quiet Hours:
    - Start time (e.g., 10 PM)
    - End time (e.g., 7 AM)
    - Override for critical alerts: Yes/No
  
  Frequency:
    - Real-time (as they happen)
    - Digest (hourly/daily)
    - Summary only (daily/weekly)
```

---

### **Page 7: Reports**

**Purpose:** Generate and download custom reports

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Reports & Analytics                                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Quick Reports (Pre-configured)                     │    │
│  │                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │    │
│  │  │ Daily        │  │ Weekly       │  │ Monthly   │ │    │
│  │  │ Summary      │  │ Report       │  │ Overview  │ │    │
│  │  │              │  │              │  │           │ │    │
│  │  │ [Generate]   │  │ [Generate]   │  │[Generate] │ │    │
│  │  │ [Schedule]   │  │ [Schedule]   │  │[Schedule] │ │    │
│  │  └──────────────┘  └──────────────┘  └───────────┘ │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Custom Report Builder                              │    │
│  │                                                      │    │
│  │  Report Type:                                       │    │
│  │  ○ Risk Analysis                                    │    │
│  │  ○ Opportunity Summary                              │    │
│  │  ○ Indicator Trends                                 │    │
│  │  ○ Complete Business Health                         │    │
│  │                                                      │    │
│  │  Time Period:                                       │    │
│  │  [Start Date] to [End Date]                         │    │
│  │                                                      │    │
│  │  Include:                                           │    │
│  │  ☑ Executive Summary                                │    │
│  │  ☑ Key Insights                                     │    │
│  │  ☑ Trend Charts                                     │    │
│  │  ☑ Recommendations                                  │    │
│  │  ☐ Detailed Data Tables                             │    │
│  │  ☐ Appendix (Raw Data)                              │    │
│  │                                                      │    │
│  │  Format:                                            │    │
│  │  ○ PDF  ○ Excel  ○ CSV                             │    │
│  │                                                      │    │
│  │  [Generate Report]                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Recent Reports                                     │    │
│  │                                                      │    │
│  │  ┌────────────────────────────────────────────┐     │    │
│  │  │ Dec 5, 2025 | Weekly Report           PDF │     │    │
│  │  │ Generated 2 hours ago                      │     │    │
│  │  │ [Download] [View] [Regenerate]             │     │    │
│  │  └────────────────────────────────────────────┘     │    │
│  │                                                      │    │
│  │  [... More reports ...]                             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Scheduled Reports                                  │    │
│  │                                                      │    │
│  │  Daily Summary - Every day at 8:00 AM               │    │
│  │  Email to: owner@company.com                        │    │
│  │  [Edit] [Pause] [Delete]                            │    │
│  │                                                      │    │
│  │  [+ Add New Schedule]                               │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Report Generation Features:**

```yaml
Quick Reports:
  Daily Summary:
    Content:
      - Today's key insights (top 3)
      - Critical alerts
      - Health score with trend
      - Quick actions recommended
    Format: PDF (1-2 pages)
  
  Weekly Report:
    Content:
      - Week overview
      - All insights generated
      - Indicator trends
      - Actions taken vs recommended
    Format: PDF (5-7 pages) or Excel
  
  Monthly Overview:
    Content:
      - Month summary
      - Performance vs previous month
      - Key achievements
      - Strategic recommendations
    Format: PDF (10-15 pages)

Custom Report Builder:
  Report Types:
    - Risk Analysis: All risks with trends
    - Opportunity Summary: All opportunities
    - Indicator Trends: Charts and data
    - Complete Health: Everything combined
  
  Customization Options:
    - Date range selection
    - Include/exclude sections
    - Chart types
    - Detail level (summary/detailed/full)
    - Comparison periods (vs last week/month)
  
  Output Formats:
    - PDF: Professional, shareable
    - Excel: Data analysis, customization
    - CSV: Raw data export

Scheduled Reports:
  Configuration:
    - Report type (any quick or custom)
    - Frequency (daily/weekly/monthly)
    - Time of day
    - Recipients (email addresses)
    - Format
  
  Management:
    - Edit schedule
    - Pause temporarily
    - Delete schedule
    - View delivery history
```

---

### **Page 8: Company Settings**

**Purpose:** Manage company profile, preferences, and team

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│  Company Settings                                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Company Profile] [Alert Settings] [Team] [Integrations]   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Company Profile                                    │    │
│  │                                                      │    │
│  │  Company Name: ABC Retail Pvt Ltd                   │    │
│  │  Industry: Retail & E-commerce                      │    │
│  │  Business Scale: Medium (51-250 employees)          │    │
│  │  Location: Western Province, Colombo                │    │
│  │                                                      │    │
│  │  [Edit Profile]                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Operational Sensitivity Settings                   │    │
│  │                                                      │    │
│  │  Import Dependency: ████████░░ 60%                  │    │
│  │  Fuel Dependency: Critical                          │    │
│  │  Currency Sensitivity: ████████░░ 8/10              │    │
│  │                                                      │    │
│  │  [Adjust Settings]                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Alert Configuration                                │    │
│  │                                                      │    │
│  │  Notification Channels:                             │    │
│  │  ☑ Dashboard (always on)                            │    │
│  │  ☑ Email (owner@company.com)                        │    │
│  │  ☑ SMS (+94 77 123 4567)                            │    │
│  │                                                      │    │
│  │  Frequency: Daily digest at 8:00 AM                 │    │
│  │                                                      │    │
│  │  Minimum Severity: High and above                   │    │
│  │                                                      │    │
│  │  [Update Settings]                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Team Management                                    │    │
│  │                                                      │    │
│  │  ┌────────────────────────────────────────────┐     │    │
│  │  │ Name           Role          Status        │     │    │
│  │  ├────────────────────────────────────────────┤     │    │
│  │  │ John Doe       Owner         Active  [✎]  │     │    │
│  │  │ Jane Smith     Manager       Active  [✎]  │     │    │
│  │  │ Bob Wilson     Viewer        Active  [✎]  │     │    │
│  │  └────────────────────────────────────────────┘     │    │
│  │                                                      │    │
│  │  [+ Invite Team Member]                             │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. API SPECIFICATIONS {#api-specs}

### **API Architecture:**

```yaml
Base URL: https://api.yourplatform.com/v1

Authentication:
  Type: JWT Bearer Token
  Header: Authorization: Bearer <token>
  Expiry: 24 hours
  Refresh: Available via /auth/refresh endpoint

Rate Limiting:
  Admin Users: 1000 requests/hour
  Business Users: 500 requests/hour
  Response Header: X-RateLimit-Remaining

Error Format:
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human readable message",
      "details": {}
    }
  }
```

### **Admin Dashboard APIs:**

```yaml
GET /admin/system/health
  Description: System health overview
  Response:
    {
      "status": "healthy|degraded|down",
      "uptime_percent": 99.8,
      "active_users": 127,
      "pipeline_status": "running|paused|error",
      "last_updated": "2025-12-05T10:30:00Z"
    }

GET /admin/pipeline/current
  Description: Current pipeline cycle status
  Response:
    {
      "cycle_id": "cycle_12345",
      "status": "running|completed|failed",
      "started_at": "2025-12-05T10:30:00Z",
      "elapsed_seconds": 135,
      "layers": [
        {
          "layer": 1,
          "status": "completed",
          "articles_collected": 43,
          "duration_seconds": 90
        },
        {
          "layer": 2,
          "status": "running",
          "progress_percent": 65
        }
      ]
    }

GET /admin/agents/performance
  Parameters:
    - time_range: "today"|"7days"|"30days"
  Response:
    {
      "summary": {
        "total_decisions": 487,
        "success_rate": 98.3,
        "avg_latency_ms": 1200,
        "total_cost_usd": 0.00
      },
      "agents": [
        {
          "name": "Source Monitor",
          "calls": 127,
          "success_rate": 100,
          "avg_latency_ms": 800
        }
      ]
    }

GET /admin/logs
  Parameters:
    - level: "info"|"warning"|"error"|"critical"
    - component: "layer1"|"layer2"|...
    - search: "text query"
    - limit: 50
    - offset: 0
  Response:
    {
      "total": 1247,
      "logs": [
        {
          "timestamp": "2025-12-05T10:35:42Z",
          "level": "warning",
          "component": "layer1",
          "message": "Source failed to scrape",
          "details": {}
        }
      ]
    }

GET /admin/stats/collection
  Parameters:
    - time_range: "24h"|"7d"|"30d"
  Response:
    {
      "total_articles": 1247,
      "unique_articles": 1089,
      "dedup_rate": 87,
      "sources": [
        {
          "name": "Daily Mirror",
          "status": "healthy",
          "success_rate": 100,
          "avg_scrape_time_seconds": 2.3
        }
      ],
      "by_category": {
        "political": 35,
        "economic": 28,
        "social": 15
      }
    }
```

### **Business Dashboard APIs:**

```yaml
POST /auth/login
  Body:
    {
      "email": "user@company.com",
      "password": "password123"
    }
  Response:
    {
      "token": "eyJhbGc...",
      "refresh_token": "refresh_token_here",
      "user": {
        "id": 123,
        "email": "user@company.com",
        "role": "BUSINESS_USER",
        "company_id": 456,
        "company_name": "ABC Retail"
      }
    }

GET /business/dashboard/home
  Description: Dashboard home page data
  Response:
    {
      "health_score": {
        "current": 72,
        "change": -5,
        "status": "good"
      },
      "summary": {
        "critical_risks": 2,
        "high_risks": 5,
        "opportunities": 3
      },
      "recent_insights": [
        {
          "id": 789,
          "type": "risk",
          "severity": "critical",
          "title": "Fuel shortage expected",
          "summary": "...",
          "created_at": "2025-12-05T08:30:00Z"
        }
      ]
    }

GET /business/risks
  Parameters:
    - severity: "critical"|"high"|"medium"|"all"
    - category: "operational"|"financial"|...
    - status: "active"|"acknowledged"|"resolved"
  Response:
    {
      "total": 15,
      "summary": {
        "critical": 2,
        "high": 5,
        "medium": 8
      },
      "risks": [
        {
          "id": 123,
          "name": "Supply Chain Disruption",
          "description": "...",
          "severity": "critical",
          "probability": 85,
          "impact": "critical",
          "time_horizon": "24-48 hours",
          "confidence": 82,
          "affected_operations": ["deliveries"],
          "created_at": "2025-12-05T08:30:00Z"
        }
      ]
    }

GET /business/risks/:id
  Description: Detailed risk information
  Response:
    {
      "id": 123,
      "name": "...",
      "description": "...",
      "full_analysis": "Complete LLM output...",
      "metrics": {...},
      "recommendations": {
        "immediate": [...],
        "short_term": [...],
        "medium_term": [...]
      },
      "history": [...]
    }

GET /business/opportunities
  Parameters:
    - value: "high"|"medium"|"low"|"all"
    - status: "active"|"interested"|"dismissed"
  Response:
    {
      "total": 11,
      "opportunities": [
        {
          "id": 456,
          "name": "Export Tax Incentive",
          "description": "...",
          "potential_value": 8.5,
          "feasibility": 75,
          "strategic_fit": 85,
          "timing": "Next 2 weeks",
          "requirements": {...}
        }
      ]
    }

GET /business/indicators
  Description: All operational indicators
  Response:
    {
      "overall_score": 72,
      "categories": [
        {
          "name": "Supply Chain Health",
          "score": 85,
          "trend": "improving",
          "sub_indicators": [
            {
              "name": "Supplier Reliability",
              "score": 90,
              "trend": "improving"
            }
          ]
        }
      ]
    }

GET /business/alerts
  Parameters:
    - status: "unread"|"read"|"all"
    - severity: "critical"|"high"|...
  Response:
    {
      "unread_count": 5,
      "alerts": [
        {
          "id": 789,
          "severity": "critical",
          "title": "Fuel Shortage Alert",
          "message": "...",
          "recommendations": [...],
          "is_read": false,
          "created_at": "2025-12-05T08:30:00Z"
        }
      ]
    }

POST /business/alerts/:id/mark-read
  Description: Mark alert as read
  Response: {"success": true}

POST /business/company/profile
  Description: Update company profile
  Body:
    {
      "company_name": "...",
      "industry": "...",
      "import_dependency": 60,
      ...
    }
  Response: {"success": true, "profile": {...}}

POST /business/reports/generate
  Body:
    {
      "type": "weekly"|"monthly"|"custom",
      "start_date": "2025-12-01",
      "end_date": "2025-12-05",
      "format": "pdf"|"excel"|"csv",
      "sections": ["summary", "risks", "opportunities"]
    }
  Response:
    {
      "report_id": "report_123",
      "status": "generating",
      "estimated_time_seconds": 30
    }

GET /business/reports/:id/download
  Description: Download generated report
  Response: File download (PDF/Excel/CSV)
```

### **Real-time WebSocket Events:**

```yaml
Connection: ws://api.yourplatform.com/ws

Authentication:
  Send token on connect:
    {
      "type": "auth",
      "token": "jwt_token_here"
    }

Admin Events:
  system.status_changed:
    {
      "event": "system.status_changed",
      "data": {
        "status": "degraded",
        "reason": "Database connection slow"
      }
    }
  
  pipeline.started:
    {"event": "pipeline.started", "data": {...}}
  
  pipeline.completed:
    {"event": "pipeline.completed", "data": {...}}
  
  agent.decision:
    {"event": "agent.decision", "data": {...}}
  
  error.occurred:
    {"event": "error.occurred", "data": {...}}

Business User Events:
  insight.created:
    {
      "event": "insight.created",
      "data": {
        "type": "risk",
        "severity": "critical",
        "insight": {...}
      }
    }
  
  alert.new:
    {"event": "alert.new", "data": {...}}
  
  indicator.updated:
    {"event": "indicator.updated", "data": {...}}
  
  health_score.changed:
    {
      "event": "health_score.changed",
      "data": {
        "old_score": 75,
        "new_score": 72
      }
    }
```

---

This completes the comprehensive specifications. Part 2 document created successfully!

**Would you like me to continue with:**
- Integration patterns
- Performance optimization
- Security implementation
- Testing strategies
- Deployment guide

Or is this sufficient for your team to start building?
