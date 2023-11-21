import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";


import Home from "./Components/Home";
import Layout from "./Components/Layout";
import PhotoUpload from "./Components/PhotoUpload";
import Checkins from "./Components/Checkins";
import WriteReview from "./Components/WriteReview";
import NoMatch from "./Components/NoMatch";

const root = ReactDOM.createRoot(document.getElementById('divesite'));
const siteId = document.getElementById('divesite').dataset.id;

root.render(
    <>
    <BrowserRouter>
      <Routes>
        <Route path="sites/:siteName" element={<Layout />}>
            <Route index element={<Home id={siteId} />} />
            <Route path="checkins" element={<Checkins id={siteId} />} />
            <Route path="writeareview" element={<WriteReview id={siteId} />} />
            <Route path="photos/upload" element={<PhotoUpload id={siteId} />} />
            <Route path="*" element={<NoMatch />} />
        </Route>
        <Route path="*" element={<NoMatch />} />
      </Routes>

    </BrowserRouter>
    </>
);
