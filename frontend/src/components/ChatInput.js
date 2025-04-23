/* Chat Input Component */
// src/components/ChatInput.js
import React, { useState } from 'react';

const ChatInput = ({ onSendMessage, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="input-area">
      <form onSubmit={handleSubmit} className="chat-form">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask something about DevOps..."
          className="chat-input"
          disabled={isLoading}
          rows={1}
          style={{ resize: 'none', overflow: 'auto' }}
        />
        <button
          type="submit"
          className="send-button"
          disabled={isLoading || !input.trim()}
        >
          {isLoading ? 'Processing...' : 'Send'}
        </button>
      </form>
    </div>
  );
  
};

export default ChatInput;