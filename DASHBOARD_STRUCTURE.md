# Dashboard Structure Documentation

## Current Dashboard Implementation

### Location
**Primary Dashboard**: `src/app/dashboard/page.tsx`
- Uses Next.js App Router (Next.js 13+)
- Protected by authentication via `ProtectedRoute`
- Implements tab-based navigation with 4 main views

### Dashboard Tabs

1. **Overview Tab** (`overview`)
   - Admin statistics (total indicators, companies, insights, risks)
   - National Indicators grouped by PESTEL category (Layer 2)
   - Operational Indicators (Layer 3)
   - Business Insights (Layer 4)

2. **Data Collection Tab** (`layer1`)
   - Data Sources Monitor
   - Processing Pipeline Status
   - Scraping Jobs Panel
   - Raw Articles Stream

3. **Indicators & Analysis Tab** (`layer2`)
   - Indicator Analysis (Layer 2)
   - Operational Overview (Layer 3)

4. **System Health Tab** (`system`)
   - System health metrics (placeholder)

### Component Structure

```
src/app/dashboard/
├── page.tsx                          # Main dashboard page
└── components/
    ├── shared/                       # Shared UI components
    │   ├── Badge.tsx                 # PestelBadge, SeverityBadge, TrendArrow
    │   ├── DataTable.tsx
    │   ├── LoadingSkeleton.tsx
    │   └── StatCard.tsx
    ├── layer1/                       # Data Collection (Layer 1)
    │   ├── DataSourcesMonitor.tsx
    │   ├── ProcessingPipelineStatus.tsx
    │   ├── RawArticlesStream.tsx
    │   └── ScrapingJobsPanel.tsx
    ├── layer2/                       # National Indicators (Layer 2)
    │   ├── IndicatorAnalysis.tsx
    │   ├── NationalIndicatorList.tsx
    │   ├── BusinessInsightsPanel.tsx
    │   └── OperationalMetricsGrid.tsx
    └── layer3/                       # Operational Indicators (Layer 3)
        ├── OperationalOverview.tsx
        ├── OperationalIndicatorCard.tsx
        └── IndustryBreakdown.tsx
```

### API Integration

**API Service**: `src/lib/api/dashboard.ts`
**Hooks**: `src/hooks/useDashboard.ts`

Key API endpoints used:
- `GET /api/v1/admin/dashboard` - Admin overview stats
- `GET /api/v1/admin/indicators/national` - Layer 2 national indicators
- `GET /api/v1/admin/insights` - Layer 4 business insights
- `GET /api/v1/user/operations-data` - Layer 3 operational indicators
- `GET /api/v1/admin/companies` - Company list

### Type Definitions

**Location**: `src/lib/api/types.ts`

Key types:
- `AdminDashboard` - Admin overview response
- `NationalIndicator` - Layer 2 indicator structure
- `NationalIndicatorList` - List response wrapper
- `OperationalIndicator` - Layer 3 indicator structure
- `OperationalIndicatorListResponse` - Layer 3 list response wrapper
- `BusinessInsight` - Layer 4 insight structure
- `BusinessInsightList` - Layer 4 list response wrapper

## Archived Components

### Old Components (Moved to Archive)

**Location**: `src/components/_archive_old_pages/`

These components were part of an earlier implementation and are **NOT USED** in the current dashboard:
- `AlertsPage.tsx`
- `IndicatorsPage.tsx`
- `OpportunitiesPage.tsx`
- `ReportsPage.tsx`
- `RiskOverviewPage.tsx`
- `SettingsPage.tsx`

**Location**: `backend/app/static/_archive/dashboard.js`
- Old static HTML/JS dashboard for development testing

## Important Notes

1. **Single Source of Truth**: The current dashboard is `src/app/dashboard/page.tsx`
2. **No Pages Router**: This project uses Next.js App Router only (no `src/pages/` directory)
3. **Component Organization**: Components are organized by layer (layer1, layer2, layer3)
4. **Type Safety**: All API responses are typed in `src/lib/api/types.ts`
5. **Authentication**: Dashboard is protected via `ProtectedRoute` wrapper

## Troubleshooting

If you see different dashboard versions or conflicts:
1. Confirm you're accessing `/dashboard` route
2. Check that old archived components are not imported anywhere
3. Verify API types match backend schemas
4. Clear `.next` build cache if needed: `rm -rf .next`

## Last Updated
2025-12-12 - Cleaned up old dashboard components and documented structure
