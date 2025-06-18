import React, { useState, useEffect } from 'react';
import { useBiometrics } from '../hooks/useBiometrics';
import Button from './Button';

const FingerPrint = () => {
  const [isScanning, setIsScanning] = useState(false);
  const { recognitionData, startRecognition, stopRecognition } = useBiometrics();

  useEffect(() => {
    if (isScanning) {
      startRecognition('fingerprint'); // Specify the recognition type
    } else {
      stopRecognition('fingerprint');
    }

    return () => {
      stopRecognition('fingerprint');
    };
  }, [isScanning, startRecognition, stopRecognition]);

  const handleScanToggle = () => {
    setIsScanning(!isScanning);
  };

  return (
    <div className="status-container">
      <h2>Fingerprint Scanner</h2>
      <Button
        onClick={handleScanToggle}
        text={isScanning ? 'Cancel Scan' : 'Start Scan'}
        variant={isScanning ? 'secondary' : 'primary'}
      />
      
      {recognitionData && recognitionData.type === 'fingerprint' && (
        <div className={`status-${recognitionData.success ? 'success' : 'error'}`}>
          <h3>Scan Results:</h3>
          <p>{recognitionData.message}</p>
          {recognitionData.matchPercentage && (
            <p className="match-percentage">Match: {recognitionData.matchPercentage}%</p>
          )}
          <p className="timestamp">
            {new Date(recognitionData.timestamp).toLocaleString()}
          </p>
        </div>
      )}

      {isScanning && (
        <div className="scanner-animation">
          <p>Place your finger on the scanner...</p>
        </div>
      )}
    </div>
  );
};

export default FingerPrint;