import { useState, useCallback, useEffect } from 'react';
import { usePubNub } from 'pubnub-react';
import { CHANNEL } from '../index';

export const useBiometrics = () => {
    const pubnub = usePubNub();
    const [recognitionData, setRecognitionData] = useState(null);

    // Set up listener when hook is initialized
    useEffect(() => {
        const handleMessage = (event) => {
            if (event.channel === CHANNEL) {
                setRecognitionData({
                    success: event.message.success,
                    message: event.message.message,
                    matchPercentage: event.message.matchPercentage,
                    type: event.message.type
                });
            }
        };

        pubnub.addListener({ message: handleMessage });

        return () => {
            pubnub.removeListener({ message: handleMessage });
        };
    }, [pubnub]);

    const startRecognition = useCallback((type) => {
        pubnub.publish({
            channel: CHANNEL,
            message: {
                command: 'START_RECOGNITION',
                type: type,
                timestamp: new Date().toISOString()
            }
        });
    }, [pubnub]);

    const stopRecognition = useCallback((type) => {
        pubnub.publish({
            channel: CHANNEL,
            message: {
                command: 'STOP_RECOGNITION',
                type: type,
                timestamp: new Date().toISOString()
            }
        });

        setRecognitionData(null);
    }, [pubnub]);

    return {
        recognitionData,
        startRecognition,
        stopRecognition
    };
};