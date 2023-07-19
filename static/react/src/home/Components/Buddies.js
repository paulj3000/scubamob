import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';


function Buddies(props) {
    return (
        <div className="row">

            {props.buddies.list.map(buddy => (
                <div className="col-md-4 mb-5" key={buddy.id}>
                    <div className="card h-100">
                        <img className="card-img-top" src={buddy.profile_image} alt="Card image cap" />
                        <div className="card-body">
                            <h2 className="card-title">{buddy.full_name}</h2>
                        </div>
                    </div>
                    <div className="card-footer"><a className="btn btn-primary btn-sm" href="#!">More Info</a></div>
                </div>
            ))}
        </div>
    )
}

export default Buddies;
