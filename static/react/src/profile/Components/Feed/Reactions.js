class Reactions extends React.Component {
    constructor(props) {
        super(props);

        console.log(props);

        this.state = {
            id: props.id,
            isFlagged: props.reactions.flagged,
            type: props.type,
            error: null,
        };
    }

    flagItem = (id, checked) => {
        const state = this.state;

        const toSend = {
            instance_id: state.id,
            is_flagged: ! state.isFlagged,
        };

        fetch(`/api/feed/${state.id}/flag`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(toSend)
        })
        .then(res => res.json())
        .then(
            (result) => {
                this.setState({
                    isFlagged: result.flagged.is_flagged,
                });
            },

            (error) => {
                this.setState({
                    isLoaded: true,
                    error
                });
            }
        )
    };

    render() {
        return(
            <>
                <div className="row">
                    <div className="col-6">
                    </div>
                    <div className="col-3">
                        <ul className="list-group list-group-horizontal">
                            <li className="list-group-item"><i className="bi bi-share"></i></li>
                            <li className="list-group-item"><i className="bi bi-award"></i></li>
                            <li className="list-group-item">
                                <i className={this.state.isFlagged ? 'bi bi-flag-fill' : 'bi bi-flag'} onClick={this.flagItem} ></i>
                            </li>
                        </ul>
                    </div>
                </div>
            </>
        )
    }
}

export default Reactions;
