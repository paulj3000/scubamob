"use strict";
let btnSend = null;
let boxChat = null;
let chatArea = null;
let fd = new FormData();
let filesToSend = [];

let templ;
let me = null;
let users = null;

function resetChatUi() {
    boxChat.value = '';
    btnSend.disabled = true;
}

function drop(e) {

    e.preventDefault();

    const items = e.dataTransfer.items;
    const files = e.dataTransfer.files;

    let formData = new FormData();
    for (let i=0; i<items.length; i++) {
        let item = items[i];
        if (item.kind === 'file')
            formData.append("file", item.getAsFile());
    }

    const headers = {
        'X-CSRFToken':  Cookies.get('csrftoken'),
    };

    fetch('/api/chats/upload', {
        headers: headers,
        method: 'POST',
        body: formData,
    })
    .then(handleErrors)
    .then(response => response.json())
    .then(data => {
        filesToSend = data.files;

        //sendMessage(chatId, boxChat.value);
        resetChatUi();
    });
}

const imageTypes = [
    'image/jpeg',
];

const generateChatString = function(msg) {

    let aMessage = templ.content.cloneNode(true);
    let answer = aMessage.querySelector('.answer');

    if (msg.userId == me)
        answer.classList.add('right')
    else
        answer.classList.add('left')

    const user = users[msg.userId];
    answer.querySelector('.name').textContent = user.full_name;
    answer.querySelector('.avatar > img').src = user.profile_image;

    if (msg.message)
        answer.querySelector('.text').textContent = msg.message;
    else
        answer.querySelector('.text').remove();

    return aMessage;

    let chatString = `<div><div>${msg.message}</div>`;

    msg.messageAttachments = msg.messageAttachments || [];

    msg.messageAttachments.forEach(mp => {
        if (mp.type == 'preview') {
            let preview = '';
            if (mp.title)
                preview += `<div>${mp.title}</div>`;
            if (mp.image)
                preview += `<div><img src="${mp.image}" alt="preview" class="og_preview" /></div>`;

            chatString += `<div><a href="${mp.url}" target="_blank">${preview}</a></div>`;
        } else if (imageTypes.includes(mp.contentType)) {
            chatString += `<div data-url="${mp.url}" onclick="alert('in here');" ><img src="${mp.url}" alt="preview" class="og_preview" /></div>`;
        }
    });

    chatString += '</div>';
    return chatString;
}

const sendMessage = function(chatId, msg) {
    let toSend = {
        message: msg,
        files: filesToSend.map(f => {
            return f.file;
        }),
    }

    socket.emit('do message', chatId, toSend);
}

document.addEventListener("DOMContentLoaded", () => {
    let chat = null;
    let chatId = null;
    templ = document.getElementById('tmpl_message');

    document.getElementById('openchat').addEventListener("click", () => {

          $('#qnimate').addClass('popup-box-on');

            $("#removeClass").click(function () {
          $('#qnimate').removeClass('popup-box-on');
            });


        socket.on('chat message', function(msg) {
            if (msg.message) {

                //boxChatWindow.innerHTML += generateChatString(msg);
                boxChatWindow.appendChild(generateChatString(msg));
                boxChatWindow.scrollTop = boxChatWindow.scrollHeight;
            }
        });

        // profile user id
        const uid = document.getElementById('uid').value;

        btnSend = document.getElementById('send');
        console.log(btnSend);
        boxChat = document.getElementById('chatbox');
        const boxChatWindow = document.getElementById('chatwindow');

        const headers = {
            'X-CSRFToken':  Cookies.get('csrftoken'),
            'Content-Type': 'application/json',
        };

        btnSend.addEventListener("click", () => {
            alert(" THIS WAS CALLED ... ");
            if (! chatId) {
                fetch('/api/accounts/chats/', {
                    headers: headers,
                    method: 'POST',
                    body: JSON.stringify({uid: uid}),
                })
                .then(handleErrors)
                .then(response => response.json())
                .then(data => {
                    users = data.chat.users;
                    chat = data.chat;
                    chatId = data.chat.id;
                    me = data.chat.me;

                    sendMessage(chatId, boxChat.value);
                    resetChatUi();
                });
            } else {
                sendMessage(chatId, boxChat.value);
                resetChatUi();
            }
        });

        boxChat.addEventListener("input", () => {
            if (boxChat.value.length)
                btnSend.disabled = false;
            else
                btnSend.disabled = true;
        });

        alert("STARTING HERE ... ");
        fetch(`/api/accounts/chats?uid=${uid}`, {
            headers: headers, method: 'GET',
        })
        .then(handleErrors)
        .then(response => response.json())
        .then(data => {
            document.getElementById('chatblock').classList.remove("d-none");
            chat = data.chat;
            chatId = (data.chat) ? data.chat.id : null;
            users = (data.chat && data.chat.users) ? data.chat.users : null;
            me = (data.chat && data.chat.me) ? data.chat.me : null;
            boxChatWindow.innerHTML = "";

            let chatString = '';
            const messages = (data.chat && data.chat.messages) || [];
            const userList = data.chat.users;
            messages.slice().reverse().forEach(f => {
                f.user = userList[f.userId];
                boxChatWindow.appendChild(generateChatString(f));
            });

            //boxChatWindow.innerHTML = chatString;
            boxChatWindow.scrollTop = boxChatWindow.scrollHeight;

            chatArea = document.getElementById('chatarea');

            chatArea.addEventListener('dragenter', e => {
                e.preventDefault();
                chatArea.classList.add('drag-over');
            });

            chatArea.addEventListener('dragover', e => {
                e.preventDefault();
                chatArea.classList.add('drag-over');
            });

            chatArea.addEventListener('dragleave', e => {
                e.preventDefault();
                chatArea.classList.remove('drag-over');
            });

            chatArea.addEventListener('drop', drop);
        });
    });
});

/* https://stackoverflow.com/questions/17040709/can-i-create-a-div-with-a-curved-bottom */
