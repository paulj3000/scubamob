import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';


function Favorites(props) {
    return (
        <div className="row">

            {props.divesites.list.map(site => (
                <div className="col-md-4 mb-5" key={site.id}>
                    <a href={site.url}>
                        <div className="card h-100">
                            <img className="card-img-top" src={site.banner} alt="Card image cap" />
                            <div className="card-body">
                                <h2 className="card-title">{site.name}</h2>
                                <p className="card-text">{site.description}</p>
                                <i className="bi bi-geo"></i>
                                <div className="row">
                                    <div className="col">
                                        <img src={site.stats.weather.condition.icon} style={{height:64, width:64}} />
                                    </div>
                                    <div className="col">
                                        <h6>{site.stats.weather.condition.text}</h6>
                                    </div>
                                </div>
                                <div className="row">
                                    <div className="col">
                                        <h6>Number of checkins: {site.checkin_count}</h6>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </a>
                    <div className="card-footer"><a className="btn btn-primary btn-sm" href="#!">More Info</a></div>
                </div>
            ))}
        </div>
    )
}

export default Favorites;
