import { Outlet, Link } from "react-router-dom";
import ListGroup from 'react-bootstrap/ListGroup';
import {Routes, Route, useNavigate} from 'react-router-dom';


import React from 'react';

export default function SignInAndSecurity() {

    const navigate = useNavigate();
    const navigateEmailAddresses = () => {
        // 👇️ navigate to /contacts
        navigate('/settings/item/manage-email-addresses');
    };

    return(
        <div className="App">
            <div className="col-8 mx-auto">
                <ul class="list-group mb-4">
                    <li class="list-group-item">
                        <h5>Account access</h5>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center"
                        onClick={navigateEmailAddresses}>
                        Email Addresses
                            <span>
                                paulj1999@yahoo.com <i className="bi bi-arrow-right"></i>
                            </span>
                    </li>
                </ul>
            </div>
        </div>
    )
}
