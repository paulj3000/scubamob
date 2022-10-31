import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';

import DailyImage from './DailyImage'


const Home = () => {
    const navigate = useNavigate();
    const navigateDarkMode = () => {
        navigate('/settings/item/dark-mode');
    };

    return(
        <div className="App">
            <DailyImage />
            <div className="col-8 mx-auto">
                <ul className="list-group mb-4">
                    <li className="list-group-item">
                        <h5>Display</h5>
                    </li>
                    <li className="list-group-item d-flex justify-content-between align-items-center" onClick={navigateDarkMode}>
                        Dark Mode
                            <span>
                                <i className="bi bi-arrow-right"></i>
                            </span>
                    </li>
                </ul>


                <ul className="list-group">
                    <li className="list-group-item">
                        <h5>Account Management</h5>
                    </li>
                    <li className="list-group-item d-flex justify-content-between align-items-center">
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
