import { Outlet, Link } from "react-router-dom";


class Layout extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            buddies: []
        };
    }

    componentDidMount() {
        fetch(`/api/profile/${profileId}/buddies`)
            .then(res => res.json())
            .then(
                (result) => {
                    console.log(result);
                        this.setState({
                        isLoaded: true,
                        buddies: result.buddies
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
        const { error, isLoaded, buddies } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            return (
            <>
              <nav>
                <ul>
                  <li>
                    <Link to={`/p/${userName}/`}>Home</Link>
                  </li>
                  <li>
                    <Link to={`/p/${userName}/buddies`}>Dive Buddies</Link>
                  </li>
                  <li>
                    <Link to={`/p/${userName}/about`}>About</Link>
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
