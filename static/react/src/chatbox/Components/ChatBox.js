import React from 'react';

/*
 * Persistent floating messaging widget (docs/chat_dynamo.md Phase 5, §20-21).
 * Mounted once, site-wide, for authenticated users only (templates/layout.html).
 *
 * UI states supported per §21: collapsed, conversation list, one active
 * conversation. Multiple open conversations / unread badges are explicitly
 * deferred ("Initial implementation can support one open active
 * conversation" / unread counts need Phase 7's infra, which doesn't exist
 * yet).
 */
class ChatBox extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            collapsed: true,
            loadedConversations: false,
            conversations: [],
            searchTerm: '',
            activeConversation: null,
            messages: [],
            messageBody: '',
            loadingMessages: false,
            sending: false,
            error: null,
        };
    }

    toggleCollapsed = () => {
        const collapsed = !this.state.collapsed;
        this.setState({ collapsed });

        if (!collapsed && !this.state.loadedConversations) {
            this.loadConversations();
        }
    };

    loadConversations = () => {
        fetch('/api/chat/conversations/')
            .then(res => res.json())
            .then(result => {
                this.setState({
                    conversations: result.conversations || [],
                    loadedConversations: true,
                });
            })
            .catch(() => {
                this.setState({ error: 'Could not load conversations.', loadedConversations: true });
            });
    };

    openConversation = (conversation) => {
        this.setState({
            activeConversation: conversation,
            messages: [],
            loadingMessages: true,
            error: null,
        });

        fetch(`/api/chat/conversations/${conversation.id}/messages/`)
            .then(res => res.json())
            .then(result => {
                this.setState({ messages: result.results || [], loadingMessages: false });
            })
            .catch(() => {
                this.setState({ error: 'Could not load messages.', loadingMessages: false });
            });
    };

    closeActiveConversation = () => {
        this.setState({ activeConversation: null, messages: [], messageBody: '' });
    };

    updateMessageBody = (event) => {
        this.setState({ messageBody: event.target.value });
    };

    updateSearchTerm = (event) => {
        this.setState({ searchTerm: event.target.value });
    };

    generateClientMessageId = () => {
        if (window.crypto && window.crypto.randomUUID) {
            return window.crypto.randomUUID();
        }
        return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    };

    sendMessage = (event) => {
        event.preventDefault();

        const body = this.state.messageBody.trim();
        const conversation = this.state.activeConversation;
        if (!body || !conversation || this.state.sending) {
            return;
        }

        this.setState({ sending: true, error: null });

        fetch(`/api/chat/conversations/${conversation.id}/messages/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': Cookies.get('csrftoken'),
            },
            body: JSON.stringify({
                body,
                client_message_id: this.generateClientMessageId(),
            }),
        })
            .then(res => res.json().then(data => ({ ok: res.ok, data })))
            .then(({ ok, data }) => {
                if (!ok) {
                    this.setState({ sending: false, error: data.error || 'Could not send message.' });
                    return;
                }
                this.setState(prevState => ({
                    messages: prevState.messages.concat([data.message]),
                    messageBody: '',
                    sending: false,
                }));
            })
            .catch(() => {
                this.setState({ sending: false, error: 'Could not send message.' });
            });
    };

    conversationLabel = (conversation) => {
        if (conversation.title) {
            return conversation.title;
        }
        return conversation.conversation_type === 'DIRECT' ? 'Direct message' : 'Untitled conversation';
    };

    filteredConversations = () => {
        const term = this.state.searchTerm.trim().toLowerCase();
        if (!term) {
            return this.state.conversations;
        }
        return this.state.conversations.filter(
            conversation => this.conversationLabel(conversation).toLowerCase().includes(term)
        );
    };

    renderCollapsed() {
        return (
            <button
                type="button"
                className="btn btn-primary rounded-pill shadow"
                style={styles.toggleButton}
                onClick={this.toggleCollapsed}
            >
                <i className="bi bi-chat-dots-fill me-1"></i> Messaging
            </button>
        );
    }

    renderConversationList() {
        const conversations = this.filteredConversations();

        return (
            <div className="card shadow" style={styles.panel}>
                <div className="card-header d-flex justify-content-between align-items-center">
                    <span className="fw-bold">Messaging</span>
                    <button type="button" className="btn-close" onClick={this.toggleCollapsed}></button>
                </div>
                <div className="p-2 border-bottom">
                    <input
                        type="text"
                        className="form-control form-control-sm"
                        placeholder="Search conversations"
                        value={this.state.searchTerm}
                        onChange={this.updateSearchTerm}
                    />
                </div>
                <div className="list-group list-group-flush" style={styles.list}>
                    {!this.state.loadedConversations && (
                        <div className="p-3 text-muted small">Loading...</div>
                    )}
                    {this.state.loadedConversations && conversations.length === 0 && (
                        <div className="p-3 text-muted small">No conversations yet.</div>
                    )}
                    {conversations.map(conversation => (
                        <button
                            type="button"
                            key={conversation.id}
                            className="list-group-item list-group-item-action"
                            onClick={() => this.openConversation(conversation)}
                        >
                            {this.conversationLabel(conversation)}
                        </button>
                    ))}
                </div>
                {this.state.error && (
                    <div className="p-2 text-danger small">{this.state.error}</div>
                )}
            </div>
        );
    }

    renderActiveConversation() {
        const { activeConversation, messages, loadingMessages } = this.state;

        return (
            <div className="card shadow" style={styles.panel}>
                <div className="card-header d-flex justify-content-between align-items-center">
                    <span>
                        <button
                            type="button"
                            className="btn btn-sm btn-link p-0 me-2"
                            onClick={this.closeActiveConversation}
                        >
                            <i className="bi bi-arrow-left"></i>
                        </button>
                        {this.conversationLabel(activeConversation)}
                    </span>
                    <button type="button" className="btn-close" onClick={this.toggleCollapsed}></button>
                </div>
                <div className="card-body" style={styles.messages}>
                    {loadingMessages && <div className="text-muted small">Loading...</div>}
                    {!loadingMessages && messages.length === 0 && (
                        <div className="text-muted small">No messages yet. Say hello.</div>
                    )}
                    {messages.map(message => (
                        <div key={message.message_id} className="mb-2">
                            <p className="small p-2 mb-0 rounded-3 bg-light">{message.body}</p>
                        </div>
                    ))}
                </div>
                {this.state.error && (
                    <div className="px-2 text-danger small">{this.state.error}</div>
                )}
                <form className="card-footer d-flex" onSubmit={this.sendMessage}>
                    <input
                        type="text"
                        className="form-control form-control-sm me-2"
                        placeholder="Write a message"
                        value={this.state.messageBody}
                        onChange={this.updateMessageBody}
                    />
                    <button
                        type="submit"
                        className="btn btn-primary btn-sm"
                        disabled={this.state.sending || !this.state.messageBody.trim()}
                    >
                        <i className="bi bi-send-fill"></i>
                    </button>
                </form>
            </div>
        );
    }

    render() {
        if (this.state.collapsed) {
            return this.renderCollapsed();
        }
        if (this.state.activeConversation) {
            return this.renderActiveConversation();
        }
        return this.renderConversationList();
    }
}

const styles = {
    toggleButton: {
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        zIndex: 1050,
    },
    panel: {
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        width: '320px',
        zIndex: 1050,
    },
    list: {
        maxHeight: '320px',
        overflowY: 'auto',
    },
    messages: {
        maxHeight: '320px',
        overflowY: 'auto',
    },
};

export default ChatBox;
