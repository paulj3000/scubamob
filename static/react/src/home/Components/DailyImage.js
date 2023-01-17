import { Outlet, Link } from "react-router-dom";

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import ProfileBlock from '../../global/Components/ProfileBlock'

class DailyImage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            image: null,
        };
    }

    componentDidMount() {
        fetch(`/api/galleries/daily`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                        this.setState({
                        isLoaded: true,
                        image: result.image
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

    render() {
        const { error, isLoaded, image } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
  return (
    <>
        <img src={image.url} />
    </>
  )
        }
    }
};

export default DailyImage;
