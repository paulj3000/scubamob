import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';
import Site from "./Site";


function OtherSite(props) {
    let site = props.site;
    return (
        <div className="col-md-4 mb-5" key={site.id}>
            <a href={site.url}>
                <div className="card h-100">
                    <img className="card-img-top" src={site.banner} alt="Card image cap" />
                    <div className="card-body">
                        <h2 className="card-title">{site.name}</h2>
                        <div className="row">
                            <div className="col">
                                <div>
                                    From User 1
                                </div>
                                <div>
                                    (five stars)
                                </div>
                            </div>
                        </div>
                        <div className="row">
                            <div className="col">
                                <h6>Number of checkins: {site.checkin_count}</h6>
                                <h6>Visibility 30 ft</h6>
                                <h6>Water Temperature 65 F</h6>
                            </div>
                        </div>
                    </div>
                </div>
            </a>
            <div className="card-footer"><a className="btn btn-primary btn-sm" href="#!">More Info</a></div>
        </div>
    )
}

function Others(props) {
    return (
        <>
        <h2>Other Checkins</h2>
        <div className="row">
            {props.divesites.list.map(site => (
                <OtherSite site={site} key={site.id} />
            ))}
        </div>
        </>
    )
}

export default Others;
