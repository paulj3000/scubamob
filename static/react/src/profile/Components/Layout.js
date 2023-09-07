import { Outlet, Link } from "react-router-dom";
import Connections from "./Connections";


class Layout extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            buddies: []
        };
    }

    render() {
        const { error, isLoaded, buddies } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else {
            return (
            <>
                <div><Connections id={profileId} /></div>
              <nav>
                <ul>
                  <li>
                    <Link to={`/p/{userName}/`}>Home</Link>
                  </li>
                  <li>
                    <Link to={`/p/{userName}/buddies`}>Dive Buddies</Link>
                  </li>
                  <li>
                    <Link to={`/p/{userName}/about`}>About</Link>
                  </li>
                </ul>
              </nav>

              <Outlet />
            </>
          )
        }
    }
};

export default Layout;
