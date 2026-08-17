import React from 'react';
import SiteCard from "./SiteCard";


function SitesPanel(props) {
    const sites = props.sites || [];

    return (
        <div className="card mb-4">
            <div className="card-header">{props.title}</div>
            <div className="card-body">
                {
                    sites.length
                        ? sites.map(site => <SiteCard site={site} key={site.id} />)
                        : <p className="text-muted mb-0">{props.emptyText}</p>
                }
            </div>
        </div>
    );
}

export default SitesPanel;
