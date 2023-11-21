import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { NavLink } from "react-router-dom";


class Share extends React.Component {
    constructor(props) {
        super(props);
        console.log(" IN PROPS ");
        console.log(props);
        self.divesite = props.divesite;
        this.state = {
            showDlg: false,
            photos: [],
        }
    };

    closeDlg = () => {
        this.setState({showDlg: false});
    };
    
    openDlg = () => {
        this.setState({showDlg: true});
    }

    render() {
        const { showDlg, photos } = this.state;
        return (
            <>
                <Button variant="outline-primary"
                    className="me-2" 
                    onClick={() => this.openDlg()}><i className="bi bi-share"></i> Share</Button>
	            
                <Modal
		            aria-labelledby="contained-modal-title-vcenter"
		            centered
		            show={showDlg}
		            onHide={() => this.closeDlg()}
	            >
                <Modal.Header closeButton>
                    <Modal.Title id="example-modal-sizes-title-sm">
                        Share Divesite
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form>
                        <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
                            <Form.Label>Email address</Form.Label>
                            <Form.Control
                                type="email"
                                placeholder="name@example.com"
                                autoFocus
                            />
                            </Form.Group>
                            <Form.Group
                                className="mb-3"
                                controlId="exampleForm.ControlTextarea1"
                            >
                            <Form.Label>Example textarea</Form.Label>
                            <Form.Control as="textarea" rows={3} />
                        </Form.Group>
                    </Form>
                </Modal.Body>

                <Modal.Footer>
                    <Button variant="secondary" onClick={() => this.closeDlg()} >
                        Close
                    </Button>
                </Modal.Footer>
	        </Modal>
        </>
        );
    }
}

export default Share;
