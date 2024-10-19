import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Chatbot from './Chatbot';
import Login from './Login';
import Register from './Register';
import Header from './Header';  // Import Header component
import Footer from './Footer';
import PrescriptionForm from './PrescriptionForm';
import './App.css'
const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);  // Successfully logged in
  };

  const handleRegisterSuccess = () => {
    setIsLoggedIn(false);  // Switch to login after successful registration
  };
  
  return (
    <Router>
      <div>
        <Header />  {/* Include Header component */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route
            path="/login"
            element={<Login onLoginSuccess={handleLoginSuccess} />}
            //element={<Login />}
          />
          <Route
            path="/register"
            element={<Register onRegisterSuccess={handleRegisterSuccess} />}
            //element={<Register />}
          />
          <Route
            path="/chatbot"
            //element={<Chatbot/>}
            element={isLoggedIn ? <Chatbot /> : <Login onLoginSuccess={handleLoginSuccess} />}
          />
          <Route
            path="/prescription"
            element={<PrescriptionForm/>}
          />
        </Routes>
        <Footer />
      </div>
    </Router>
  );
};

const Home = () => (
  <div>
    <h2>Welcome to the Doctor Portal!!</h2>
  </div>
);

export default App;
