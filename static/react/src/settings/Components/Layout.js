import { Outlet, Link } from "react-router-dom";

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

const Layout = () => {
  return (
    <>
    <div>
      <Row>
        <Col className="col-2">
        <h1>Settings</h1>
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
};

export default Layout;
