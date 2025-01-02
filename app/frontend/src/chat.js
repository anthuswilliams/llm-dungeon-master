import React, { useState } from 'react';

const ChatInterface = ({ initialMessages = [] }) => {
  const [messages, setMessages] = useState(initialMessages);
  const [newMessage, setNewMessage] = useState('');

  const renderMessages = () => {
    return messages.map((msg, index) => (
      <div key={index} className="message">
        {msg.message}
      </div>
    ));
  };

  const handleSendMessage = async () => {
    if (newMessage.trim() === '') return;

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
    }

    setNewMessage('');
  };

  return (
    <div>
      <div className="chat-feed">
        {renderMessages()}
      </div>
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
