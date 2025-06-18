import { useState, useCallback, useEffect } from 'react';
import { usePubNub } from 'pubnub-react';
import { getChannel } from '../utils/pubnub-config';

export const useHistory = () => {
    const pubnub = usePubNub();
    const channel = getChannel();
    const [history, setHistory] = useState([]);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const getActivityName = (message) => {
        if (message.state === 0) {
            switch (message.type) {
                case 'remote':
                    return 'Remote Access';
                case 'rfid':
                    return 'RFID Card';
                case 'face':
                    return 'Face Recognition';
                case 'fingerprint':
                    return 'Fingerprint';
                default:
                    return 'Unknown';
            }
        }
        return message.name || 'Unknown';
    };

    const fetchLogs = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const result = await pubnub.history({
                channel: channel,
                count: 100,
                stringifiedTimeToken: true
            });

            const formattedLogs = result.messages.map(item => {
                const message = item.entry || item.message;
                const activityStatus = message.state === 1 ? 'Access Granted' : 'Access Denied';
                const activityName = getActivityName(message);
                const activityType = message.type || 'Unknown';

                return {
                    id: item.timetoken,
                    timestamp: new Date(parseInt(item.timetoken / 10000)).toISOString(),
                    type: activityType,
                    success: message.state === 1,
                    message: `${activityType} - ${activityStatus}`,
                    name: activityName,
                    state: message.state
                };
            });

            setLogs(formattedLogs);
        } catch (error) {
            setError('Failed to fetch access logs: ' + error.message);
            console.error('Failed to fetch access logs:', error);
        } finally {
            setLoading(false);
        }
    }, [pubnub, channel]);

    useEffect(() => {
        const handleMessage = (event) => {
            if (event.channel === channel && event.message.message_type === 'status') {
                const message = event.message;
                const activityStatus = message.state === 1 ? 'Access Granted' : 'Access Denied';
                const activityName = getActivityName(message);
                const activityType = message.type || 'Unknown';

                setLogs(prevLogs => [{
                    id: event.timetoken,
                    timestamp: new Date(parseInt(event.timetoken / 10000)).toISOString(),
                    type: activityType,
                    success: message.state === 1,
                    message: `${activityType} - ${activityStatus}`,
                    name: activityName,
                    state: message.state
                }, ...prevLogs]);
            }
        };

        pubnub.addListener({
            message: handleMessage
        });

        // Initial fetch
        fetchLogs();

        return () => {
            pubnub.removeListener({ message: handleMessage });
        };
    }, [pubnub, fetchLogs, channel]);

    const clearLogs = useCallback(() => {
        setLogs([]);
    }, []);

    return {
        logs,
        loading,
        error,
        fetchLogs,
        clearLogs
    };
};

export default useHistory;