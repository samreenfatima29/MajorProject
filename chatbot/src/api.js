import axios from 'axios';

// Function to handle user login
export const login = async (username, password) => {
    const response = await axios.post('http://localhost:8080/login', { username, password });
    return response.data; // Returns the data received from the server
};

// Function to handle user registration
export const register = async (username, password) => {
    await axios.post('http://localhost:8080/register', { username, password });
};
