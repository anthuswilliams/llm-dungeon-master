import React, { useState } from 'react';
import { ChatFeed, Message } from 'react-chat-ui';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

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
      <ChatFeed
        messages={messages}
        showSenderName
        bubblesCentered={false}
      />
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