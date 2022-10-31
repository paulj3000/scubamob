import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';


const Home = () => {
    const navigate = useNavigate();
    const navigateDarkMode = () => {
        navigate('/settings/item/dark-mode');
    };

    return(
        <div className="App">
            <div className="col-8 mx-auto">
                <ul class="list-group mb-4">
                    <li class="list-group-item">
                        <h5>Display</h5>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center" onClick={navigateDarkMode}>
                        Dark Mode
                            <span>
                                <i className="bi bi-arrow-right"></i>
                            </span>
                    </li>
                </ul>


                <ul class="list-group">
                    <li class="list-group-item">
                        <h5>Account Management</h5>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        Close Account
                            <span>
                                <i className="bi bi-arrow-right"></i>
                            </span>
                    </li>
                </ul>
            </div>
        </div>
    )
}

export default Home;
