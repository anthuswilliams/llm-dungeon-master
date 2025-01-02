import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import ChatInterface from '../chat';

// Suppress act warnings in the console
beforeAll(() => {
  jest.spyOn(console, 'error').mockImplementation((message) => {
    if (!message.includes('act(...)')) {
      console.error(message);
    }
});

afterAll(() => {
  console.error.mockRestore();
});

test('submits message on Enter key press', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation(() => Promise.resolve({
    json: () => Promise.resolve({}),
  }));

  render(<ChatInterface />);

  const input = screen.getByPlaceholderText('Type a message...');

  expect(screen.queryByText('Loading...')).not.toBeInTheDocument();

  const newMessage = 'Enter key message';
  fireEvent.change(input, { target: { value: newMessage } });

  // Simulate pressing the Enter key
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  expect(screen.getByText('Loading...')).toBeInTheDocument();

  // eslint-disable-next-line testing-library/no-unnecessary-act
  await act(async () => {
    await screen.findByText((content, element) => {
      return element.tagName.toLowerCase() === 'div' && content === 'Enter key message';
    });
  });

  expect(screen.queryByText('Loading...')).not.toBeInTheDocument();

  fetchMock.mockRestore();
});

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

test('updates character count as user types', () => {
  render(<ChatInterface />);

  const input = screen.getByPlaceholderText('Type a message...');
  const charCount = screen.getByText('0/1000');

  expect(charCount).toBeInTheDocument();

  fireEvent.change(input, { target: { value: 'Hello' } });

  expect(screen.getByText('5/1000')).toBeInTheDocument();

  fireEvent.change(input, { target: { value: 'Hello, world!' } });

  expect(screen.getByText('13/1000')).toBeInTheDocument();
});

test('disables input box while request is in flight', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation(() => Promise.resolve({
    json: () => Promise.resolve({}),
  }));

  render(<ChatInterface />);

  const input = screen.getByPlaceholderText('Type a message...');
  const sendButton = screen.getByText('Send');

  expect(input).not.toBeDisabled();

  fireEvent.change(input, { target: { value: 'Test message' } });

  // eslint-disable-next-line testing-library/no-unnecessary-act
  act(() => {
    fireEvent.click(sendButton);
  });

  expect(input).toBeDisabled();

  // eslint-disable-next-line testing-library/no-unnecessary-act
  await act(async () => {
    await screen.findByText((content, element) => {
      return element.tagName.toLowerCase() === 'div' && content === 'Test message';
    });
  });

  expect(input).not.toBeDisabled();

  fetchMock.mockRestore();
});
});
