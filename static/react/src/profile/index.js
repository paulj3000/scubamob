import React from 'react';
import ReactDOM from 'react-dom/client';
//import App from './App';

import Home from "./Components/Home";
import About from "./Components/About";
import Buddies from "./Components/Buddies";
import Gallery from "./Components/Gallery";
import Photos from "./Components/Photos";
import PhotoAlbums from "./Components/PhotoAlbums";
import Layout from "./Components/Layout";
//import Dashboard from "./Components/Dashboard";

/* do the "me" stuff */
import Checkins from "./Components/me/Checkins";

/* the 404 page */
import NoMatch from "./Components/NoMatch";

import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";

const profile = document.getElementById('profile');
const root = ReactDOM.createRoot(profile);

const profileData = JSON.parse(document.getElementById('profileData').textContent);

root.render(
    <>
    <BrowserRouter>
      <Routes>
        <Route path="p/:userName" element={<Layout {...profileData} />}>
            <Route index element={<Home {...profileData} />} />
            <Route path="buddies" element={<Buddies id={profileData.id} />} />
            <Route path="gallery" element={<Gallery id={profileData.id} />} />
            <Route path="photo_albums" element={<PhotoAlbums id={profileData.id} />} />
            <Route path="photos" element={<Photos id={profileData.id} />} />
            <Route path="checkins" element={<Checkins id={profileData.id} />} />
            <Route path="*" element={<NoMatch />} />
        </Route>
        <Route path="*" element={<NoMatch />} />
      </Routes>

    </BrowserRouter>
    </>
);
