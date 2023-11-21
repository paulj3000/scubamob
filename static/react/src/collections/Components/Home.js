import Row from 'react-bootstrap/Row';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';
import Modal from 'react-bootstrap/Modal';
import Card from 'react-bootstrap/Card';

import React from 'react';

function CollectionItem(props) {
    return (
        <Card>
            <img alt="header" />
            <Card.Body>
                <a href="#" className="btn btn-primary">{props.name}</a>
            </Card.Body>
        </Card>
    )
}

class Home extends React.Component {
    constructor(props) {
        super(props);
        self.id = props.id;
        this.state = {
            error: null,
            collections: [],
            isLoaded: false,
            showShareDlg: false,
            smShow: false,
            name: "",
            is_public: true,
        }
    }

    componentDidMount() {
        fetch(`/api/collections`)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        collections: result.collections,
                        isLoaded: true,
                    });
                },

                (error) => {
                    this.setState({
                        isLoaded: true,
                        error
                    });
                }
            )
    }

    createCollection = () => {
        const toSend = {
            name: this.state.name,
            is_public: (this.state.is_public == '1') ? true : false,
        };

        fetch(`/api/collections/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify(toSend)
        })
        .then(res => res.json())
        .then((result) => {
            let collections = this.state.collections;

            //this.state.collections.push(result);

            this.setState(collections => ({
                collections: this.state.collections.concat(result)
            }));

            this.setState({ smShow: false });
        });
    };


    render() {
        const { error, collections, isLoaded, showShareDlg, smShow, is_public, name } = this.state;

        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
                <>
<Container>
    <section className="container">
      <ul className="nav nav-tabs pt-5">
        <li className="nav-item"><a className="nav-link active" href="#">Home</a></li>
        <li className="nav-item"><a className="nav-link" href="#">Data</a></li>
        <li className="nav-item ms-auto">
          <button type="button" className="btn btn-primary ml-2" onClick={() => this.setState({ smShow: true })}>Create a Collection</button>
        </li>
      </ul>
    </section>
    <Row>
            {this.state.collections.map((item) => (
                <Col md="4" lg="3" xs="6"
                     id={item.id}
                     key={item.id}>
                        <CollectionItem {...item} />
                </Col>
            ))}
    </Row>
</Container>

      <Modal
        aria-labelledby="contained-modal-title-vcenter"
        centered
        show={smShow}
        onHide={() => this.setState({ smShow: false })}
      >
        <Modal.Header closeButton>
          <Modal.Title id="example-modal-sizes-title-sm">
            Create a Collection
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group className="mb-3" controlId="exampleForm.ControlInput1">
              <Form.Label>New Collection</Form.Label>
              <Form.Control
                onChange={e => this.setState({ name: e.target.value })}
                type="text"
                autoFocus
              />
            </Form.Group>
            <Form.Group
              className="mb-3"
              controlId="exampleForm.ControlTextarea1"
            >

                <div key={`inline-radio`} className="mb-3">
                    <Form.Check
                        inline
                        onChange={e => this.setState({ is_public: e.target.value })}
                        label="Public"
                        name="is_public"
                        value="1"
                        type="radio"
                        id="inline-radio-public"
                    />
                    <Form.Check
                        inline
                        onChange={e => this.setState({ is_public: e.target.value })}
                        defaultChecked={true}
                        label="Non-Public"
                        value="0"
                        name="is_public"
                        type="radio"
                        id="inline-radio-non-public"
                    />
                </div>
            </Form.Group>
        </Form>
        <div>A public Collection can be openly featured on Yelp and alerts followers when you make updates. A non-public Collection can still be visible to others if you share a link to it.</div>
        </Modal.Body>
        <Modal.Footer>
            <Button variant="primary" onClick={this.createCollection}>
                Save
            </Button>
            <Button variant="secondary" onClick={() => this.setState({ smShow: false })} >
                Cancel
            </Button>
        </Modal.Footer>


      </Modal>


                </>
            )
    }
    }
}

export default Home;
