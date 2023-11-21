import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Container from 'react-bootstrap/Container';

import React from 'react';
import Actions from "./Home/Actions";
import Map from "./Home/Map";
import Tags from "./Home/Tags";
import Weather from "./Weather";


class Checkins extends React.Component {
    constructor(props) {
        super(props);
        self.id = props.id;
        this.state = {
            error: null,
            isLoaded: false,
            divesite: null,
            weather: null,
        }
    }

    componentDidMount() {
        fetch(`/api/divesites/${self.id}`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                    this.setState({
                        isLoaded: true,
                        divesite: result.divesite,
                        weather: result.weather,
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

    render() {
        const { error, isLoaded, divesite, weather } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return (
                <>
<section className="bg-secondary py-5">
    <Container>
        <div className="loading" data-mdb-parent-selector="#loading-test">
            <div className="spinner-border loading-icon" role="status"></div>
            <span className="loading-icon">Loading...</span>
        </div>
    </Container>
</section>
                </>
            );
        } else {
            return (
                <>
<section className="bg-secondary py-5 jumbotron" style={{backgroundImage: `url(${divesite.banner})`}}>
    <Container>
        <div className="row gx-5 align-items-left justify-content-left">
            <div className="col-lg-8 col-xl-7 col-xxl-6">
                 <div className="my-5 text-center text-xl-start">
                     <h1 className="display-5 fw-bolder text-white mb-2">{divesite.name}</h1>
                    <p className="lead fw-normal text-white-50 mb-4">Quickly design and customize responsive mobile-first sites with Bootstrap, the world’s most popular front-end open source toolkit!</p>

                    <div className="d-grid gap-3 d-sm-flex justify-content-sm-center justify-content-xl-start">
                        <a className="btn btn-primary btn-lg px-4 me-sm-3" href="#features">Get Started</a>
                        <a className="btn btn-outline-light btn-lg px-4" href="#!">Learn More</a>
                    </div>


                    <div className="d-grid gap-3 d-sm-flex justify-content-sm-center justify-content-xl-start">
                        <Tags tags={divesite.tags} location={divesite.location} />
                    </div>
                </div>
            </div>
            <div className="col align-text-bottom">
                this is a test
            </div>
        </div>
    </Container>
</section>

<Container>
    <Row>
        <Col className="col-6">
            <Actions id={divesite.id} />
        </Col>
    </Row>
    <Row>
        <Col className="col-6">
            <Map {...divesite.coords} />
        </Col>
        <Col>
            <Weather weather={divesite.stats.weather} />
        </Col>
    </Row>
</Container>
                </>
            )
        }
    }
}

export default Checkins;
