import React from 'react';
import { render, screen, fireEvent, act, cleanup } from '@testing-library/react';
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

afterEach(() => {
  cleanup();
})

test('uses random question as placeholder when no messages are submitted', () => {
  render(<ChatInterface initialMessages={[]} />);
  const input = screen.getByPlaceholderText(/e\.g\. "/);
  expect(input).toBeInTheDocument();
});

test('Send button is active and sends random question when clicked with no user input', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation((url, options) => {
    const body = JSON.parse(options.body);
    expect(body.messages[0].content).toMatch(/e\.g\./);
    return Promise.resolve({
      json: () => Promise.resolve({}),
    });
  });

  render(<ChatInterface initialMessages={[]} />);
  const sendButton = screen.getByText('Send');
  expect(sendButton).not.toBeDisabled();

  fireEvent.click(sendButton);

  fetchMock.mockRestore();
});

test('handles Enter key press to send message', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation((url, options) => {
    const body = JSON.parse(options.body);
    expect(body).toHaveProperty('messages');
    expect(Array.isArray(body.messages)).toBe(true);
    return Promise.resolve({
      json: () => Promise.resolve({}),
    });
  });

  render(<ChatInterface />);

  const input = screen.getByPlaceholderText(/Type new message.../);

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

test('uses "Type new message..." as placeholder when messages are submitted', () => {
  const messages = [{ id: 0, message: 'Hello', type: 'user' }];
  render(<ChatInterface initialMessages={messages} />);
  const input = screen.getByPlaceholderText('Type new message...');
  expect(input).toBeInTheDocument();
});

test('Send button is disabled until user types a message after messages are submitted', () => {
  const messages = [{ id: 0, message: 'Hello', type: 'user' }];
  render(<ChatInterface initialMessages={messages} />);
  const sendButton = screen.getByText('Send');
  expect(sendButton).toBeDisabled();

  const input = screen.getByPlaceholderText('Type new message...');
  fireEvent.change(input, { target: { value: 'New message' } });
  expect(sendButton).not.toBeDisabled();
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

  const input = screen.getByPlaceholderText("Type new message...");

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
    { id: 0, message: 'Hello', type: 'user' },
    { id: 1, message: 'How are you?', type: 'api' },
    { id: 0, message: 'I am fine, thank you!', type: 'user' },
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
  const copyButton = screen.getByRole('button', { name: 'Copy' });
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

  // Open settings panel first
  const settingsButton = screen.getByTitle('Settings');
  fireEvent.click(settingsButton);

  const debugCheckbox = screen.getByLabelText('Debug Mode');
  fireEvent.click(debugCheckbox);

  const input = screen.getByPlaceholderText("Type new message...");
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
  const input = screen.getByPlaceholderText("Type new message...");
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
  const input = screen.getByPlaceholderText("Type new message...");
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  fetchMock.mockRestore();
});

test('sliders always sum to 1', () => {
  render(<ChatInterface />);

  // Open settings panel first
  const settingsButton = screen.getByTitle('Settings');
  fireEvent.click(settingsButton);

  const knnSlider = screen.getByLabelText(/KNN Weight:/);
  const keywordsSlider = screen.getByLabelText(/Keywords Weight:/);

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

  // Open settings panel first
  const settingsButton = screen.getByTitle('Settings');
  fireEvent.click(settingsButton);

  const debugCheckbox = screen.getByLabelText('Debug Mode');
  fireEvent.click(debugCheckbox);

  const input = screen.getByPlaceholderText("Type new message...");
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  await screen.findByText('API response');
  expect(screen.getByText('context1, context2')).toBeInTheDocument();

  fetchMock.mockRestore();
});


test('sends selected model value to API', async () => {
  const fetchMock = jest.spyOn(global, 'fetch').mockImplementation((url, options) => {
    const body = JSON.parse(options.body);
    expect(body.model).toBe('claude-3.5');
    return Promise.resolve({
      json: () => Promise.resolve({}),
    });
  });

  render(<ChatInterface />);

  // Open settings panel first
  const settingsButton = screen.getByTitle('Settings');
  fireEvent.click(settingsButton);

  // Change model selection
  const modelSelect = screen.getByLabelText('Model');
  fireEvent.change(modelSelect, { target: { value: 'claude-3.5' } });

  // Send a message
  const input = screen.getByPlaceholderText("Type new message...");
  fireEvent.change(input, { target: { value: 'Test message' } });
  fireEvent.keyDown(input, { key: 'Enter', code: 'Enter', charCode: 13 });

  // Wait for message to be sent
  await screen.findByText((content, element) => {
    return element.tagName.toLowerCase() === 'span' &&
      element.className === 'user' &&
      content === 'Test message';
  });

  fetchMock.mockRestore();
});

test('slider controls show correct initial values', () => {
  render(<ChatInterface />);

  // Open settings panel first
  const settingsButton = screen.getByTitle('Settings');
  fireEvent.click(settingsButton);

  // Find the KNN slider label in the control panel
  const knnLabel = screen.getByText(/KNN Weight:/);
  expect(knnLabel).toHaveTextContent('KNN Weight: 0.80');

  // Find the Keywords slider label in the control panel
  const keywordsLabel = screen.getByText(/Keywords Weight:/);
  expect(keywordsLabel).toHaveTextContent('Keywords Weight: 0.20');
});

test('displays character count', () => {
  render(<ChatInterface initialMessages={[]} />);
  const input = screen.getByPlaceholderText(/Type new message.../);
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

  const input = screen.getByPlaceholderText("Type new message...");
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
