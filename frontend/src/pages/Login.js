import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { login, register } from '../lib/api';
import './Login.css';

export default function Login() {
  const navigate = useNavigate();
  const { loginUser } = useApp();

  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [role, setRole] = useState('child'); // 'child' or 'therapist'
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState(7);
  const [diagnosis, setDiagnosis] = useState('Speech Sound Disorder');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleAuth(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (mode === 'login') {
        const res = await login(username, password);
        loginUser(res.user);
        if (res.user.role === 'therapist') {
          navigate('/therapist-dashboard');
        } else {
          navigate('/child-dashboard');
        }
      } else {
        const res = await register({
          username,
          password,
          full_name: fullName,
          role,
          age: parseInt(age, 10),
          diagnosis
        });
        loginUser(res.user);
        if (role === 'therapist') {
          navigate('/therapist-dashboard');
        } else {
          navigate('/child-dashboard');
        }
      }
    } catch (err) {
      setError(err.message || 'Authentication failed.');
    } finally {
      setLoading(false);
    }
  }

  function handleDemoLogin(demoUsername, demoPassword) {
    setUsername(demoUsername);
    setPassword(demoPassword);
    login(demoUsername, demoPassword)
      .then(res => {
        loginUser(res.user);
        if (res.user.role === 'therapist') {
          navigate('/therapist-dashboard');
        } else {
          navigate('/child-dashboard');
        }
      })
      .catch(err => setError(err.message));
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="brand-logo-circle">🗣️</div>
          <h2>SpeechSense Portal</h2>
          <p className="login-desc">AI-Powered Pediatric Speech Sound Disorder Therapy</p>
        </div>

        {/* Instant Demo Quick Login Buttons */}
        <div className="demo-login-box">
          <span className="demo-title">⚡ Instant Demonstration Access</span>
          <div className="demo-btn-group">
            <button
              type="button"
              className="demo-pill-btn child-demo"
              onClick={() => handleDemoLogin('child_leo', 'leo123')}
            >
              🦊 Login as Child (Leo)
            </button>
            <button
              type="button"
              className="demo-pill-btn therapist-demo"
              onClick={() => handleDemoLogin('dr_sarah', 'therapist123')}
            >
              🩺 Login as Therapist (Dr. Sarah)
            </button>
          </div>
        </div>

        <div className="login-tabs">
          <button
            type="button"
            className={`tab-btn ${mode === 'login' ? 'active' : ''}`}
            onClick={() => { setMode('login'); setError(''); }}
          >
            Sign In
          </button>
          <button
            type="button"
            className={`tab-btn ${mode === 'register' ? 'active' : ''}`}
            onClick={() => { setMode('register'); setError(''); }}
          >
            Create Account
          </button>
        </div>

        {error && <div className="login-error-alert">{error}</div>}

        <form onSubmit={handleAuth} className="login-form">
          {mode === 'register' && (
            <>
              <div className="form-group">
                <label>I am a:</label>
                <div className="role-selector">
                  <button
                    type="button"
                    className={`role-btn ${role === 'child' ? 'selected' : ''}`}
                    onClick={() => setRole('child')}
                  >
                    Child / Parent
                  </button>
                  <button
                    type="button"
                    className={`role-btn ${role === 'therapist' ? 'selected' : ''}`}
                    onClick={() => setRole('therapist')}
                  >
                    Therapist (SLP)
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>Full Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Leo Miller"
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                />
              </div>

              {role === 'child' && (
                <div className="form-row">
                  <div className="form-group">
                    <label>Age</label>
                    <input
                      type="number"
                      min="3"
                      max="18"
                      value={age}
                      onChange={e => setAge(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Primary Diagnosis</label>
                    <input
                      type="text"
                      value={diagnosis}
                      onChange={e => setDiagnosis(e.target.value)}
                    />
                  </div>
                </div>
              )}
            </>
          )}

          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              required
              placeholder="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              required
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
            />
          </div>

          <button type="submit" className="submit-auth-btn" disabled={loading}>
            {loading ? 'Please wait...' : mode === 'login' ? 'Sign In to Portal' : 'Complete Registration'}
          </button>
        </form>
      </div>
    </div>
  );
}
