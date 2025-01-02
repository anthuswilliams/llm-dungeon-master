import React, { useState } from 'react';
import './spinner.css'; // Assuming you have a CSS file for the spinner

const ChatInterface = ({ initialMessages = [] }) => {
  const [messages, setMessages] = useState(initialMessages);
  const [newMessage, setNewMessage] = useState('');

  const [loading, setLoading] = useState(false);

  const renderMessages = () => {
    return messages.map((msg, index) => (
      <div key={index} className="message">
        {msg.message}
      </div>
    ));
  };

  const handleSendMessage = async () => {
    if (newMessage.trim() === '') return;
    setLoading(true);

    const message = { id: 0, message: newMessage };
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
        const responseMessages = data.responses.map((msg, index) => ({ id: index + 1, message: msg }));
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
    <div>
      <div className="chat-feed">
        {renderMessages()}
      </div>
      {loading && <div className="spinner">Loading...</div>}
      <input
        type="text"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
        placeholder="Type a message..."
      />
      <button onClick={handleSendMessage}>Send</button>
    </div>
  );
};

export default ChatInterface;
