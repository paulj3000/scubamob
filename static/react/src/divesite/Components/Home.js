import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { BrowserRouter, Routes, Route, Outlet, Link } from "react-router-dom";
import Container from 'react-bootstrap/Container';

import React from 'react';
import Map from "./Home/Map";
import Tags from "./Home/Tags";
import Weather from "./Weather";

import Actions from "./Home/Actions";
import AddCheckin from "./Home/Actions/AddCheckin";


class Home extends React.Component {
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
        Promise.all([
          fetch(`/api/divesites/${self.id}`).then(res => res.json()),
          fetch(`/api/divesites/${self.id}/reviews`).then(res => res.json())
        ])
        .then((result) => {
            this.setState({
                isLoaded: true,
                divesite: result[0].divesite,
                weather: result[0].weather,
                reviews: result[1].reviews,
            });
        })

        /*
        fetch(`/api/divesites/${self.id}`)
            .then(res => res.json())
            .then(
                (result) => {
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
        */
    }

    addCheckin = (dlg) => {
        alert("IN HERE ... ");
    }

    render() {
        const { error, isLoaded, divesite, weather, reviews } = this.state;
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
            <div>
                <Link to={divesite.url + '/checkins'}>Checkins</Link>
            </div>
            <div>
               <AddCheckin id={divesite.id} addCheckin={this.addCheckin} />
            </div>
        </Col>
    </Row>
    <Row>
        <Col className="col-6">
            <h4>Reviews</h4>
            {
                (() => {
                    if (reviews.length) {
                        return reviews.map((item) => {
                            return <div key={item.id}>{item.review}</div>
                        })
                    } else {
                        return <div>no reviews yet</div>
                    }
                })()
            }
        </Col>
    </Row>
</Container>
                </>
            )
        }
    }
}

export default Home;
