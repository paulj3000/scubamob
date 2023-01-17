import { Outlet, Link } from "react-router-dom";
import ListGroup from 'react-bootstrap/ListGroup';
import {Routes, Route, useNavigate} from 'react-router-dom';


import React from 'react';

class ProfileBlock extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data: this.props.dataProfile
        }
    }

    render() {
        const {data} = this.state;
        return(
            <>
                <div className="card mb-4">
                    <div className="card-body text-center">
                        <a href={'/p/' + data.username}>
                            <img src={data.profile_image} alt="profile image for user.get_full_name"
                            className="rounded-circle img-fluid" style={{width: '150px'}} />
                        </a>
                        <h6 className="my-3">
                            <a href={'/p/' + data.username}>{data.full_name}</a>
                        </h6>
                        <p className="text-muted mb-1">Full Stack Developer</p>
                        <p className="text-muted mb-4">Bay Area, San Francisco, CA</p>
                        <div className="d-flex justify-content-center mb-2">
                            <button type="button" className="btn btn-primary">Follow</button>
                            <button type="button" className="btn btn-outline-primary ms-1">Message</button>
                        </div>
                    </div>
                </div>
            </>
        )
    }
}

export default ProfileBlock;
