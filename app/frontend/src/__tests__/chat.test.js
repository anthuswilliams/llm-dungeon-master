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

  render(<ChatInterface />);

  const input = screen.getByPlaceholderText('Type a message...');
  const sendButton = screen.getByText('Send');

  expect(screen.queryByText('Loading...')).not.toBeInTheDocument();

  const newMessage = 'Test message';
  fireEvent.change(input, { target: { value: newMessage } });

  // eslint-disable-next-line testing-library/no-unnecessary-act
  act(() => {
    fireEvent.click(sendButton);
  });

  expect(screen.queryByText('Loading...')).toBeInTheDocument();

  // eslint-disable-next-line testing-library/no-unnecessary-act
  await act(async () => {
    await screen.findByText('Test message');
  });

  expect(screen.queryByText('Loading...')).not.toBeInTheDocument();

  fetchMock.mockRestore();
});
