import React from 'react';

class Connections extends React.Component {
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
        fetch(`/api/profile/q/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({q: 'connections', id: self.id})
        })
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
                    </ul>
                </>
            );
        }
    }
}

export default Connections;
