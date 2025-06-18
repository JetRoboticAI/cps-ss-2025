import React, { useState, useEffect } from 'react';
import { useNFC } from '../hooks/useNFC';
import Button from './Button';

const NFCReader = () => {
  const [isScanning, setIsScanning] = useState(false);
  const { nfcData, error, startScan, stopScan } = useNFC();

  useEffect(() => {
    if (isScanning) {
      startScan();
    } else {
      stopScan();
    }

    return () => {
      stopScan();
    };
  }, [isScanning, startScan, stopScan]);

  const handleScanToggle = () => {
    setIsScanning(!isScanning);
  };

  return (
    <div className="status-container">
      <h2>NFC Reader</h2>
      <Button
        onClick={handleScanToggle}
        text={isScanning ? 'Cancel Scan' : 'Start NFC Scan'}
        variant={isScanning ? 'secondary' : 'primary'}
        disabled={!!error}
      />

      {error && (
        <div className="status-error">
          <p>{error}</p>
        </div>
      )}

      {nfcData && (
        <div className={`status-${nfcData.success ? 'success' : 'error'}`}>
          <h3>NFC Scan Results:</h3>
          <p>{nfcData.message}</p>
          {nfcData.tagId && (
            <p className="tag-id">Tag ID: {nfcData.tagId}</p>
          )}
          <p className="timestamp">
            {new Date(nfcData.timestamp).toLocaleString()}
          </p>
        </div>
      )}

      {isScanning && !error && (
        <div className="scanner-animation">
          <p>Please tap your NFC card...</p>
        </div>
      )}
    </div>
  );
};

export default NFCReader;