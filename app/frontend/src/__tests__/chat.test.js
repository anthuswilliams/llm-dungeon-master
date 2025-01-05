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
});

afterAll(() => {
  console.error.mockRestore();
});

test('submits message on Enter key press', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation((url, options) => {
    const body = JSON.parse(options.body);
    expect(body).toHaveProperty('messages');
    expect(Array.isArray(body.messages)).toBe(true);
    return Promise.resolve({
      json: () => Promise.resolve({}),
    });
  });

  render(<ChatInterface />);

  const input = screen.getByPlaceholderText(/e\.g\./);

  expect(screen.queryByText('Loading...')).not.toBeInTheDocument();

  const newMessage = 'Enter key message';
  fireEvent.change(input, { target: { value: newMessage } });
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  expect(screen.getByText('Loading...')).toBeInTheDocument();

  // eslint-disable-next-line testing-library/no-unnecessary-act
  await act(async () => {
    await screen.findByText((content, element) => {
      return element.tagName.toLowerCase() === 'span' && content === 'Enter key message';
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

test('Copy button is disabled when there are no messages', () => {
  render(<ChatInterface initialMessages={[]} />);
  const copyButton = screen.getByText('Copy');
  expect(copyButton).toBeDisabled();
});

test('Copy button copies messages to clipboard when enabled', async () => {
  const messages = [
    { id: 0, message: 'Hello', type: 'user' },
    { id: 1, message: 'How are you?', type: 'api' },
  ];

  // Mock the clipboard API
  const writeTextMock = jest.fn();
  Object.assign(navigator, {
    clipboard: {
      writeText: writeTextMock,
    },
  });

  render(<ChatInterface initialMessages={messages} />);
  const copyButton = screen.getByText('Copy');
  expect(copyButton).not.toBeDisabled();

  fireEvent.click(copyButton);
  expect(writeTextMock).toHaveBeenCalledWith(JSON.stringify(messages, null, 2));
});

test('sends debug: true when checkbox is checked', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation((url, options) => {
    const body = JSON.parse(options.body);
    expect(body.debug).toBe(true);
    return Promise.resolve({
      json: () => Promise.resolve({}),
    });
  });

  render(<ChatInterface />);
  const debugCheckbox = screen.getByLabelText('Debug');
  fireEvent.click(debugCheckbox);

  const input = screen.getByPlaceholderText(/e\.g\./);
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  fetchMock.mockRestore();
});

test('sends debug: false when checkbox is unchecked', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation((url, options) => {
    const body = JSON.parse(options.body);
    expect(body.debug).toBe(false);
    return Promise.resolve({
      json: () => Promise.resolve({}),
    });
  });

  render(<ChatInterface />);
  const input = screen.getByPlaceholderText(/e\.g\./);
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  fetchMock.mockRestore();
});

test('sends correct slider values', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation((url, options) => {
    const body = JSON.parse(options.body);
    expect(body.knn).toBeCloseTo(0.4);
    expect(body.keywords).toBeCloseTo(0.6);
    return Promise.resolve({
      json: () => Promise.resolve({}),
    });
  });

  render(<ChatInterface />);
  const input = screen.getByPlaceholderText(/e\.g\./);
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  fetchMock.mockRestore();
});

test('sliders always sum to 1', () => {
  render(<ChatInterface />);
  const knnSlider = screen.getByLabelText(/KNN:/);
  const keywordsSlider = screen.getByLabelText(/Keywords:/);

  fireEvent.change(knnSlider, { target: { value: 0.7 } });
  expect(parseFloat(knnSlider.value) + parseFloat(keywordsSlider.value)).toBeCloseTo(1);

  fireEvent.change(keywordsSlider, { target: { value: 0.3 } });
  expect(parseFloat(knnSlider.value) + parseFloat(keywordsSlider.value)).toBeCloseTo(1);
});

test('displays debug info when debug is checked', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation(() => Promise.resolve({
    json: () => Promise.resolve({
      response: 'API response',
      context: ['context1', 'context2'],
    }),
  }));

  render(<ChatInterface />);
  const debugCheckbox = screen.getByLabelText('Debug');
  fireEvent.click(debugCheckbox);

  const input = screen.getByPlaceholderText(/e\.g\./);
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  await screen.findByText('API response');
  expect(screen.getByText('context1, context2')).toBeInTheDocument();

  fetchMock.mockRestore();
});


test('debug info includes slider values at submission time', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation(() => Promise.resolve({
    json: () => Promise.resolve({
      response: 'API response',
      context: ['context1', 'context2'],
      knn: 0.4,
      keywords: 0.6,
    }),
  }));

  render(<ChatInterface />);
  const debugCheckbox = screen.getByLabelText('Debug');
  fireEvent.click(debugCheckbox);

  const input = screen.getByPlaceholderText(/e\.g\./);
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  await screen.findByText('API response');
  expect(screen.getByText('KNN: 0.40')).toBeInTheDocument();
  expect(screen.getByText('Keywords: 0.60')).toBeInTheDocument();

  fetchMock.mockRestore();
});

test('displays character count', () => {
  render(<ChatInterface initialMessages={[]} />);
  const input = screen.getByPlaceholderText(/e\.g\./);
  expect(screen.getByText('0/1000')).toBeInTheDocument();

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

  const input = screen.getByPlaceholderText(/e\.g\./);
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
      return element.tagName.toLowerCase() === 'span' && content === 'Test message';
    });
  });

  expect(input).not.toBeDisabled();

  fetchMock.mockRestore();
});
