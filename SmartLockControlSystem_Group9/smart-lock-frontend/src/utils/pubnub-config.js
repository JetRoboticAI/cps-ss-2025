import PubNub from 'pubnub';
import env from '../config/environment';

export const getDefaultConfig = () => ({
  subscribeKey: 'demo',
  publishKey: 'demo',
  uuid: 'default-user',
  channel: 'demo-channel'
});

export const initializePubNub = () => {
  try {
    const settings = localStorage.getItem('pubnub_settings');
    if (settings) {
      const { subscribeKey, publishKey, uuid } = JSON.parse(settings);
      return new PubNub({
        subscribeKey,
        publishKey,
        uuid,
        ssl: true,
        logVerbosity: env.NODE_ENV === 'development' ? true : false
      });
    }
    const defaultConfig = getDefaultConfig();
    return new PubNub({
      subscribeKey: defaultConfig.subscribeKey,
      publishKey: defaultConfig.publishKey,
      uuid: defaultConfig.uuid,
      ssl: true,
      logVerbosity: env.NODE_ENV === 'development' ? true : false
    });
  } catch (error) {
    console.error('Failed to initialize PubNub:', error);
    return null;
  }
};

export const getChannel = () => {
  const settings = localStorage.getItem('pubnub_settings');
  if (settings) {
    return JSON.parse(settings).channel;
  }
  return getDefaultConfig().channel;
};