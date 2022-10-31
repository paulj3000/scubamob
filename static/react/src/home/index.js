import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";


import Home from "./Components/Home";
import Layout from "./Components/Layout";
import NoMatch from "./Components/NoMatch";

const root = ReactDOM.createRoot(document.getElementById('home'));

root.render(
    <BrowserRouter>
      <Routes>
        <Route path="home/" element={<Layout />}>
          <Route exact path="" home element={<Home />} />
          <Route path="*" element={<NoMatch />} />
        </Route>
      </Routes>

    </BrowserRouter>
);
