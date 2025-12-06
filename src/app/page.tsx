"use client";
import {useState} from "react";
import RiskOverviewPage from "@/components/Pages/RiskOverviewPage"
import OpportunitiesPage from "@/components/Pages/OpportunitiesPage"
import IndicatorsPage from "@/components/Pages/IndicatorsPage"
import AlertsPage from "@/components/Pages/AlertsPage"
import ReportsPage from "@/components/Pages/ReportsPage"
import SettingsPage from "@/components/Pages/SettingsPage"
import Navigation from "@/components/utility/Navigation"

export default function Dashboard() {
    const [activePage, setActivePage] = useState('risks');

    const renderPage = () => {
        switch (activePage) {
            case 'risks':
                return <RiskOverviewPage />;
            case 'opportunities':
                return <OpportunitiesPage />;
            case 'indicators':
                return <IndicatorsPage />;
            case 'alerts':
                return <AlertsPage />;
            case 'reports':
                return <ReportsPage />;
            case 'settings':
                return <SettingsPage />;
            default:
                return <RiskOverviewPage />;
        }
    };

    return (
        <div className="min-h-screen bg-slate-950">
            <Navigation activePage={activePage} onNavigate={setActivePage} />
            <main className="ml-64 p-8">
                {renderPage()}
            </main>
        </div>
    );
}
