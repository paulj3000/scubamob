import React from 'react';
import ReactDOM from 'react-dom/client';
//import App from './App';
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";


import SignInAndSecurity from "./Components/SignInAndSecurity";
import Layout from "./Components/Layout";
import EmailAddresses from "./Components/EmailAddresses";
import ManageEmailAddresses from "./Components/ManageEmailAddresses";

import Home from "./Components/Home";
import DisplayMode from "./Components/AccountPreferences/DisplayMode.js";
import BasicInfo from "./Components/AccountPreferences/BasicInfo.js";

import NoMatch from "./Components/NoMatch";


const root = ReactDOM.createRoot(document.getElementById('settings'));

let userName = 'paulj3000';
root.render(
    <BrowserRouter>
      <Routes>
        <Route path="settings/" element={<Layout />}>
          <Route exact path="" home element={<Home />} />
          <Route exact path="category/account" home element={<Home />} />
          <Route exact path="item/display-mode" element={<DisplayMode />} />
          <Route exact path="item/basic-info" element={<BasicInfo />} />

          <Route exact path="category/sign-in-and-security" home element={<SignInAndSecurity />} />
          <Route exact path="item/manage-email-addresses" element={<ManageEmailAddresses />} />
          <Route exact path="email-addresses" home element={<EmailAddresses />} />
          <Route exact path="settings1" home element={<Home />} />
          <Route exact path="settings2" home element={<Home />} />
          <Route path="*" element={<NoMatch />} />
        </Route>
      </Routes>

    </BrowserRouter>
);
