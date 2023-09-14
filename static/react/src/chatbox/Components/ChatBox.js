import { Outlet, Link } from "react-router-dom";
import {Routes, Route, useNavigate} from 'react-router-dom';

import React from 'react';


class ChatBox extends React.Component {
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
<section style={{backgroundColor: "#eee"}} >
  <div className="container py-5">

    <div className="row d-flex justify-content-center">
      <div className="col-md-10 col-lg-8 col-xl-6">

        <div className="card" id="chat2">
          <div className="card-header d-flex justify-content-between align-items-center p-3">
            <h5 className="mb-0">Chat</h5>
            <button type="button" className="btn btn-primary btn-sm" data-mdb-ripple-color="dark">Let's Chat
              App</button>
          </div>
          <div className="card-body" data-mdb-perfect-scrollbar="true" style={{position: "relative", height: "400px", overflow: "auto"}} >

            <div className="d-flex flex-row justify-content-start">
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp"
                alt="avatar 1" style={{width: "45px", height: "100%"}} />
              <div>
                <p className="small p-2 ms-3 mb-1 rounded-3" style={{backgroundColor: "#f5f6f7"}}>Hi</p>
                <p className="small p-2 ms-3 mb-1 rounded-3" style={{backgroundColor: "#f5f6f7"}}>How are you ...???
                </p>
                <p className="small p-2 ms-3 mb-1 rounded-3" style={{backgroundColor: "#f5f6f7"}}>What are you doing
                  tomorrow? Can we come up a bar?</p>
                <p className="small ms-3 mb-3 rounded-3 text-muted">23:58</p>
              </div>
            </div>

            <div className="divider d-flex align-items-center mb-4">
              <p className="text-center mx-3 mb-0" style={{color: "#a2aab7"}}>Today</p>
            </div>

            <div className="d-flex flex-row justify-content-end mb-4 pt-1">
              <div>
                <p className="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">Hiii, I'm good.</p>
                <p className="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">How are you doing?</p>
                <p className="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">Long time no see! Tomorrow
                  office. will
                  be free on sunday.</p>
                <p className="small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end">00:06</p>
              </div>
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava4-bg.webp"
                alt="avatar 1" style={{width: "45px", height: "100%"}} />
            </div>

            <div className="d-flex flex-row justify-content-start mb-4">
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp"
                alt="avatar 1" style={{width: "45px", height: "100%"}} />
              <div>
                <p className="small p-2 ms-3 mb-1 rounded-3" style={{backgroundColor: "#f5f6f7"}}>Okay</p>
                <p className="small p-2 ms-3 mb-1 rounded-3" style={{backgroundColor: "#f5f6f7"}}>We will go on
                  Sunday?</p>
                <p className="small ms-3 mb-3 rounded-3 text-muted">00:07</p>
              </div>
            </div>

            <div className="d-flex flex-row justify-content-end mb-4">
              <div>
                <p className="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">That's awesome!</p>
                <p className="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">I will meet you Sandon Square
                  sharp at
                  10 AM</p>
                <p className="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">Is that okay?</p>
                <p className="small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end">00:09</p>
              </div>
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava4-bg.webp"
                alt="avatar 1" style={{width: "45px", height: "100%"}} />
            </div>

            <div className="d-flex flex-row justify-content-start mb-4">
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp"
                alt="avatar 1" style={{width: "45px", height: "100%"}} />
              <div>
                <p className="small p-2 ms-3 mb-1 rounded-3" style={{backgroundColor: "#f5f6f7"}}>Okay i will meet
                  you on
                  Sandon Square</p>
                <p className="small ms-3 mb-3 rounded-3 text-muted">00:11</p>
              </div>
            </div>

            <div className="d-flex flex-row justify-content-end mb-4">
              <div>
                <p className="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">Do you have pictures of Matley
                  Marriage?</p>
                <p className="small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end">00:11</p>
              </div>
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava4-bg.webp"
                alt="avatar 1" style={{width: "45px", height: "100%"}} />
            </div>

            <div className="d-flex flex-row justify-content-start mb-4">
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp"
                alt="avatar 1" style={{width: "45px", height: "100%"}} />
              <div>
                <p className="small p-2 ms-3 mb-1 rounded-3" style={{backgroundColor: "#f5f6f7" }}>Sorry I don't
                  have. i
                  changed my phone.</p>
                <p className="small ms-3 mb-3 rounded-3 text-muted">00:13</p>
              </div>
            </div>

            <div className="d-flex flex-row justify-content-end">
              <div>
                <p className="small p-2 me-3 mb-1 text-white rounded-3 bg-primary">Okay then see you on sunday!!
                </p>
                <p className="small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end">00:15</p>
              </div>
              <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava4-bg.webp"
                alt="avatar 1" style={{width: "45px", height: "100%"}} />
            </div>

          </div>
          <div className="card-footer text-muted d-flex justify-content-start align-items-center p-3">
            <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava3-bg.webp"
              alt="avatar 3" style={{width: "40px", height: "100%"}} />
            <input type="text" className="form-control form-control-lg" id="exampleFormControlInput1"
              placeholder="Type message" />
            <a className="ms-1 text-muted" href="#!"><i className="fas fa-paperclip"></i></a>
            <a className="ms-3 text-muted" href="#!"><i className="fas fa-smile"></i></a>
            <a className="ms-3" href="#!"><i className="fas fa-paper-plane"></i></a>
          </div>
        </div>

      </div>
    </div>

  </div>
</section>
        )
    }
}

export default ChatBox;
