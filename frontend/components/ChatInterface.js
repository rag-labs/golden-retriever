"use client";

import { useState } from 'react';

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages([...messages, userMessage]);

    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input }),
    });

    const data = await response.json();
    const botMessage = { sender: 'bot', text: data.reply };
    setMessages([...messages, userMessage, botMessage]);
    setInput('');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      <div className="flex-1 p-4 overflow-y-auto">
        {messages.map((msg, index) => (
          <div key={index} className={`my-2 p-2 rounded ${msg.sender === 'user' ? 'bg-gray-700' : 'bg-gray-500'}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="p-4 bg-gray-800">
        <input
          type="text"
          className="w-full p-2 rounded bg-gray-700 text-white"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
        />
      </div>
    </div>
  );
}