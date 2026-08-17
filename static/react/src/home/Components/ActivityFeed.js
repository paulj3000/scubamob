import React from 'react';
import Review from '../../profile/Components/Feed/Review';
import Checkin from '../../profile/Components/Feed/Checkin';


function Item(activity) {
    const user = activity.user;

    let body;
    if (activity.type === 'REVIEW') {
        body = <Review {...activity} />;
    } else if (activity.type === 'CHECKIN') {
        body = <Checkin {...activity} />;
    } else {
        return null;
    }

    return (
        <div className="mb-4">
            <div className="d-flex align-items-center mb-2">
                <a href={user.url}>
                    <img
                        src={user.profile_image}
                        className="rounded-circle me-2"
                        style={{ width: '32px', height: '32px' }}
                        alt=""
                    />
                </a>
                <a href={user.url} className="text-decoration-none">
                    <strong>{user.full_name}</strong>
                </a>
            </div>
            {body}
        </div>
    );
}

function ActivityFeed(props) {
    const activity = props.activity || [];

    return (
        <div className="card mb-4">
            <div className="card-header">What your buddies have been doing</div>
            <div className="card-body">
                {
                    activity.length
                        ? activity.map(item => <Item {...item} key={item.id} />)
                        : <p className="text-muted mb-0">
                            Nothing here yet. Once your buddies check in or review a dive site, it'll show up here.
                          </p>
                }
            </div>
        </div>
    );
}

export default ActivityFeed;
