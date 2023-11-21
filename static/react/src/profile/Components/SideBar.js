import React from "react";
import { NavLink } from "react-router-dom";


class SideBar extends React.Component {

    constructor(profile) {
        super(profile);
        this.state = {
            profile: profile,
            following: profile.is_following,
        };
    }

    doFollow = () => {
        this.setState({following: !this.state.following});
        const profile = this.state.profile;

        const toSend = {
            follow: !this.state.following
        };

        fetch(`/api/profile/${profile.id}/follow`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(toSend)
        })
        .then(res => res.json())
        .then((result) => {
            this.setState({ following: result.following });
        });
    }

    render() {
        const { profile, following } = this.state;
        return (
          <>
            <div className="card profile-sidebar">
                <div className="header"></div>
                <div className="profile-userpic">
                    <img src={profile.profile_image} className="img-fluid img-thumbnail rounded-circle" alt="" />
                </div>

                <div className="profile-usertitle">
                    <div className="profile-usertitle-name">
                        {profile.full_name}
                    </div>
                    <div className="profile-usertitle-job">
                        {profile.location}
                    </div>
                    <div className="profile-usertitle-job mx-auto">

                        <ul>
                            <li style={{"display": "inline"}} className="pe-2"><i className="bi bi-person-square" /> {profile.buddy_count}</li>
                            <li style={{"display": "inline"}} className="pe-2"><i className="bi bi-stars" /> {profile.reviews_count}</li>
                            <li style={{"display": "inline"}} className="pe-2"><i className="bi bi-image" /> {profile.reviews_count}</li>
                        </ul>
                    </div>
                </div>
                {
                    (() => {
                        if (! profile.is_self) {
                            return (
                                <div className="profile-userbuttons">
                                    <button type="button" className="btn btn-success btn-sm" onClick={this.doFollow}>
                                    {
                                        following ? 'Following' : 'Follow'
                                    }
                                    </button>
                                    <button type="button" className="btn btn-danger btn-sm">Message</button>
                                </div>
                            )
                        }
                    })()
                }
            </div>

            <div className="pt-3">
                <ul className="list-group list-group-flush">
                    <li className="list-group-item">
                        <NavLink to={"/p/" + profile.username}>
                            <i className="bi bi-stars"></i> Reviews
                        </NavLink>
                    </li>
                    <li className="list-group-item">
                        <NavLink to={"/p/" + profile.username + "/gallery"}>
                            <i className="bi bi-image"></i> Photos and Videos
                        </NavLink>
                    </li>
                    <li className="list-group-item">
                        <NavLink to={"/p/" + profile.username + "/buddies"}>
                            <i className="bi bi-person-square"></i> Buddies
                        </NavLink>
                    </li>
                    <li className="list-group-item">
                        <NavLink to={"/p/" + profile.username + "/certifications"}>
                            <i className="bi bi-tablet-landscape"></i> Certifications
                        </NavLink>
                    </li>
                </ul>
                {
                    (() => {
                        if (profile.is_self) {
                            return (
                                <>
                                    <hr />
                                    <ul className="list-group list-group-flush">
                                        <li className="list-group-item">
                                            <NavLink to={"/p/" + profile.username + "/checkins"}>
                                                <i className="bi bi-tablet-landscape"></i> Checkins
                                            </NavLink>
                                        </li>
                                    </ul>
                                </>
                            )
                        }
                    })()
                }
            </div>
          </>
        );
    }
}

export default SideBar;
