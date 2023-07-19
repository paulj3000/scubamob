import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';
import Favorites from "./Favorites";
import Buddies from "./Buddies";
import Location from "./Location";


class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            divesites: null,
            buddies: null,
            weather: null,
        }
    }

    componentDidMount() {
        fetch(`/api/home`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                    this.setState({
                        isLoaded: true,
                        divesites: result.divesites,
                        buddies: result.buddies,
                        location: result.location,
                        weather: result.weather,
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
    }

    render() {
        const { error, isLoaded, divesites, buddies, location, weather } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return <div className="App">
                <div className="row">
                    <Location location={location} weather={weather} />;
                </div>

                <div className="row">
                    <Favorites divesites={divesites} />;
                </div>

                <div className="row">
                    <Buddies buddies={buddies} />;
                </div>

                <div className="row">
                    {this.state.buddies.list.map(buddy => (
                        <div className="col-md-4 mb-5" key={buddy.id}>
                            <div className="card h-100">
                                <div className="card-body">
                                    <h2 className="card-title">Card Two</h2>
                                    <p className="card-text">Lorem ipsum dolor sit amet, consectetur adipisicing elit. Quod tenetur ex natus at dolorem enim! Nesciunt pariatur voluptatem sunt quam eaque, vel, non in id dolore voluptates quos eligendi labore.</p>
                                </div>
                            </div>
                            <div className="card-footer"><a className="btn btn-primary btn-sm" href="#!">More Info</a></div>
                        </div>
                    ))}
                </div>


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
        }
    }
}

export default Home;
