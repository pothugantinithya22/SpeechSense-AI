import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import './Navbar.css';

export default function Navbar() {
  const { user, logoutUser } = useApp();
  const navigate = useNavigate();

  function handleLogout() {
    logoutUser();
    navigate('/login');
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <NavLink to="/" className="navbar-brand">
          <span className="brand-badge">SpeechSense</span>
          <span className="brand-tag">AI Clinical Suite</span>
        </NavLink>

        <div className="navbar-links">
          <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            Home
          </NavLink>

          <NavLink to="/child-dashboard" className={({ isActive }) => `nav-link child-link ${isActive ? 'active' : ''}`}>
            ⭐ Child Hub
          </NavLink>

          <NavLink to="/analyze" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            🎙️ Analyze Speech
          </NavLink>

          <NavLink to="/feedback" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            🎯 Feedback & Drills
          </NavLink>

          <NavLink to="/articulation" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            🗣️ Mouth Guide
          </NavLink>

          <NavLink to="/progress" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            📈 Progress
          </NavLink>

          <NavLink to="/therapy-plan" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            📋 Therapy Plan
          </NavLink>

          <NavLink to="/therapist-dashboard" className={({ isActive }) => `nav-link therapist-link ${isActive ? 'active' : ''}`}>
            🩺 Therapist Portal
          </NavLink>

          <NavLink to="/report" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            📄 Report
          </NavLink>
        </div>

        <div className="navbar-user">
          {user ? (
            <div className="user-profile-badge">
              <span className="user-avatar">
                {user.role === 'therapist' ? '🩺' : '🦊'}
              </span>
              <div className="user-meta">
                <span className="user-name">{user.full_name}</span>
                {user.role === 'child' && (
                  <span className="user-stars">⭐ {user.stars || 0} | 🔥 {user.streak_days || 1}d</span>
                )}
                {user.role === 'therapist' && (
                  <span className="user-role-label">SLP Clinician</span>
                )}
              </div>
              <button type="button" className="logout-btn" onClick={handleLogout} title="Switch User / Logout">
                Sign Out
              </button>
            </div>
          ) : (
            <NavLink to="/login" className="login-btn">
              Sign In
            </NavLink>
          )}
        </div>
      </div>
    </nav>
  );
}
