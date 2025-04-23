/* Message Component */
// src/components/Message.js
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const Message = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className="message-container">
      <div className={`message-bubble ${isUser ? 'user-message' : 'assistant-message'}`}>
        {!isUser && (
          <div className="avatar assistant-avatar">A</div>
        )}
        {isUser && (
          <div className="avatar user-avatar">U</div>
        )}
        <div className="prose max-w-none">
          <ReactMarkdown
            components={{
              code({node, inline, className, children, ...props}) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={atomDark}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                )
              }
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default Message;