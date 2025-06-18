const API_BASE_URL = 'https://api.smartlocksystem.com';

export const unlockDoor = async () => {
    const response = await fetch(`${API_BASE_URL}/unlock`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    if (!response.ok) {
        throw new Error('Failed to unlock the door');
    }
    return response.json();
};

export const fetchHistory = async () => {
    const response = await fetch(`${API_BASE_URL}/history`);
    if (!response.ok) {
        throw new Error('Failed to fetch history');
    }
    return response.json();
};

export const verifyBiometrics = async (biometricData) => {
    const response = await fetch(`${API_BASE_URL}/verify`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(biometricData),
    });
    if (!response.ok) {
        throw new Error('Biometric verification failed');
    }
    return response.json();
};

export const verifyNFC = async (nfcData) => {
    const response = await fetch(`${API_BASE_URL}/verify-nfc`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(nfcData),
    });
    if (!response.ok) {
        throw new Error('NFC verification failed');
    }
    return response.json();
};

export const getSystemStatus = async () => {
    const response = await fetch(`${API_BASE_URL}/status`);
    if (!response.ok) {
        throw new Error('Failed to fetch system status');
    }
    return response.json();
};