import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';


function Buddies(props) {
    return (
        <div className="row">

            {props.buddies.list.map(buddy => (
                <div className="col-md-4 mb-5" key={buddy.id}>
                    <div className="bg-white rounded shadow-sm py-5 px-4">
                        <img className="img-fluid rounded-circle mb-3 img-thumbnail shadow-sm" src={buddy.profile_image} alt="Card image cap" width="100" />
                        <h5 className="mb-0">{buddy.full_name}</h5>
                    </div>
                    <div className="card-footer"><a className="btn btn-primary btn-sm" href="#!">More Info</a></div>
                </div>
            ))}
        </div>
    )
}

export default Buddies;
