import React from 'react';
import ReactDOM from 'react-dom';
import ChatInterface from './chat';

const API_HOST = process.env.REACT_APP_API_HOST || 'http://localhost:8000';

ReactDOM.render(
  <React.StrictMode>
    <ChatInterface />
  </React.StrictMode>,
  document.getElementById('root')
);
