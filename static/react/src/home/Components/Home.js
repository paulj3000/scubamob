import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';


class Home extends React.Component {

    /*
    const navigate = useNavigate();
    const navigateDisplayMode = () => {
        navigate('/settings/item/display-mode');
    };
    */

    constructor(props) {
        super(props);
    }


    componentDidMount() {
        fetch(`/api/home`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                },

                // Note: it's important to handle errors here
                // instead of a catch() block so that we don't swallow
                // exceptions from actual bugs in components.
                (error) => {
                    this.setState({
                        isLoaded: true,
                        error
                    });
                }
            )
    }





    render() {
        return(
            <div className="App">
                <div className="col-8 mx-auto">
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
}

export default Home;
