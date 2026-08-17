import React from 'react';


function ProfileCard(props) {
    const profile = props.profile;

    return (
        <>
            <div className="card profile-sidebar">
                <div className="profile-userpic text-center">
                    <a href={'/p/' + profile.username}>
                        <img
                            src={profile.profile_image}
                            className="img-fluid img-thumbnail rounded-circle"
                            style={{ width: '100px' }}
                            alt=""
                        />
                    </a>
                </div>
                <div className="profile-usertitle text-center">
                    <div className="profile-usertitle-name">
                        <a href={'/p/' + profile.username}>{profile.full_name}</a>
                    </div>
                    <div className="profile-usertitle-job">
                        <i className="bi bi-person-square" /> {profile.buddy_count} buddies
                    </div>
                </div>
            </div>

            <div className="pt-3">
                <ul className="list-group list-group-flush">
                    <li className="list-group-item">
                        <a href="/sites/">
                            <i className="bi bi-geo"></i> Favorite Dive Sites
                        </a>
                    </li>
                    <li className="list-group-item">
                        <a href="/equipment/">
                            <i className="bi bi-tools"></i> My Equipment
                        </a>
                    </li>
                    <li className="list-group-item">
                        <a href={'/p/' + profile.username + '/buddies'}>
                            <i className="bi bi-people"></i> My Buddies
                        </a>
                    </li>
                    <li className="list-group-item">
                        <a href="/logbooks/">
                            <i className="bi bi-journal-text"></i> My Logbook
                        </a>
                    </li>
                </ul>
            </div>
        </>
    );
}

export default ProfileCard;
