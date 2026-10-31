import React, { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [selectedPhoneme, setSelectedPhoneme] = useState('R');
  const [activeTargetWord, setActiveTargetWord] = useState('');
  
  // Default demo child session
  const defaultUser = {
    id: 2,
    username: 'child_leo',
    full_name: 'Leo Miller',
    role: 'child',
    child_id: 1,
    stars: 45,
    streak_days: 5,
    avatar: 'fox',
    age: 7,
    diagnosis: 'Speech Sound Disorder - Rhotic /r/ & Sibilant /s/'
  };

  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('speechsense_user');
      return saved ? JSON.parse(saved) : defaultUser;
    } catch {
      return defaultUser;
    }
  });

  const [patientInfo, setPatientInfo] = useState({
    name: user?.full_name || 'Leo Miller',
    age: user?.age || 7,
    sessionType: 'Acoustic Phoneme Assessment',
    therapist: 'Dr. Sarah Jenkins, CCC-SLP',
  });

  useEffect(() => {
    if (user) {
      localStorage.setItem('speechsense_user', JSON.stringify(user));
      setPatientInfo(prev => ({
        ...prev,
        name: user.full_name,
        age: user.age || 7
      }));
    } else {
      localStorage.removeItem('speechsense_user');
    }
  }, [user]);

  function loginUser(userData) {
    setUser(userData);
  }

  function logoutUser() {
    setUser(null);
  }

  function addStars(count) {
    if (user && user.role === 'child') {
      setUser(prev => ({
        ...prev,
        stars: (prev.stars || 0) + count
      }));
    }
  }

  return (
    <AppContext.Provider value={{
      analysisResult,
      setAnalysisResult,
      user,
      loginUser,
      logoutUser,
      addStars,
      patientInfo,
      setPatientInfo,
      selectedPhoneme,
      setSelectedPhoneme,
      activeTargetWord,
      setActiveTargetWord
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  return useContext(AppContext);
}
