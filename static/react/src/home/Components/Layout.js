import { Outlet } from "react-router-dom";

import Container from 'react-bootstrap/Container';

const Layout = () => {
  return (
    <Container fluid className="p-3">
        <Outlet />
    </Container>
  )
};

export default Layout;
