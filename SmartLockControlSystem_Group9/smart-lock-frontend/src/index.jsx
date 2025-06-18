import React from 'react';
import ReactDOM from 'react-dom';
import { BrowserRouter } from 'react-router-dom';
import { PubNubProvider } from 'pubnub-react';
import App from './App';
import { initializePubNub } from './utils/pubnub-config';
import './index.css';

const router = {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true
  }
};

const pubnub = initializePubNub();

ReactDOM.render(
  <React.StrictMode>
    <PubNubProvider client={pubnub}>
      <BrowserRouter future={router}>
        <App />
      </BrowserRouter>
    </PubNubProvider>
  </React.StrictMode>,
  document.getElementById('root')
);