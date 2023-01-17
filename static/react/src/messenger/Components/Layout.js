import { Outlet, Link } from "react-router-dom";

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import React from "react";

class Layout extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            chats: [],
            users: [],
            idx: 0,
            me: null
        };
    }

    componentDidMount() {
        const fetchReq1 = fetch(`/api/chats/all`)
            .then(res => res.json());

        const allData = Promise.all([fetchReq1]);
        allData.then((res) => {
            res = res[0];

            // define the Me constant
            const me = res.me;
            const users = res.users;

            res.chats.forEach(chat => {
                if (! chat.title) {

                    const chatUsers = chat.users.filter(e => { return e != me });
                    if (chatUsers.length > 1)
                        chat.title = 'Coming Up';
                    else
                        chat.title = users[chatUsers[0]].full_name;
                }
            });

            this.setState({
                me: res.me,
                chats: res.chats,
                users: res.users,
            });
        });
    }

    render() {
        return (
    <>
    <Row className="row-broken">
        <div className="col-sm-3 col-xs-12">
            <div className="col-inside-lg decor-default chat nooverflow" tabIndex="5000">
                <div className="chat-users">
                    <div className="mb-2 d-flex justify-content-between align-items-center">
                        <div className="col-9">Messaging</div>
                        <div className="me-1"><i className="bi bi-three-dots"></i></div>
                        <Link to="/messenger/new"><i className="bi bi-pencil-square"></i></Link>
                    </div>

                    <Row>
                        <div className="input-group mb-3">
                            <span className="input-group-text" id="basic-addon1"><i className="bi bi-search"></i></span>
                            <input type="text" className="form-control" placeholder="Search Messages" aria-label="search" aria-describedby="search messages" />
                        </div>
                    </Row>
                    <div id="chats-list">
                        {this.state.chats.map(chat => (
                        <div key={chat.id}>
                            <Link
                                to={{
                                    pathname: `/messenger/t/${chat.id}`
                                   }}
                            >
                            <div className="user">
                                <div className="avatar">
                                    <img src="https://bootdey.com/img/Content/avatar/avatar1.png" alt="User name" />
                                    <div className="status off"></div>
                                </div>
                                <div className="name">{chat.title}</div>
                                <div className="mood">User mood</div>
                            </div>
                            </Link>
                        </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>

        <div className="col-sm col-xs-12 chat nooverflow">
            <Outlet />
        </div>
    </Row>
    </>
      )
  }
};

export default Layout;
