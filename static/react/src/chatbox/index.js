import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";


import ChatBox from "./Components/ChatBox";

const root = ReactDOM.createRoot(document.getElementById('chatbox'));

root.render(
    <>
        <ChatBox />
    </>
);
