import React from 'react';

class ManageEmailAddresses extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            emails: []
        };
    }

    componentDidMount() {
        fetch(`/api/settings/emails`)
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
                <>
                    <h1>Email addresses</h1>
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
                </>
            );
        }
    }
};

export default ManageEmailAddresses;
