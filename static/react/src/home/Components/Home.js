import React from 'react';
import Location from "./Location";
import ProfileCard from "./ProfileCard";
import ActivityFeed from "./ActivityFeed";
import SitesPanel from "./SitesPanel";
import NewsPanel from "./NewsPanel";


class Home extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            divesites: null,
            friendsActivity: null,
            location: null,
            weather: null,
            news: null,
            profile: null,
        }
    }

    componentDidMount() {
        Promise.all([
            fetch(`/api/home`).then(res => res.json()),
            fetch(`/api/profile/me`).then(res => res.json()),
        ]).then(
            ([home, me]) => {
                this.setState({
                    isLoaded: true,
                    divesites: home.divesites,
                    friendsActivity: home.friends_activity,
                    location: home.location,
                    weather: home.weather,
                    news: home.news,
                    profile: me.profile,
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
        const { error, isLoaded, divesites, friendsActivity, location, weather, news, profile } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return <div className="App row">
                <div className="col-lg-3">
                    <ProfileCard profile={profile} />
                </div>

                <div className="col-lg-6">
                    <div className="mb-4">
                        <Location location={location} weather={weather} />
                    </div>

                    <ActivityFeed activity={friendsActivity} />
                </div>

                <div className="col-lg-3">
                    <SitesPanel
                        title="Favorite Dive Sites"
                        sites={divesites.favorites}
                        emptyText="You haven't favorited any dive sites yet."
                    />
                    <SitesPanel
                        title="Popular Dive Sites"
                        sites={divesites.list}
                        emptyText="No dive sites yet."
                    />
                    <NewsPanel news={news} />
                </div>
            </div>
        }
    }
}

export default Home;
