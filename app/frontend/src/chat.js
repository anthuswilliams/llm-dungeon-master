import React, { useState, useRef, useEffect } from 'react';
import dndQuestions from './dnd-5e-questions.json';
import otherscapeQuestions from './otherscape-questions.json';
import './chat.css';

const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://chat-rpg.ai/api' 
  : process.env.REACT_APP_API_HOST || 'http://localhost:8000';

const getUrlParams = () => {
  const params = new URLSearchParams(window.location.search);
  return {
    game: params.get('game') || 'dnd-5e',
    debug: params.get('debug') === 'true',
    model: params.get('model') || 'claude-3.5',
    knn: params.has('knn') ? parseFloat(params.get('knn')) : 0.7,
    keywords: params.has('keywords') ? parseFloat(params.get('keywords')) : 0.3
  };
};

const updateUrl = (params) => {
  if (typeof window === 'undefined') return;
  
  const url = new URL(window.location.href || 'http://localhost');
  Object.entries(params).forEach(([key, value]) => {
    if (value !== null && value !== undefined) {
      url.searchParams.set(key, value);
    }
  });
  try {
    window.history.replaceState({}, '', url.search);
  } catch (e) {
    console.warn('Failed to update URL:', e);
  }
};

const ChatInterface = ({ initialMessages = [] }) => {
  const urlParams = getUrlParams();
  const [game, setGame] = useState(urlParams.game);
  const [games, setGames] = useState([]);
  const [loadingGames, setLoadingGames] = useState(true);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await fetch(`${API_URL}/games`);
        const data = await response.json();
        setGames(data);
      } catch (error) {
        console.error('Error fetching games:', error);
      } finally {
        setLoadingGames(false);
      }
    };

    fetchGames();
  }, []);
  const [messages, setMessages] = useState(() => {
    const savedMessages = localStorage.getItem(`chat-history-${urlParams.game}`);
    return savedMessages ? JSON.parse(savedMessages) : initialMessages;
  });
  const exampleQuestions = game === 'dnd-5e' ? dndQuestions : otherscapeQuestions;
  const randomExampleQuestion = exampleQuestions[Math.floor(Math.random() * exampleQuestions.length)]

  const messageInputRef = useRef(null);
  const [newMessage, setNewMessage] = useState('');

  const [loading, setLoading] = useState(false);
  const [copyStatus, setCopyStatus] = useState('');
  const [debug, setDebug] = useState(urlParams.debug);
  const [model, setModel] = useState(urlParams.model);
  const [knn, setKnn] = useState(urlParams.knn);
  const [keywordsWeight, setKeywordsWeight] = useState(urlParams.keywords);
  const [controlsVisible, setControlsVisible] = useState(false);

  const getFormattedGameName = () => {
    const currentGame = games.find(g => g.id === game);
    return currentGame ? currentGame.displayName : 'the RPG';
  };

  const handleSliderChange = (type, value) => {
    if (type === 'knn') {
      setKnn(value);
      setKeywordsWeight(1 - value);
      updateUrl({ knn: value, keywords: 1 - value });
    } else {
      setKeywordsWeight(value);
      setKnn(1 - value);
      updateUrl({ keywords: value, knn: 1 - value });
    }
  };

  // Update URL when settings change
  useEffect(() => {
    updateUrl({
      game,
      debug,
      model,
      knn,
      keywords: keywordsWeight
    });
  }, [game, debug, model, knn, keywordsWeight]);

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

  // Save messages to localStorage whenever they change
  React.useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chat-history-${game}`, JSON.stringify(messages));
    }
  }, [messages, game]);

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
        model: model,
        game: game
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
      setTimeout(() => setCopyStatus(''), 500);
    } catch (err) {
      setCopyStatus('Failed to copy to clipboard');
      setTimeout(() => setCopyStatus(''), 500);
    }
  };

  const handleClearChat = () => {
    localStorage.removeItem(`chat-history-${game}`);
    setMessages([]);
    setCopyStatus('');
  };

  return (
    <div className="chat-container">
      <div className="game-sidebar">
        <h2>Games</h2>
        {loadingGames ? (
          <div className="spinner" aria-label="Loading games..." />
        ) : (
          games.map(({ id, name, displayName }) => (
            <button
              key={id}
              className={`game-option ${game === id ? 'selected' : ''}`}
              onClick={() => {
                // Save current chat before switching
                if (messages.length > 0) {
                  localStorage.setItem(`chat-history-${game}`, JSON.stringify(messages));
                }
                setGame(id);
                // Load chat history for new game or start fresh
                const savedMessages = localStorage.getItem(`chat-history-${id}`);
                setMessages(savedMessages ? JSON.parse(savedMessages) : []);
              }}
            >
              {displayName}
            </button>
          ))
        )}
      </div>
      <div className="chat-main">
        <h1 className="chat-title">Chat with {getFormattedGameName()}</h1>
        <div className="chat-feed">
          <div className="messages-container">
            {renderMessages()}
          </div>
          <div className="copy-container">
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <div className="copy-status-container">
                <button
                  onClick={handleCopyToClipboard}
                  className="copy-link"
                  disabled={!messages.length || loading}
                  aria-label="Copy"
                >
                  Copy
                </button>
                {copyStatus && (
                  <div 
                    className="copy-status visible" 
                    style={{ color: copyStatus === 'Copied!' ? 'green' : 'red' }}
                    aria-hidden="true"
                  >
                    {copyStatus}
                  </div>
                )}
              </div>
              <button
                onClick={handleClearChat}
                className="copy-link"
                disabled={messages.length === 0 || loading}
                aria-label="Clear"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
        {loading && <div className="spinner" aria-label="Loading..." />}
        <div className="input-container">
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
        </div>
        <div className="char-count">
          {newMessage.length}/1000
        </div>
        <div className="controls-row">
          <button
            className="settings-toggle"
            onClick={() => setControlsVisible(!controlsVisible)}
            aria-expanded={controlsVisible}
            title="Settings"
          >
            ⚙️
          </button>
          <button
            onClick={handleSendMessage}
            className="send-button"
            disabled={messages.length > 0 && newMessage.trim() === ''}
          >
            Send
          </button>
        </div>
        {controlsVisible && (
          <div className="controls-panel">
            <div className="control-elements">
              <div className="control-group">
                <label className="control-label" htmlFor="debug-checkbox">
                  <input
                    id="debug-checkbox"
                    type="checkbox"
                    checked={debug}
                    onChange={() => setDebug(!debug)}
                  />
                  Debug Mode
                </label>
              </div>
              <div className="control-group">
                <label className="control-label" htmlFor="model-select">Model</label>
                <select
                  id="model-select"
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                >
                  <option value="gpt-4o">OpenAI GPT 4o</option>
                  <option value="claude-3.5">Claude 3.5 Sonnet</option>
                </select>
              </div>
              <div className="control-group">
                <label className="control-label" htmlFor="knn-slider">
                  KNN Weight: {knn.toFixed(2)}
                </label>
                <input
                  id="knn-slider"
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={knn}
                  onChange={(e) => handleSliderChange('knn', parseFloat(e.target.value))}
                />
              </div>
              <div className="control-group">
                <label className="control-label" htmlFor="keywords-slider">
                  Keywords Weight: {keywordsWeight.toFixed(2)}
                </label>
                <input
                  id="keywords-slider"
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={keywordsWeight}
                  onChange={(e) => handleSliderChange('keywordsWeight', parseFloat(e.target.value))}
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
