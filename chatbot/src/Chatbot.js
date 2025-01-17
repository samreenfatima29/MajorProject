import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css'; // Add your styles here or use inline styling
const Chatbot = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of chat when new message is added
  // Runs after the component renders whenever the messages array changes. It scrolls the chat container to the bottom to show the latest message.
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const appendMessage = (content, type) => {
    setMessages((prevMessages) => [
      ...prevMessages,
      { content, type, id: prevMessages.length + 1 },
    ]);
  };

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;

    appendMessage(inputValue, 'user');
    setInputValue('');

    // Simulate API call for the bot response
    const response = await fetch('http://localhost:8080/ask_pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: inputValue }),
    });

    const data = await response.json();
    appendMessage(data.answer, 'bot');
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8080/upload_pdf', {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    appendMessage(`File uploaded: ${data.filename}`, 'bot');
    event.target.value = ''; // Clear file input
  };

  return (
    <div>
      {/* Chatbot Floating Button */}
      <div className="chatbot-button" onClick={toggleChat}>
        <img
          src="https://cdn4.vectorstock.com/i/1000x1000/81/78/chatbot-icon-outline-robot-sign-on-a-blue-vector-19838178.jpg"
          alt="Chatbot"
        />
      </div>

      {/* Chat Container */}
      {isChatOpen && (
        <div className="chat-container">
          <div className="chat-header">
            Chatbot Support
            <button className="close-button" onClick={toggleChat}>
              &times;
            </button>
          </div>

          <div className="chat-box">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.type}`}>
                {message.type === 'bot' && (
                  <div className="avatar">
                    <img
                      src="https://cdn-icons-png.flaticon.com/512/12430/12430774.png"
                      alt="Bot Avatar"
                    />
                  </div>
                )}
                <p>{message.content}</p>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <input
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              placeholder="Type a message..."
            />
            <button onClick={handleSendMessage}>Send</button>

            <label htmlFor="file-input" className="file-upload">
              📄
            </label>
            <input
              id="file-input"
              type="file"
              accept=".pdf"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
