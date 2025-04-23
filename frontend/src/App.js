/* App Component */
// src/App.js
import React from 'react';
import Header from './components/Header';
import Chat from './components/Chat';
import './styles/main.css';

function App() {
  return (
    <div className="app-container">
      <div className="container">
      <Header />
        <Chat />
      </div>
    </div>
  );
}

export default App;