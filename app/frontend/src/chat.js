import React, { useState } from 'react';
import { Message } from 'react-chat-ui';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
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

    const message = new Message({ id: 0, message: newMessage });
    setMessages([...messages, message]);

    try {
      await fetch('http://localhost:8000/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: newMessage }),
      });
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
