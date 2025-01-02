import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import ChatInterface from '../chat';


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
test('sends correct payload to server on submit and checks spinner visibility', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation(() => Promise.resolve({
    json: () => Promise.resolve({}),
  }));

  const { getByPlaceholderText, getByText } = render(<ChatInterface />);

  const input = getByPlaceholderText('Type a message...');
  const sendButton = getByText('Send');

  // Assert spinner is not present initially
  expect(screen.queryByText('Loading...')).not.toBeInTheDocument();

  // Simulate user typing a message
  const newMessage = 'Test message';
  fireEvent.change(input, { target: { value: newMessage } });

  // Simulate clicking the send button
  await act(async () => {
    fireEvent.click(sendButton);
  });

  // Assert spinner is present while message is in flight
  expect(screen.queryByText('Loading...')).toBeInTheDocument();
  expect(fetch).toHaveBeenCalledWith('http://localhost:8000/messages', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ messages: [newMessage] }),
  });

  // Wait for the fetch to complete and assert spinner is no longer present
  await screen.findByText('Test message');
  expect(screen.queryByText('Loading...')).not.toBeInTheDocument();

  fetchMock.mockRestore();
});
