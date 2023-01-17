import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";


import Home from "./Components/Home";
import Chat from "./Components/Chat";
import NewChat from "./Components/NewChat";
import Layout from "./Components/Layout";
import NoMatch from "./Components/NoMatch";

const root = ReactDOM.createRoot(document.getElementById('messenger'));

root.render(
    <BrowserRouter>
      <Routes>
        <Route path="messenger/" element={<Layout />}>
          <Route exact path="t/:id" chat element={<Chat />} />
          <Route exact path="new" newchat element={<NewChat />} />
          <Route exact path="" home element={<Home />} />
          <Route path="*" element={<NoMatch />} />
        </Route>
      </Routes>

    </BrowserRouter>
);
