import React, { useEffect, useState } from "react";
import { useHistory } from "../hooks/useHistory";
import Button from "./Button";

const History = ({ onClose }) => {
  const { logs, loading, error, fetchLogs } = useHistory();
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const filterLogs = (logs) => {
    if (!logs) return [];
    if (filter === "all") return logs;
    return logs.filter((log) => log.type === filter);
  };

  return (
    <div className="sidebar-content">
      <div className="sidebar-header">
        <div className="header-actions">
          <button 
            className="history-button"
            onClick={onClose}
          >
            Close
          </button>
        </div>
        <h2>Access History</h2>
        <div className="header-actions">
          <button 
            className="history-button"
            onClick={fetchLogs}
            disabled={loading}
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="filter-controls">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="select"
          disabled={loading || !logs?.length}
        >
          <option value="all">All Activities</option>
          <option value="facial">Facial Recognition</option>
          <option value="nfc">NFC</option>
          <option value="remote">Remote Control</option>
          <option value="manual">Manual Unlock</option>
        </select>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
          <Button onClick={fetchLogs} text="Try Again" variant="primary" />
        </div>
      )}

      <div className="logs-wrapper">
        {loading ? (
          <div className="loading-state">
            <p>Loading access logs...</p>
          </div>
        ) : (
          <div className="logs-container">
            {filterLogs(logs).length === 0 ? (
              <div className="empty-state">
                <p>No access logs found</p>
              </div>
            ) : (
              filterLogs(logs).map((log) => (
                <div
                  key={log.id}
                  className={`log-entry ${
                    log.success ? "status-success" : "status-error"
                  }`}
                >
                  <div className="log-header">
                    <span className="log-type">{log.type}</span>
                    <span className="log-time">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>
                  <p className="log-message">{log.message}</p>
                  {log.user && <p className="log-user">User: {log.user}</p>}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
