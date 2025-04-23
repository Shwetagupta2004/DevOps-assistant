/* Chat Component */
// src/components/Chat.js
import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import ChatInput from './ChatInput';
import { sendMessage } from '../utils/api';

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your DevOps Engineer Assistant. How can I help you with your DevOps needs today?'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content) => {
    const userMessage = { role: 'user', content };
    
    // Update UI immediately with user's message
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setIsLoading(true);
    
    try {
      // Create messages array to send to API
      const messagesToSend = [
        { role: 'system', content: 'You are a helpful DevOps engineer assistant.' },
        ...messages.filter(msg => msg.role !== 'system'),
        userMessage
      ];
      
      const result = await sendMessage(messagesToSend);
      
      // Add assistant's response to chat
      setMessages(prevMessages => [
        ...prevMessages,
        { role: 'assistant', content: result.response }
      ]);
    } catch (error) {
      console.error('Failed to get response:', error);
      setMessages(prevMessages => [
        ...prevMessages,
        { 
          role: 'assistant', 
          content: 'Sorry, I encountered an error. Please try again.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="message-area">
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
        {isLoading && (
          <div className="typing-indicator">
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
            <div className="typing-dot"></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

export default Chat;