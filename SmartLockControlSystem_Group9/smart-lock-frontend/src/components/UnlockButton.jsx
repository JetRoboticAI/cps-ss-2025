import React, { useState } from 'react';
import { usePubNub } from 'pubnub-react';
import { getChannel } from '../utils/pubnub-config';

const UnlockButton = () => {
  const [isUnlocking, setIsUnlocking] = useState(false);
  const pubnub = usePubNub();

  const handleUnlock = async () => {
    setIsUnlocking(true);
    const channel = getChannel();

    try {
      await pubnub.publish({
        channel,
        message: {
          message_type: "control",
          action: "unlock",
          timestamp: new Date().toISOString()
        }
      });
    } catch (error) {
      console.error('Failed to send unlock command:', error);
    } finally {
      setIsUnlocking(false);
    }
  };

  return (
    <div className="unlock-container">
      <button 
        onClick={handleUnlock}
        disabled={isUnlocking}
        className="unlock-button"
      >
        {isUnlocking ? 'Unlocking...' : 'Unlock Door'}
      </button>
    </div>
  );
};

export default UnlockButton;