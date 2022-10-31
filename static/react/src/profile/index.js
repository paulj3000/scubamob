import React from 'react';
import ReactDOM from 'react-dom/client';
//import App from './App';

import Home from "./Components/Home";
import About from "./Components/About";
import Buddies from "./Components/Buddies";
import Layout from "./Components/Layout";
//import Dashboard from "./Components/Dashboard";
import NoMatch from "./Components/NoMatch";

import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";

//import 'bootstrap/dist/css/bootstrap.css';


const root = ReactDOM.createRoot(document.getElementById('profile'));

let userName = 'paulj3000';
root.render(

    <>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route exact path="p/:userName" home element={<Home />} />
          <Route path="p/:userName/about" element={<About />} />
          <Route path="p/:userName/buddies" element={<Buddies />} />
          <Route path="*" element={<NoMatch />} />
        </Route>
      </Routes>

    </BrowserRouter>
    </>
);
