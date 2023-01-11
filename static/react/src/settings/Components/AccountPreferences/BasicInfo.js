import React from 'react';

class BasicInfo extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            settings: null,
            pronoun: null,
            custom: null,
            options: [],
        };

        this.onChangePronoun = this.onChangePronoun.bind(this);
        this.onSubmit = this.onSubmit.bind(this);
        this.originalSelected = null;
    }

    componentDidMount() {
        fetch(`/api/settings/list/options?settings=pronoun`)
            .then(res => res.json())
            .then(
                (result) => {
                    const settings = result.settings;
                    let toUpdate = {settings:settings};
                    result.settings.forEach(e => {
                        toUpdate[e.id] = e.options;
                    });
                    toUpdate.isLoaded = true;
                    this.setState(toUpdate);
                    this.onChangePronoun();
                },

                (error) => {
                    this.setState({
                        isLoaded: true,
                        error
                    });
                }
            )
    }

    onSubmit(event) {
        const selectedValue = event.target.value;
        event.preventDefault();

        let toSend = {
            key: 'pronoun',
            value: this.state.pronouns,
        }

        if (this.state.pronouns == 'custom')
            toSend.custom = this.state.custom

        fetch(`/api/settings/pronoun`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({settings: [toSend]})
        });
    }

    onChangePronoun(event) {
        const target = event.target;
        const selectedValue = target.value;
        const name = target.name;

        this.setState({
            [name]: selectedValue
        });

        if (name == 'pronouns') {
            const selected = this.state.pronoun.find(e => {
                return e.id == selectedValue;
            });

            if (selected && selected.isCustom) {
                pronounCustom.style.display = 'block';
            } else {
                pronounCustom.style.display = 'none';
                this.setState({ custom: null });
            }
        }
    }

    render() {
        const { error, isLoaded, settings, pronoun, options } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
                <div className="App">
                    <div className="col-9 mx-auto">
                        <h1>settings.title</h1>
                        <div className="form-check">
                        </div>

                        <form onSubmit={this.onSubmit}>
                        <div className="mb-3">
                            <label htmlFor="pronouns">Pronouns</label>
                            <select className="form-control" id="pronouns" onChange={this.onChangePronoun} name="pronouns">
                                <option value="">Please select</option>
                                {pronoun.map(item => (
                                    (() => {
                                        return (
                                            <option data-custom={ item.isCustom } key={item.id} value={item.id}>{item.display}</option>
                                        )
                                    })()
                                ))}
                            </select>
                        </div>

                        <div className="mb-3" id="pronounCustom" style={{display:'none'}}>
                            <label htmlFor="exampleInputEmail2">Enter custom pronouns</label>
                            <input type="input" className="form-control" id="custom" aria-describedby="custom" onChange={this.onChangePronoun} name="custom" />
                        </div>
                        <button type="submit" className="btn btn-primary">Submit</button>
                        </form>

                    </div>
                </div>
            );
        }
    }
};

export default BasicInfo;
