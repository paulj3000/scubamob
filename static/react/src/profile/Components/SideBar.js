import React from "react";
import { NavLink } from "react-router-dom";


class SideBar extends React.Component {

    constructor(profile) {
        super(profile);
        this.state = {
            profile: profile,
            following: profile.is_following,
            uploadingAvatar: false,
            avatarError: null,
        };
        this.avatarInputRef = React.createRef();
    }

    onAvatarClick = () => {
        this.avatarInputRef.current.click();
    }

    onAvatarFileSelected = (event) => {
        const file = event.target.files[0];
        event.target.value = null;

        if (!file) {
            return;
        }

        this.setState({ uploadingAvatar: true, avatarError: null });

        const formData = new FormData();
        formData.append('image', file);

        fetch(`/api/settings/profile-image/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: formData,
        })
        .then(res => res.json().then(data => ({ ok: res.ok, data })))
        .then(({ ok, data }) => {
            if (!ok) {
                this.setState({ uploadingAvatar: false, avatarError: data.errors || 'Upload failed' });
                return;
            }

            this.setState((state) => ({
                uploadingAvatar: false,
                profile: { ...state.profile, profile_image: data.profile_image },
            }));
        })
        .catch(() => {
            this.setState({ uploadingAvatar: false, avatarError: 'Upload failed' });
        });
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
        const { profile, following, uploadingAvatar, avatarError } = this.state;
        return (
          <>
            <div className="card profile-sidebar">
                <div className="header"></div>
                <div className="profile-userpic">
                    <img src={profile.profile_image} className="img-fluid img-thumbnail rounded-circle" alt="" />
                    {
                        profile.is_self &&
                        <div className="text-center mt-1">
                            <button
                                type="button"
                                className="btn btn-sm btn-outline-secondary"
                                onClick={this.onAvatarClick}
                                disabled={uploadingAvatar}
                            >
                                {uploadingAvatar ? 'Uploading...' : 'Change photo'}
                            </button>
                            <input
                                ref={this.avatarInputRef}
                                type="file"
                                accept="image/jpeg,image/png,image/webp"
                                style={{ display: 'none' }}
                                onChange={this.onAvatarFileSelected}
                            />
                            {avatarError && <div className="text-danger small mt-1">{avatarError}</div>}
                        </div>
                    }
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
