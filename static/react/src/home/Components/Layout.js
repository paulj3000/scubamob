import { Outlet, Link } from "react-router-dom";

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import ProfileBlock from '../../global/Components/ProfileBlock'
import RecentDives from './RecentDives'

class Layout extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            profile: null,
        };
    }

    componentDidMount() {
        fetch(`/api/profile`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                        this.setState({
                        isLoaded: true,
                        profile: result.profile
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
        const { error, isLoaded, profile } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
  return (
    <>
    <div>
      <Row>
        <Col className="col-2">
        <ProfileBlock dataProfile = {profile} />
        <RecentDives dataProfile = {profile} />
      <nav>
        <ul>
          <li>
            <Link to={`/settings/category/account`}>Account Preferences</Link>
          </li>
          <li>
            <Link to={`/settings/category/sign-in-and-security`}>Sign In and Security</Link>
          </li>
          <li>
            <Link to={`/settings/settings2`}>Settings 2</Link>
          </li>
        </ul>
      </nav>
        </Col>

        <Col>
            <Outlet />
        </Col>



      </Row>
    </div>


    </>
  )
        }
    }
};

export default Layout;
