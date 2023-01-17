import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';

import ChatWindow from './ChatWindow'


class Chat extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            chats: [],
            users: [],
            idx: 0,
            me: null
        };
    }

    render() {
        return (
            <>
                <ChatWindow />
            </>
        )
    }
}

export default Chat;
