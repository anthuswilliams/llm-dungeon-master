import React, { useState, useRef } from 'react';
import exampleQuestions from './example_questions.json';
import './spinner.scss'; // Assuming you have a CSS file for the spinner

const ChatInterface = ({ initialMessages = [] }) => {
  const [messages, setMessages] = useState(initialMessages);
  const randomExampleQuestion = exampleQuestions[Math.floor(Math.random() * exampleQuestions.length)];
  const messageInputRef = useRef(null);
  const [newMessage, setNewMessage] = useState('');

  const [loading, setLoading] = useState(false);
  const [copyStatus, setCopyStatus] = useState('');
  const [debug, setDebug] = useState(false);

  const [knn, setKnn] = useState(0.4);
  const [keywordsWeight, setKeywordsWeight] = useState(0.6);

  const handleSliderChange = (type, value) => {
    if (type === 'knn') {
      setKnn(value);
      setKeywordsWeight(1 - value);
    } else {
      setKeywordsWeight(value);
      setKnn(1 - value);
    }
  };

  const renderMessages = () => {
    return messages.map((msg, index) => (
      <div key={index}>
        <div className={`message ${msg.type}`}>
          <span className={msg.type}>{msg.message}</span>
        </div>
        {debug && msg.type === 'api' && (
          <div className="debug-info">
            <>
              <div><strong>Keywords Weight:</strong> {msg.keywordWeight !== undefined ? msg.keywordWeight.toFixed(2) : 'N/A'}</div>
              <div><strong>KNN:</strong> {msg.knnWeight !== undefined ? msg.knnWeight.toFixed(2) : 'N/A'}</div>
              <div><strong>Keywords:</strong> {msg.keywords}</div>
              <div><strong>Context:</strong> {msg.context ? msg.context.join(', ') : 'N/A'}</div>
            </>
          </div>
        )}
      </div>
    ));
  };

  if (messageInputRef.current) {
    messageInputRef.current.focus();
  }

  const handleSendMessage = async () => {
    if (newMessage.trim() === '') return;
    setLoading(true);

    const userMessage = { id: 0, message: newMessage, type: 'user' };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);

    try {
      const formattedMessages = {
        messages: updatedMessages.map((msg, index) => ({
          role: index % 2 === 0 ? 'user' : 'assistant',
          content: msg.message,
        })),
        debug,
        knnWeight: knn,
        keywordWeight: keywordsWeight
      };

      const apiUrl = process.env.NODE_ENV === 'production' ? 'https://chat-rpg.ai/api' : process.env.REACT_APP_API_HOST || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formattedMessages),
      });
      const data = await response.json();
      if (data.response) {
        const responseMessage = {
          id: updatedMessages.length,
          message: data.response,
          type: 'api',
          keywords: data.keywords || null,
          keywordWeight: keywordsWeight,
          context: data.context || null,
          knnWeight: knn,
        };
        setMessages([...updatedMessages, responseMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }

    setNewMessage('');
  };

  const handleCopyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(messages, null, 2));
      setCopyStatus('Copied!');
    } catch (err) {
      setCopyStatus('Failed to copy to clipboard');
    }
  };

  return (
    <div className="chat-interface">
      <h1 className="chat-title">Chat with the RPG</h1>
      <div className="chat-feed">
        {renderMessages()}
      </div>
      {loading && <div className="spinner" aria-label="Loading..."><span className="visually-hidden">Loading...</span></div>}
      <button onClick={handleCopyToClipboard} className="copy-link" disabled={messages.length === 0}>
        Copy
      </button>
      <span className="copy-status" style={{ color: copyStatus === 'Copied!' ? 'green' : 'red' }}>
        {copyStatus}
      </span>
      <textarea
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        placeholder={`e.g. "${randomExampleQuestion}"`}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
          }
        }}
        ref={messageInputRef}
        autoFocus
        disabled={loading}
        maxLength={1000}
        rows={4}
        className="message-input"
      />
      <div className="char-count">
        {newMessage.length}/1000
      </div>
      <div className="controls">
        <div className="control-elements">
          <div className="debug-checkbox">
            <label>
              <input
                type="checkbox"
                checked={debug}
                onChange={() => setDebug(!debug)}
              />
              Debug
            </label>
          </div>
          <br />
          <div className="slider-container">
            <label>
              KNN: {knn.toFixed(2)}
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={knn}
                onChange={(e) => handleSliderChange('knn', parseFloat(e.target.value))}
              />
            </label>
          </div>
          <br />
          <div className="slider-container">
            <label>
              Keywords: {keywordsWeight.toFixed(2)}
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={keywordsWeight}
                onChange={(e) => handleSliderChange('keywordsWeight', parseFloat(e.target.value))}
              />
            </label>
          </div>
        </div>
        <button onClick={handleSendMessage} className="send-button">Send</button>
      </div>
    </div>
  );
};

export default ChatInterface;
