import React from 'react';

class DisplayMode extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            settings: null,
            selected: null,
            options: []
        };

        this.onValueChange = this.onValueChange.bind(this);
        this.originalSelected = null;
    }

    componentDidMount() {
        fetch(`/api/settings/display-mode`)
            .then(res => res.json())
            .then(
                (result) => {
                    const settings = result.settings[0];
                    const selected = (settings.selected) ? settings.selected.value : null;
                    this.originalSelected = selected;
                    this.setState({
                        isLoaded: true,
                        settings: settings,
                        selected: selected,
                        options: settings.options,
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

    onValueChange(event) {
        this.setState({
            selected: event.target.value,
        });

        fetch(`/api/settings/display-mode`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                'settings': [{
                    'key': 'display_mode',
                    'value': event.target.value
                }]
            })
        });
    }

    render() {
        const { error, isLoaded, settings, options, selected } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
                <div className="App">
                    <div className="col-9 mx-auto">
                        <h1>{settings.title}</h1>
                        <div className="form-check">
                            {options.map(item => (
                                (() => {
                                    return (
                                            <div className="form-check" key={item.id}>
                                                <input 
                                                    className="form-check-input"
                                                    type="radio"
                                                    name={item._id}
                                                    id={item.id}
                                                    checked={item.id === selected}
                                                    value={item.id} onChange={this.onValueChange} />
                                                <label>
                                                {item.display}
                                                </label>
                                            </div>
                                    )
                                })()
                            ))}
                        </div>
                    </div>
                </div>
            );
        }
    }
};

export default DisplayMode;
