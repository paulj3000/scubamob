import React from 'react';
import Review from './Feed/Review';
import Checkin from './Feed/Checkin';


function Item(item) {
	/* this is WEIRD */
    if (item.type == 'REVIEW') {	
        return <Review {...item} />;
    }
    else if (item.type == 'CHECKIN') {	
        return <Checkin {...item} />;
    }
    return <h6>UNKNOWN</h6>;
}

class Feed extends React.Component {
    constructor(props) {
        super(props);
        self.id = props.id;
        this.state = {
            id: props.id,
            error: null,
            isLoaded: false,
            feed: []
        };
    }

    componentDidMount() {
        fetch(`/api/feed/${self.id}`)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        isLoaded: true,
                        feed: result.feed
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
        const { error, isLoaded, feed } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
                <>
		            <div className="row text-center text-lg-start">
                        <h2>Activity</h2>
                        <hr />
                        {
                            (() => {
                                if (feed.length) {
                                    return feed.map((item) => {
			                            return <Item {...item} key={item.id} />
                                    })
                                } else {
                                    return <div>nothing here yet</div>
                                }
                            })()
                        }
		            </div>
                </>
            );
        }
    }
}

export default Feed;
