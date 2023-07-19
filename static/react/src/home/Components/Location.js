import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';


function Location(props) {
    return (
        <div className="row">
            <div class="col-3">
                <img src={props.weather.condition.icon} style={{height: "120px", width: "120px"}}/>
            </div>
            <div class="col">
                <h1>{props.location.name}</h1>
                <h4>{props.weather.condition.text}</h4>
            </div>
        </div>
    )
}

export default Location;
