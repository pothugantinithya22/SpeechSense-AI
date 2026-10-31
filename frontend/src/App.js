import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Navbar from './components/Navbar';
import GeminiChatbotWidget from './components/GeminiChatbotWidget';
import Home from './pages/Home';
import Login from './pages/Login';
import ChildDashboard from './pages/ChildDashboard';
import TherapistDashboard from './pages/TherapistDashboard';
import Analyze from './pages/AnalyzeLive';
import Feedback from './pages/FeedbackLive';
import ArticulationGuide from './pages/ArticulationGuide';
import ProgressAnalytics from './pages/ProgressAnalytics';
import TherapyPlanPage from './pages/TherapyPlanPage';
import Report from './pages/ReportLive';

export default function App() {
  return (
    <AppProvider>
      <Navbar />
      <Routes>
        <Route path="/"                    element={<Home />} />
        <Route path="/login"               element={<Login />} />
        <Route path="/child-dashboard"     element={<ChildDashboard />} />
        <Route path="/therapist-dashboard" element={<TherapistDashboard />} />
        <Route path="/analyze"             element={<Analyze />} />
        <Route path="/feedback"            element={<Feedback />} />
        <Route path="/articulation"        element={<ArticulationGuide />} />
        <Route path="/progress"            element={<ProgressAnalytics />} />
        <Route path="/therapy-plan"        element={<TherapyPlanPage />} />
        <Route path="/report"              element={<Report />} />
        <Route path="*"                    element={<Navigate to="/" replace />} />
      </Routes>
      <GeminiChatbotWidget />
    </AppProvider>
  );
}
