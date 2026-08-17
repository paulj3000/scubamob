import React from 'react';


function SiteCard(props) {
    const site = props.site;

    return (
        <a href={site.url} className="text-decoration-none">
            <div className="card mb-3">
                <img className="card-img-top" src={site.banner} alt={site.name} style={{ height: '100px', objectFit: 'cover' }} />
                <div className="card-body py-2">
                    <h6 className="card-title mb-1">{site.name}</h6>
                    <small className="text-muted">
                        {site.difficulty_display} &middot; {site.checkin_count} checkins today
                    </small>
                </div>
            </div>
        </a>
    );
}

export default SiteCard;
