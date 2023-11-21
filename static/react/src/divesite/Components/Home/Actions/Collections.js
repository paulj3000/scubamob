import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { NavLink } from "react-router-dom";


class Collections extends React.Component {
    constructor(props) {
        super(props);
        self.divesite = props.divesite;
        this.state = {
            showDlg: false,
            showCreate: false,
            submitDisabled: false,
            collections: [],
        }
    };

    componentDidMount() {
        fetch(`/api/collections?instance=${self.id}`)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        collections: result.collections,
                        //isLoaded: true,
                    });
                },

                (error) => {
                    this.setState({
                        //isLoaded: true,
                        error
                    });
                }
            )
    }

    closeDlg = () => {
        this.setState({showDlg: false});
    };

    openDlg = () => {
        this.setState({showDlg: true});
    }

    addToCollection = (id, checked) => {
        const toSend = {
            instance_id: self.id,
            instance_type: 0,
            is_active: checked,
        };

        fetch(`/api/collections/${id}/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(toSend)
        });
    };

    addAndCreateCollection = (e) => {
        e.preventDefault();
        let toSend = {
            divesite_id: self.id,
        };

        for (let i=0; i<e.target.elements.length; ++i) {
            let elem = e.target.elements[i];
            toSend[elem.name] = elem.value;
        }

        fetch(`/api/collections/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(toSend)
        });
    };

    openCreate = () => {
        this.setState({showCreate: true});
    }

    render() {
        const { showDlg, showCreate, submitDisabled, collections } = this.state;
        return (
            <>
                <Button variant="outline-primary" className="me-2" onClick={() => this.openDlg()}>Save</Button>

                <Modal
                    aria-labelledby="contained-modal-title-vcenter"
                    centered
                    show={showDlg}
                    onHide={() => this.closeDlg()}
                >
                <Modal.Header closeButton>
                    <Modal.Title id="example-modal-sizes-title-sm">
                        Save Divesite
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {collections.map(collection => (
                        <Form.Check
                            onChange={(e) => this.addToCollection(`${collection.id}`, e.target.checked)}
                            key={collection.id}
                            type='checkbox'
                            id='collection'
                            defaultChecked={collection.is_active}
                            value={`${collection.id}`}
                            label={`${collection.name}`}
                        />
                    ))}
                    <div onClick={() => this.openCreate()} style={{"display": (showCreate ? 'none': 'block')}} >
                        <i className="bi bi-plus"></i> Create new Collection
                    </div>
                    <div style={{"display": (showCreate ? 'block': 'none')}}>
                        <form onSubmit={this.addAndCreateCollection}>
                          <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
                            <Form.Label>Name</Form.Label>
                            <Form.Control type="text" placeholder="Enter collection name..." name="name" />
                          </Form.Group>
                          <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
                            <Form.Label>Privacy</Form.Label>
                            <Form.Select aria-label="Default select example" name="is_public">
                              <option value="0">Not Public</option>
                              <option value="1">Public</option>
                            </Form.Select>
                          </Form.Group>
                          <div className="text-end">
                            <Button variant="primary" type="submit">Create</Button>
                          </div>
                        </form>
                    </div>
                </Modal.Body>
            </Modal>
        </>
        );
    }
}

export default Collections;
