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
  const [model, setModel] = useState('gpt-4');
  const [knn, setKnn] = useState(0.8);
  const [keywordsWeight, setKeywordsWeight] = useState(0.2);

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
    const messageToSend = newMessage.trim() === '' ? randomExampleQuestion : newMessage;
    setLoading(true);

    const userMessage = { id: 0, message: messageToSend, type: 'user' };
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
        keywordWeight: keywordsWeight,
        model: model
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
        placeholder={messages.length > 0 ? "Type new message..." : `e.g. "${randomExampleQuestion}"`}
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
              <span className="control-label">Debug:</span>
              <input
                type="checkbox"
                checked={debug}
                onChange={() => setDebug(!debug)}
                style={{ marginLeft: '5px' }}
              />
            </label>
          </div>
          <div style={{ marginTop: '0.5em' }}>
            <span className="control-label">Model:</span>
            <select 
              value={model}
              onChange={(e) => setModel(e.target.value)}
              style={{ marginLeft: '5px', padding: '0.3em 0.5em' }}
            >
              <option value="gpt-4o">OpenAI GPT 4o</option>
              <option value="claude-3.5">Claude 3.5 Sonnet</option>
            </select>
          </div>
          <div className="slider-container" style={{ marginTop: '0.5em' }}>
            <label>
              <span className="control-label">KNN:</span> {knn.toFixed(2)}
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
          <div className="slider-container" style={{ marginTop: '0.5em' }}>
            <label>
              <span className="control-label">Keywords:</span> {keywordsWeight.toFixed(2)}
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
        <button onClick={handleSendMessage} className="send-button" disabled={messages.length > 0 && newMessage.trim() === ''}>Send</button>
      </div>
    </div>
  );
};

export default ChatInterface;
