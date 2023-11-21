import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { NavLink } from "react-router-dom";


class Photos extends React.Component {
    constructor(props) {
        super(props);
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

        /*
        fetch(`/api/collections`)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        collections: result.collections,
                        //isLoaded: true,
                    });

                    this.setState({smSave: true});
                },

                (error) => {
                    this.setState({
                        //isLoaded: true,
                        error
                    });
                }
            )
        */


    };

    render() {
        const { showDlg, photos } = this.state;
        return (
            <>
                <Button 
                    variant="outline-primary" 
                    className="me-2" 
                    onClick={() => this.openDlg()}>Photos</Button>

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

export default Photos;
