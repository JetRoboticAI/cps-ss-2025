import React, { useState } from 'react';
import RecognitionResult from './RecognitionResult';
import History from './History';
import UnlockButton from './UnlockButton';
import Settings from './Settings';
import { logout } from '../utils/auth';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      <div className="top-bar">
        <h1 className="project-title">Smart Lock System</h1>
        <div className="top-bar-actions">
          <button 
            className="history-button"
            onClick={() => setShowHistory(!showHistory)}
          >
            {showHistory ? 'Hide History' : 'Show History'}
          </button>
          <button 
            className="history-button"
            onClick={() => setShowSettings(true)}
          >
            Settings
          </button>
          <button 
            className="logout-button"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>
      <div className={`app-container ${showHistory ? 'with-sidebar' : ''}`}>
        <UnlockButton />
        <div className="recognitions-container">
          <div className="recognition-section">
            <h2>RFID Recognition</h2>
            <div className="status-display">
              <RecognitionResult type="rfid" />
            </div>
          </div>
          {/* <div className="recognition-section">
            <h2>Face Recognition</h2>
            <div className="status-display">
              <RecognitionResult type="face" />
            </div>
          </div>
          <div className="recognition-section">
            <h2>Fingerprint Recognition</h2>
            <div className="status-display">
              <RecognitionResult type="fingerprint" />
            </div>
          </div> */}
        </div>

        {showHistory && (
          <div className="sidebar">
            <History onClose={() => setShowHistory(false)} />
          </div>
        )}
      </div>

      {showSettings && (
        <Settings onClose={() => setShowSettings(false)} />
      )}
    </>
  );
};

export default Dashboard;