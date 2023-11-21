import Modal from 'react-bootstrap/Modal';
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import { useState } from 'react';


class AddCheckin extends React.Component {

    constructor(props) {
        super(props);
        self.id = props.id;
        this.state = {
            openDlg: false,
        }
    }

    addCheckin = (e) => {
        e.preventDefault();
        let toSend = {divesite: self.id};

        for (let i=0; i<e.target.elements.length; ++i) {
            let elem = e.target.elements[i];
            if (elem.name) {
                if (elem.name == 'is_anonymous')
                    toSend[elem.name] = elem.checked;
                else
                    toSend[elem.name] = elem.value;
            }
        }

        fetch(`/api/divesites/${self.id}/checkins`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(toSend),
        })
            .then(res => res.json())
            .then(
                (result) => {
                    console.log('Going to Send', toSend);
                    this.setState({openDlg: false});
                },

                (error) => {
                    this.setState({
                        //isLoaded: true,
                        error
                    });
                }
            )
    }

    openDlg = () => {
        this.setState({openDlg: true});
    }

    closeDlg = () => {
        this.setState({openDlg: false});
    }

    render() {
        return (
            <>
                <button type="button"
                    className="btn btn-success btn-sm"
                    onClick={this.openDlg}>Add Checkin</button>

                <Modal
                    aria-labelledby="contained-modal-title-vcenter"
                    centered
                    show={this.state.openDlg}
                    onHide={this.closeDlg}
                >
                    <Modal.Header closeButton>
                        <Modal.Title id="example-modal-sizes-title-sm">
                            Add Checkin
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <form onSubmit={this.addCheckin}>
                            <Row>
                                <Col>
                                    <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
                                        <Form.Label>Rating</Form.Label>
                                        <Form.Select aria-label="Default select example" name="rating">
                                          <option value="1">One</option>
                                          <option value="2">Two</option>
                                          <option value="3">Three</option>
                                          <option value="4">Four</option>
                                          <option value="5">Five</option>
                                        </Form.Select>
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Row>
                                <Col>
                                    <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
                                        <Form.Label>Water Temperature</Form.Label>
                                        <Form.Control
                                            name="temp_c"
                                            type="number"
                                            autoFocus
                                        />
                                    </Form.Group>
                                </Col>

                                <Col>
                                    <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
                                        <Form.Label>Visibility</Form.Label>
                                        <Form.Control
                                            name="visibility"
                                            type="number"
                                            autoFocus
                                        />
                                    </Form.Group>
                                </Col>
                            </Row>
                            <Row>
                                <Col>
                                    <Form.Group className="mb-3" controlId="checkinForm.Review">
                                        <Form.Label>Checkin Review</Form.Label>
                                        <Form.Control as="textarea" name="review" rows={3} />
                                    </Form.Group>
                                </Col>
                            </Row>

                            <Row>
                                <Col>
                                    <Form.Group className="mb-3" controlId="checkinForm.Review">
                                        <Form.Check // prettier-ignore
                                            type="checkbox"
                                            name="is_anonymous"
                                            label="Post Anonymously"
                                        />
                                    </Form.Group>
                                </Col>
                            </Row>

                            <div className="text-end">
                                <Button variant="primary" type="submit">Add Checkin</Button>
                            </div>
                        </form>
                    </Modal.Body>
                </Modal>
            </>
        );
    }
};

export default AddCheckin;
