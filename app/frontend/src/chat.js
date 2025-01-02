import React, { useState } from 'react';
import './spinner.scss'; // Assuming you have a CSS file for the spinner

const ChatInterface = ({ initialMessages = [] }) => {
  const [messages, setMessages] = useState(initialMessages);
  const [newMessage, setNewMessage] = useState('');

  const [loading, setLoading] = useState(false);

  const renderMessages = () => {
    return messages.map((msg, index) => (
      <div key={index} className={`message ${msg.type}`}>
        <span className={msg.type}>{msg.message}</span>
      </div>
    ));
  };

  const handleSendMessage = async () => {
    if (newMessage.trim() === '') return;
    setLoading(true);

    const message = { id: 0, message: newMessage, type: 'user' };
    setMessages([...messages, message]);

    try {
      const response = await fetch('http://localhost:8000/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ messages: [newMessage] }),
      });
      const data = await response.json();
      if (data.responses) {
        const responseMessages = data.responses.map((msg, index) => ({ id: index + 1, message: msg, type: 'api' }));
        setMessages([...messages, message, ...responseMessages]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setLoading(false);
    }

    setNewMessage('');
  };

  return (
    <div className="chat-interface">
      <h1 className="chat-title">Chat with the RPG</h1>
      <div className="chat-feed">
        {renderMessages()}
      </div>
      {loading && <div className="spinner" aria-label="Loading..."><span className="visually-hidden">Loading...</span></div>}
      <textarea
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        placeholder="Type a message..."
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
          }
        }}
        disabled={loading}
        maxLength={1000}
        rows={4}
        className="message-input"
      />
      <div className="char-count">
        {newMessage.length}/1000
      </div>
      <button onClick={handleSendMessage} className="send-button">Send</button>
    </div>
  );
};

export default ChatInterface;
