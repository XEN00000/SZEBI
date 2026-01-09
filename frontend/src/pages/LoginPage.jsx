import React, { useState } from 'react';

const LoginPage = ({ onLoginSuccess }) => {
    const [credentials, setCredentials] = useState({ username: '', password: '' });

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetch('http://localhost:8000/api/login/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials),
        });
        if (response.ok) {
            const data = await response.json();
            onLoginSuccess(data.user);
        } else {
            alert("Błąd logowania!");
        }
    };

    return (
        <form onSubmit={handleSubmit} className="p-8 max-w-sm mx-auto">
            <input 
                type="text" 
                placeholder="Login" 
                onChange={e => setCredentials({...credentials, username: e.target.value})}
                className="block w-full mb-4 p-2 border"
            />
            <input 
                type="password" 
                placeholder="Hasło" 
                onChange={e => setCredentials({...credentials, password: e.target.value})}
                className="block w-full mb-4 p-2 border"
            />
            <button type="submit" className="bg-blue-500 text-white p-2 w-full">Zaloguj</button>
        </form>
    );
};

export default LoginPage;