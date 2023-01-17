let socket = undefined;
let server = undefined;
let user = undefined;

class ChatServer {
    constructor() {
        ChatServer._connect().then(res => {
            this.socket = res.socket.server;
            this.user = res.socket.user;

            this._initSocketServer(this.socket.CHAT_SERVER, this.user);
        });
    }

    _initSocketServer(chatServerUrl, user) {
        this.socket = io(chatServerUrl, {transports : ['websocket'], tester: 'chuck'});
        const socket = this.socket;

        socket.on('connect', function() {
            socket.emit('join', user.id, user.full_name);
        });
    }

    addSocketCallback(on, fn) {
        let socket = this.socket;
        socket.on(on, fn);
    }

    static async _connect() {
        const resp = await fetch('/api/accounts/socket');
        const data = await resp.json();

        return data;
    }
}

//const chatServer = new ChatServer();

const updateAlertCount = (dom, count) => {
    let divAlert = document.getElementById(dom);

    if (count)
        divAlert.innerHTML = count;
    else
        divAlert.innerHTML = '';
};

document.addEventListener("DOMContentLoaded", function() {

    /*
    chatServer.addSocketCallback('alerts', function(art) {
        let divAlert = document.getElementById('alerts');

        if (art.count)
            divAlert.innerHTML = art.count;
        else
            divAlert.innerHTML = '';
    });
    */

    fetch('/api/accounts/socket', {
        headers: {
            'X-CSRFToken':  Cookies.get('csrftoken')
        },
        method: 'GET',
    })
    .then(handleErrors)
    .then(response => response.json())
    .then(data => {
        server = data.socket.server;
        let user = data.socket.user;

        if (server.CHAT_SERVER) {
            socket = io(server.CHAT_SERVER, {transports : ['websocket'], tester: 'chuck'});
            socket.on('connect', function() {
                socket.emit('join', user.id, user.full_name);
            });

            socket.on('alerts', function(art) {
                updateAlertCount('alertcount', art.alertCount);
                updateAlertCount('messagecount', art.messageCount);
            });

            socket.on('buddy request', function(art) {
                alert(" BUDDY REQUEST SENT ");
                console.log(art);
            });

            socket.on('message alert', function(art) {
                updateAlertCount('messagecount', art.count);
                let divAlert = document.getElementById('messagealert');

                if (art.count)
                    divAlert.innerHTML = art.count;
                else
                    divAlert.innerHTML = '';
            });
        }
    }).catch(error => console.log(`Here is our error: ${error}`));
});

function handleErrors(response) {
    if (!response.ok) {
        throw Error(response.status);
    }
    return response;
}
