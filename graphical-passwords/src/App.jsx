import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import WheelPage from './pages/WheelPage.jsx';
import Dashboard from './pages/Dashboard.jsx';
import EmojiGrid from "./pages/EmojiGrid";



function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/wheel" element={<WheelPage />} />
                <Route path="/" element={<Dashboard />} />
                <Route path="/emoji-auth" element={<EmojiGrid />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
