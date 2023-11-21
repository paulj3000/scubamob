import React from 'react';

class Checkins extends React.Component {
    constructor(props) {
        console.log('checkins', props);
        super(props);
        self.id = props.id;
        this.state = {
            id: props.id,
            error: null,
            isLoaded: false,
            checkins: []
        };
    }

    componentDidMount() {

        fetch(`/api/profile/me/checkins`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                        this.setState({
                        isLoaded: true,
                        checkins: result.checkins
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
        const { error, isLoaded, checkins } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
                <>
                    <h1>Dive Photos</h1>
                    <ul>
                        {checkins.map(item => (
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

export default Checkins;
