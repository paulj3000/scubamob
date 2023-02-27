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
