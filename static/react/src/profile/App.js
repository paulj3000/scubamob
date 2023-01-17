import React from 'react';
import * as ReactBootStrap from "react-bootstrap";
//import DankMemes from "./Components/DankMemes";
import Features from "./Components/Features";
//import NavBar from "./Components/Navbar"
//import Footer from "./Components/Footer"

import { Outlet, Link } from "react-router-dom";

function App() {
  return (
    <div className="App">
        <Outlet />
    </div>
  );
}

export default App;

