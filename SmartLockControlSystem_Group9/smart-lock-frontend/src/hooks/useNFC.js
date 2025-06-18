import { useState, useCallback, useEffect, useRef } from 'react';
import { usePubNub } from 'pubnub-react';
import { CHANNEL } from '../index';

export const useNFC = () => {
  const pubnub = usePubNub();
  const [nfcData, setNfcData] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);
  const cleanupRef = useRef(null);

  const startScan = useCallback(async () => {
    try {
      setIsScanning(true);
      setError(null);

      await pubnub.publish({
        channel: CHANNEL,
        message: {
          type: 'NFC',
          command: 'START_SCAN',
          timestamp: new Date().toISOString()
        }
      });
    } catch (err) {
      setError('Failed to start NFC scan: ' + err.message);
      console.error('NFC scan error:', err);
      setIsScanning(false);
    }
  }, [pubnub]);

  const stopScan = useCallback(async () => {
    try {
      await pubnub.publish({
        channel: CHANNEL,
        message: {
          type: 'NFC',
          command: 'STOP_SCAN',
          timestamp: new Date().toISOString()
        }
      });

      setNfcData(null);
      setIsScanning(false);
    } catch (err) {
      setError('Failed to stop NFC scan: ' + err.message);
      console.error('NFC stop error:', err);
    }
  }, [pubnub]);

  useEffect(() => {
    const handleMessage = (event) => {
      if (event.channel === CHANNEL && event.message.type === 'NFC') {
        setNfcData({
          success: event.message.success,
          message: event.message.message,
          tagId: event.message.tagId,
          timestamp: new Date().toISOString()
        });
      }
    };

    pubnub.addListener({ message: handleMessage });
    cleanupRef.current = handleMessage;

    return () => {
      pubnub.removeListener({ message: cleanupRef.current });
    };
  }, [pubnub]);

  // Separate effect for handling scanning state cleanup
  useEffect(() => {
    return () => {
      if (isScanning) {
        stopScan();
      }
    };
  }, [isScanning, stopScan]);

  return {
    nfcData,
    isScanning,
    error,
    startScan,
    stopScan
  };
};

export default useNFC;