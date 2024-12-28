import React, { useState } from 'react';
import axios from 'axios'; // use to communicate with apis
import { useNavigate } from 'react-router-dom'; 
// to navigate between different pages
const Register = ({ onRegisterSuccess }) => {
  const [username, setUsername] = useState(''); 
  // state variables (useState hook) to store the values of usename and passwords
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate=useNavigate();
  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:8080/register', {
        username,
        password,
      });
      if (response.status === 201) {
       // onRegisterSuccess();  // Notify parent component to switch to login
        navigate("/login");
      }
    } catch (error) {
      setErrorMessage('Registration failed. User might already exist.');
    }
  };

  return (
    <div>
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
        <button type="submit">Register</button>
      </form>
    </div>
  );
};

export default Register;
