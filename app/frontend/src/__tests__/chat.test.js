import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import ChatInterface from '../chat';

global.fetch = jest.fn();

test('renders all messages', () => {
  const messages = [
    { id: 0, message: 'Hello' },
    { id: 1, message: 'How are you?' },
    { id: 0, message: 'I am fine, thank you!' },
  ];

  render(<ChatInterface initialMessages={messages} />);

  // Simulate setting messages
  messages.forEach(msg => {
    const messageElement = screen.getByText(msg.message);
    expect(messageElement).toBeInTheDocument();
  });
});

test('each message is rendered', () => {
  const messages = [
    { id: 0, message: 'Hello' },
    { id: 1, message: 'How are you?' },
    { id: 0, message: 'I am fine, thank you!' },
  ];

  render(<ChatInterface initialMessages={messages} />);

  messages.forEach(msg => {
    const messageElement = screen.getByText(msg.message);
    expect(messageElement).toBeInTheDocument();
  });
});
test('sends correct payload to server on submit', async () => {
  const { getByPlaceholderText, getByText } = render(<ChatInterface />);

  const input = getByPlaceholderText('Type a message...');
  const sendButton = getByText('Send');

  // Simulate user typing a message
  const newMessage = 'Test message';
  fireEvent.change(input, { target: { value: newMessage } });

  // Simulate clicking the send button
  fireEvent.click(sendButton);

  // Assert fetch was called with the correct payload
  expect(fetch).toHaveBeenCalledWith('http://localhost:8000/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: newMessage }),
  });
});
