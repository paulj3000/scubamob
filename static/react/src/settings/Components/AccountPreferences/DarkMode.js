import React from 'react';

class DarkMode extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            emails: []
        };
    }

    componentDidMount() {
        fetch(`/api/settings/dark-mode`)
            .then(res => res.json())
            .then(
                (result) => {
                        this.setState({
                        isLoaded: true,
                        emails: result.emails
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
        const { error, isLoaded, emails } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
                <div className="App">
                    <div className="col-9 mx-auto">
                        <h1>Dark Mode</h1>
                        <ul>
                            {emails.map(item => (
                                (() => {
                                    if(item.is_primary) {
                                        return (
                                            <>
                                                <li>Primary Email</li>
                                                <li>{item.email}</li>
                                            </>
                                        )
                                    } else {
                                        (
                                            <li>{item.email} -> Make Primary</li>
                                        )
                                    }
                                })()
                            ))}
                        </ul>
                    </div>
                </div>
            );
        }
    }
};

export default DarkMode;
