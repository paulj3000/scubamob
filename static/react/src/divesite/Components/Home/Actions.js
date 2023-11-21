import Modal from 'react-bootstrap/Modal';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import { NavLink } from "react-router-dom";

import Photos from './Actions/Photos';
import Collections from './Actions/Collections';
import Share from './Actions/Share';


class Actions extends React.Component {
    constructor(props) {
        super(props);
        self.id = props.id;
        this.state = {
            showShareDlg: false,
            smShow: false,
            smSave: false,
            collections: [],
            collectionsLoaded: false,
        }
    };

    render() {
        return (
            <>
                <div role="group" aria-label="Basic example">
                    <Photos divesite={self.divesites} />
                    <button type="button" className="btn btn-primary me-2">Left</button>
                    <Share divesite={self.divesites} />
                    <Collections divesite={self.divesites} />
                </div>
            </>
        );
    }
}

export default Actions;
