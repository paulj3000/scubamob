import { Outlet, Link } from "react-router-dom";
import Connections from "./Connections";
import SideBar from "./SideBar";


class IsPrivate extends React.Component {
  render() {
    return <h2>This is a private account</h2>
  }
}


class Layout extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            profile: props,
            error: null,
            isLoaded: false,
            buddies: []
        };
    }

    render() {
        const { profile, error, isLoaded, buddies } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else {
            return (
                <div className="row profile">
                    <div className="col-sm-3" style={{"width": "20%"}}>
                        <SideBar {...profile} />
                    </div>
                    <div className="col-sm-9">
                        {profile.is_private ? <IsPrivate /> : <Outlet {...profile} /> }
                    </div>
                </div>
            )
        }
    }
};

export default Layout;
