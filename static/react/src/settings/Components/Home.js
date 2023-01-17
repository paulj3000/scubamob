import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';
import { useState, useEffect } from "react";
import BasicsModal from "./modals/BasicsModal";


class Home extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            displayMode: null,
            fullname: null,
            username: null,
            email: null,
            pronoun: null,
        };
    }

    componentDidMount() {
        const fetchReq1 = fetch(`/api/settings/list?settings=display_mode,pronoun`)
            .then(res => res.json());

        const fetchReq2 = fetch(`/api/settings/list/general`)
            .then(res => res.json());

        const allData = Promise.all([fetchReq1, fetchReq2]);
        allData.then((res) => {
            this.setState({
                displayMode: res[0].settings.display_mode,
                pronoun: res[0].settings.pronoun,
                fullname: res[1].full_name,
                username: res[1].username,
                email: res[1].email,
                isLoaded: true
            });
        });

        /*
            .then(
                (result) => {
                    const settings = result.settings;
                    this.setState({
                        displayMode: settings.display_mode,
                        isLoaded: true
                    });
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
        */
    }

    render() {
        const { error, isLoaded, displayMode, fullname, username, email, pronoun } = this.state;

        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return(
                <div className="App">
                    <div className="col-8 mx-auto">
                        <ul className="list-group mb-4">
                            <li className="list-group-item">
                                <h5>Profile information</h5>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                                <div className="me-5">
                                    <h6 style={{ marginBottom: 0 }}>Name</h6>
                                </div>
                                <div className="ms-2 me-auto">
                                    <Link to={'/settings/item/basic-info'}>{fullname}</Link>
                                </div>
                                <Link to={'/settings/item/basic-info'}>
                                    <i className="bi bi-arrow-right"></i>
                                </Link>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                                <div className="me-5">
                                    <h6 style={{ marginBottom: 0 }}>Username</h6>
                                </div>
                                <div className="ms-2 me-auto">
                                    <Link to={'/settings/item/basic-info'}>{username}</Link>
                                </div>
                                <Link to={'/settings/item/basic-info'}>
                                    <i className="bi bi-arrow-right"></i>
                                </Link>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                                <div className="me-5">
                                    <h6 style={{ marginBottom: 0 }}>{pronoun.title}</h6>
                                </div>
                                <div className="ms-2 me-auto">
                                    <Link to={'/settings/item/basic-info'}>
                                        {
                                            pronoun.value ? pronoun.value : 'Not Set'
                                        }
                                    </Link>
                                </div>
                                <Link to={'/settings/item/basic-info'}>
                                    <i className="bi bi-arrow-right"></i>
                                </Link>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                                <div className="me-5">
                                    <h6 style={{ marginBottom: 0 }}>Email</h6>
                                </div>
                                <div className="ms-2 me-auto">
                                    Primary:<Link to={'/settings/item/basic-info'}>{email}</Link>
                                </div>
                                <Link to={'/settings/item/basic-info'}>
                                    <i className="bi bi-arrow-right"></i>
                                </Link>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                                <div className="ms-2 me-auto">
                                    <Link to={'/settings/item/basic-info'}>Name and all of that stuff</Link>
                                </div>
                                <Link to={'/settings/item/basic-info'}>
                                    <i className="bi bi-arrow-right"></i>
                                </Link>
                            </li>
                        </ul>
                    </div>

                    <div className="col-8 mx-auto">
                        <ul className="list-group mb-4">
                            <li className="list-group-item">
                                <h5>{displayMode.title}</h5>
                            </li>
                            <li className="list-group-item d-flex justify-content-between align-items-center">
                                <div className="ms-2 me-auto">
                                    <Link to={'/settings/item/display-mode'}>{displayMode.display}</Link>
                                </div>
                                <Link to={'/settings/item/display-mode'}>
                                    <i className="bi bi-arrow-right"></i>
                                </Link>
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
    }
}

export default function(props) {
  const navigation = useNavigate();

  return <Home {...props} navigation={navigation} />;
}

//https://stackoverflow.com/questions/63858745/how-to-use-multiple-material-ui-dialog-with-react
//export default Home;
