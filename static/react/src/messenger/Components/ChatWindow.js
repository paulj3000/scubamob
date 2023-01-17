import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';
import { useParams } from 'react-router-dom';
import React, { useEffect, useRef } from 'react'

import DailyImage from './DailyImage'


export function withRouter(Children){
    return(props) => {
        const match  = {params: useParams()};
        return <Children {...props}  match = {match}/>
    }
}

class ChatWindow extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            message: null,
            messages: [],
            users: [],
            me: null,
            userCount: null
        };

        this.sendMessage = this.sendMessage.bind(this);
        this.changeTitle = this.changeTitle.bind(this);
    }

    componentDidUpdate() {
        this.scrollToBottom();
    }

    scrollToBottom() {
        this.el.scrollIntoView({ behavior: 'smooth' });
    }

    componentDidMount() {
        const chatId = this.props.match.params.id;
        const fetchReq1 = fetch(`/api/chats/?chatId=${chatId}`)
            .then(res => res.json());

        const allData = Promise.all([fetchReq1]);
        allData.then((res) => {
            res = res[0];

            // define the Me constant
            let me = res.me,
                  users = res.users,
                  messages = res.chat.messages;

            for (let i=0; i< messages.length; i++) {
                let message = messages[i];
                message.user = users[message.userId];
            }

            this.setState({
                me: res.me,
                messages: messages,
                message: null,
                users: res.users,
                userCount: res.users.length-1,
            });
        });
    }

    sendMessage(event) {
        console.log(socket);

        /*
        const chatBox = document.getElementById('chatbox');
        let toSend = {
            message: chatBox.value,
            files: filesToSend.map(f => {
                return f.file;
            }),
        }
        */

        /* send the new message */
        //socket.emit('do message', activeChat.id, toSend);


    }

    changeTitle(event) {
        alert("IN HERE ... 2");
        scrollToBottom();
    }

    render() {
        return (
            <>
                <div>
                    <div className="chat-header d-flex" style={{"flex": "wrap", "width": "100%", "padding": "20px", "paddingTop": "5px", "paddingBottom": "10px"}}>
                        <h6 className="chat-title" style={{"flex":"1 1 auto", "width": "1%"}}>Mini Chat</h6>
                        <div className="btn-group">
                            <button type="button" className="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">O</button>
                            <ul className="dropdown-menu dropdown-menu-end">
                                <li><button className="dropdown-item" type="button" onClick={this.changeTitle}>Change Chat Title</button></li>
                            </ul>
                        </div>
                    </div>
                    <div className="col-inside-lg decor-default" style={{"overflow": "scroll"}} id="chat-window">
                        <div className="chat-body">
                            <div id="chat-messages" ref={el => { this.el = el; }}>
                            {this.state.messages.map(message => (
                                <div className={`answer ${this.state.me == message.userId ? "right" : "left"}`} key={message.id}>
                                    <div className="avatar">
                                        <img src={message.user.profile_image} alt={message.user.full_name} />
                                        <div className="status off"></div>
                                    </div>
                                    <div className="name">{message.user.first_name}</div>
                                    <div className="text">{message.message}</div>
                                    <div className="time">5 min ago</div>
                                </div>
                            ))}
                            </div>
                        </div>
                    </div>
                    <div className="input-group answer-add">
                        <input placeholder="Write a message" id="chatbox" name="chatbox" className="form-control me-2" autoComplete="off" ref={inputRef} />
                        <button className="px-2 me-1"><i className="bi bi-paperclip"></i></button>
                        <button className="px-2" onClick={this.sendMessage}><i className="bi bi-send"></i></button>
                    </div>
                </div>
            </>
        )
    }
}

export default withRouter(ChatWindow);
