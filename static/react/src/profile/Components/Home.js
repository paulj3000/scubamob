import Feed from "./Feed";

const Home = (profile) => {
    return(
        <>
            <div className="row">
                <div className="col">
                    <Feed id={profile.id} />
                </div>
                <div className="col-sm-3">
                    <ul className="list-group list-group-flush">
                    </ul>

                    <ul className="list-group list-group-flush">
                        <li className="list-group-item"><h4>Location</h4></li>
                        <li className="list-group-item">{profile.location}</li>
                        <li className="list-group-item"><h4>Buddy Count</h4></li>
                        <li className="list-group-item">{profile.buddy_count}</li>
                    </ul>
                </div>
            </div>
        </>
    )
}

export default Home;
