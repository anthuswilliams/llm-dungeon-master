import React, { useState } from 'react';
import { ChatFeed, Message } from 'react-chat-ui';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');

  const handleSendMessage = async () => {
    if (newMessage.trim() === '') return;

    const userMessage = new Message({ id: 0, message: newMessage });
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);

    try {
      const formattedMessages = updatedMessages.map((msg, index) => ({
        role: index % 2 === 0 ? 'user' : 'assistant',
        content: msg.message,
      }));

      await fetch('http://localhost:8000/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formattedMessages),
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
