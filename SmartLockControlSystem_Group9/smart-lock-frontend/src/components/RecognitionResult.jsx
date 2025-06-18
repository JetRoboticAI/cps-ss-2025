import React, { useState } from 'react';
import { usePubNub } from 'pubnub-react';
import { getChannel } from '../utils/pubnub-config';

const RecognitionResult = ({ type }) => {
  const [lastActivity, setLastActivity] = useState(null);
  const pubnub = usePubNub();

  React.useEffect(() => {
    const channel = getChannel();

    const handleMessage = (msg) => {
      if (msg.message.message_type === 'status' && msg.message.type === type) {
        setLastActivity({
          name: msg.message.name,
          time: new Date(msg.message.time * 1000).toLocaleString(),
          state: msg.message.state
        });
      }
    };

    pubnub.subscribe({ channels: [channel] });
    pubnub.addListener({ message: handleMessage });

    return () => {
      pubnub.removeListener({ message: handleMessage });
      pubnub.unsubscribe({ channels: [channel] });
    };
  }, [pubnub, type]);

  return (
    <div className="recognition-result">
      {lastActivity ? (
        <>
          <p className="name">{lastActivity.name}</p>
          <p className="time">{lastActivity.time}</p>
          <p className={`status ${lastActivity.state === 1 ? 'success' : 'error'}`}>
            {lastActivity.state === 1 ? 'Unlock' : 'Block Access'}
          </p>
        </>
      ) : (
        <p>No recent activity</p>
      )}
    </div>
  );
};

export default RecognitionResult;