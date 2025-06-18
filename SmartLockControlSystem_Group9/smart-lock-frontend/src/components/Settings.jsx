import React, { useState, useEffect } from 'react';
import { getDefaultConfig } from '../utils/pubnub-config';

const Settings = ({ onClose }) => {
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('pubnub_settings');
    return saved ? JSON.parse(saved) : getDefaultConfig();
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem('pubnub_settings', JSON.stringify(settings));
    alert('Settings saved! The page will reload to apply changes.');
    window.location.reload();
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="settings-overlay">
      <div className="settings-modal">
        <div className="settings-header">
          <h2>PubNub Settings</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>
        <form onSubmit={handleSubmit} className="settings-form">
          <div className="form-group">
            <label htmlFor="subscribeKey">Subscribe Key</label>
            <input
              type="text"
              id="subscribeKey"
              name="subscribeKey"
              value={settings.subscribeKey}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="publishKey">Publish Key</label>
            <input
              type="text"
              id="publishKey"
              name="publishKey"
              value={settings.publishKey}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="channel">Channel</label>
            <input
              type="text"
              id="channel"
              name="channel"
              value={settings.channel}
              onChange={handleChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="uuid">UUID</label>
            <input
              type="text"
              id="uuid"
              name="uuid"
              value={settings.uuid}
              onChange={handleChange}
              required
            />
          </div>
          <div className="settings-actions">
            <button type="submit" className="save-button">Save Settings</button>
            <button type="button" className="cancel-button" onClick={onClose}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Settings;