import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';
import Favorites from "./Favorites";
import Buddies from "./Buddies";
import Location from "./Location";
import Others from "./Others";


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
                    <Location location={location} weather={weather} />
                </div>

                <div className="row">
                    <Favorites divesites={divesites} />
                </div>

                <div className="row">
                    <Buddies buddies={buddies} />
                </div>

                <div className="row">
                    <Others divesites={divesites} />
                </div>
            </div>
        }
    }
}

export default Home;
