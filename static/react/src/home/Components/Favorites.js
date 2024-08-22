import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';
import Site from "./Site";


function Favorites(props) {
    return (
        <>
        <h2>Favorites</h2>
        <div className="row">
            {props.divesites.list.map(site => (
                <Site site={site} key={site.id} />
            ))}
        </div>
        </>
    )
}

export default Favorites;
