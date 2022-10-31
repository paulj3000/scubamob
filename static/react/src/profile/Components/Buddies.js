import React from 'react';

class Buddies extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            buddies: []
        };
    }

    componentDidMount() {
        fetch(`/api/profile/${profileId}/buddies`)
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
                    <ul>
                        {buddies.map(item => (
                            <li key={item.id}>
                                <img src={item.profile_image} alt="profile image" />
                                {item.full_name}
                            </li>
                        ))}
                    </ul>
                </>
            );
        }
    }
}

export default Buddies;
