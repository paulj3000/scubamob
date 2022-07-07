"use strict";

let messageNames = {};
let activeChat = null;
let filesToSend = [];

let activeChatPages = {
};

let messagesLoading = false;


const sendMessage = function() {
    const chatBox = document.getElementById('chatbox');
    let toSend = {
        message: chatBox.value,
        files: filesToSend.map(f => {
            return f.file;
        }),
    }

    /* send the new message */
    socket.emit('do message', activeChat.id, toSend);
}

const scrollChatWindow = () => {
    const objDiv = document.getElementById('chat-window')
    objDiv.scrollTop = objDiv.scrollHeight;
}

const changeTitle = () => {
    let newTitle = prompt("Enter a new title for Chat", "Chat Title");

    if (newTitle) {
        socket.emit('change title', activeChat.id, newTitle);
    }
}

const getChat = (chatId) => {
    fetch('/api/chats?chatId=' + chatId)
    .then(handleErrors)
    .then(response => response.json())
    .then(data => {
        let messageList = document.getElementById('chat-messages');
        messageList.innerHTML = '';
        addMessages(data, true);
        let chatTitle = document.querySelector('.chat-title');
        chatTitle.innerHTML = messageNames[chatId];
        activeChat = data.chat;

        activeChatPages[chatId] = 0;
        messagesLoading = false;

        scrollChatWindow();
    });
}

const addMessages = (chatData, first) => {
    const chat = chatData.chat;
    const me = chatData.me;
    const users = chatData.users;
    const messages = chat.messages;

    let templ = document.getElementById('tmpl_message');
    let messageList = document.getElementById('chat-messages');

    messages.forEach(f => {
        let aMessage = templ.content.cloneNode(true);

        const user = users[f.userId];
        let answer = aMessage.querySelector('.answer');

        if (f.userId == me)
            answer.classList.add('right')
        else
            answer.classList.add('left')

        aMessage.querySelector('.name').textContent = user.full_name;
        aMessage.querySelector('.avatar > img').src = user.profile_image;
        aMessage.querySelector('.text').textContent = f.message;

        if (first)
            messageList.appendChild(aMessage);
        else
            messageList.prepend(aMessage);
    });
}

const getChatMessagesByPage = () => {
    const chatId = activeChat.id;
    console.log(`${chatId} -> ${activeChatPages[chatId]}`);

    const page = activeChatPages[chatId] + 1;
    fetch(`/api/chats/messages?chatId=${chatId}&page=${page}`)
    .then(handleErrors)
    .then(response => response.json())
    .then(data => {
        addMessages({chat: data, users: data.users, me: data.me});
        activeChatPages[chatId] = page;
        messagesLoading = false;
        //scrollChatWindow();
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const div = document.getElementById("chat-window");
    div.addEventListener('scroll', (event) => {
        let p = div.scrollTop / (div.scrollHeight - div.clientHeight) * 100;
        p = parseInt(p);
        if (p < 5 && ! messagesLoading) {
            getChatMessagesByPage();
            messagesLoading = true;
        }
    });

    let templ = document.getElementById('tmpl_chat');
    let chatList = document.getElementById('chats-list');
    let chatTitle = document.querySelector('.chat-title');

    fetch('/api/chats/all')
    .then(handleErrors)
    .then(response => response.json())
    .then(data => {
        const users = data.users;
        const me = data.me;
        data.chats.forEach(f => {
            let name = null;

            f.users = f.users.filter(g => {
                return g != me;
            });

            if (f.users.length == 1) {
                name = users[f.users[0]].full_name;
            } else {
                let lst = f.users.map(g => {
                    return users[g].first_name;
                });

                name = lst.sort().join(', ');
            }

            messageNames[f.id] = name;

            let aChat = templ.content.cloneNode(true);
            aChat.querySelector('.name').textContent = name;
            aChat.querySelector('.user').onclick = function() {
                getChat(f.id);
            }

            aChat.querySelector('.user').setAttribute('id', `chat${f.id}`);

            chatList.appendChild(aChat);
        });

        getChat(data.chats[0].id);
    });
});
