import React from 'react';

class Buddies extends React.Component {
    constructor(props) {
        super(props);
        self.id = props.id;
        this.state = {
            id: props.id,
            error: null,
            isLoaded: false,
            buddies: []
        };
    }

    componentDidMount() {
        fetch(`/api/profile/${self.id}/buddies`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                        this.setState({
                        isLoaded: true,
                        buddies: result.buddies
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
        const { error, isLoaded, buddies } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
                <>
                    <h1>Dive Buddies</h1>
		    <div className="row text-center text-lg-start">
                    {buddies.map(item => (
			<div className="col-lg-6 col-md-6 col-6 pe-5">
			    	<div className="row d-flex justify-content-center align-items-center h-11">
                                        <div className="card" style={{"border-radius": "15px"}}>
                                            <div className="card-body p-4">
                                                <div className="d-flex text-black">
                                                    <div className="flex-shrink-0">
			    <a href={item.url} title={"link to " + item.username}>
                            		                <img src={item.profile_image} alt="profile image" style={{width: "90px", "border-radius": "10px"}} />
			    </a>
                                                    </div>
                                                    <div className="flex-grow-1 ms-3">
			    <a href={item.url} title={"link to " + item.username}>
			                                <h5 className="mb-1">{item.full_name}</h5>
			    </a>
			    <a href={item.url} title={"link to " + item.username}>
			                                <p className="mb-2 pb-1">{item.username}</p>
			    </a>
			                                <div className="d-flex justify-content-start rounded-3 p-2 mb-2" style={{"background-color": "#efefef"}}>
			                                    <div>
			                                        <p className="small text-muted mb-1">Articles</p>
			                                        <p className="mb-0">41</p>

			                                    </div>
			                                    <div className="px-3">
			                                        <p className="small text-muted mb-1">Followers</p>
			                                        <p className="mb-0">976</p>

			                                    </div>
			                                    <div>
			                                        <p className="small text-muted mb-1">Rating</p>
			                                        <p className="mb-0">8.6</p>

			                                    </div>
			                                </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
			    	</div>
			</div>
                    ))}
		    </div>
                </>
            );
        }
    }
}

export default Buddies;
