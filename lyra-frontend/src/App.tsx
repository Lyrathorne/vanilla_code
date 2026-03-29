import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

type User = {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
};

type Chat = {
  id: number;
  title: string;
  is_group: boolean;
  member_ids: number[];
};

type Message = {
  id: number;
  chat_id: number;
  sender_id: number;
  text: string;
  created_at: string;
  is_read?: boolean;
};

type LoginResponse = {
  access_token: string;
  token_type: string;
};

const API_BASE = window.location.origin;

function decodeJwt(token: string): { sub?: string } | null {
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function getWsUrl(chatId: number, token: string) {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws/${chatId}?token=${encodeURIComponent(token)}`;
}

async function api<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(options.headers || {});

  if (!(options.body instanceof FormData) && !headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const data = await response.json();
      message = data.detail || JSON.stringify(data);
    } catch {
      message = await response.text();
    }
    throw new Error(message || `HTTP ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function hashStringToHue(text: string) {
  let hash = 0;
  for (let i = 0; i < text.length; i += 1) {
    hash = text.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash % 360);
}

function App() {
  const [token, setToken] = useState<string>(() => localStorage.getItem("lyra_token") || "");
  const [usernameFromToken, setUsernameFromToken] = useState<string>("");
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const [users, setUsers] = useState<User[]>([]);
  const [activeUsers, setActiveUsers] = useState<User[]>([]);
  const [searchUsersResult, setSearchUsersResult] = useState<User[]>([]);

  const [chats, setChats] = useState<Chat[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedChatId, setSelectedChatId] = useState<number | null>(null);
  const [selectedMessageId, setSelectedMessageId] = useState<string>("");
  const [selectedUserId, setSelectedUserId] = useState<string>("");

  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  const [regUsername, setRegUsername] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");

  const [profileUsername, setProfileUsername] = useState("");
  const [profileEmail, setProfileEmail] = useState("");
  const [profilePassword, setProfilePassword] = useState("");

  const [newChatTitle, setNewChatTitle] = useState("");
  const [newChatMembers, setNewChatMembers] = useState<number[]>([]);
  const [newChatIsGroup, setNewChatIsGroup] = useState(true);

  const [memberToAdd, setMemberToAdd] = useState("");
  const [memberToRemove, setMemberToRemove] = useState("");
  const [userSearch, setUserSearch] = useState("");

  const [messageText, setMessageText] = useState("");
  const [openedMessage, setOpenedMessage] = useState<Message | null>(null);
  const [openedUser, setOpenedUser] = useState<User | null>(null);

  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [socketStatus, setSocketStatus] = useState<"disconnected" | "connecting" | "connected">("disconnected");

  const socketRef = useRef<WebSocket | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const messagesRequestIdRef = useRef(0);
  const activeChatIdRef = useRef<number | null>(null);

  const selectedChat = useMemo(
    () => chats.find((chat) => chat.id === selectedChatId) || null,
    [chats, selectedChatId]
  );

  const usersMap = useMemo(() => {
    const map = new Map<number, User>();
    users.forEach((user) => map.set(user.id, user));
    return map;
  }, [users]);

  useEffect(() => {
    const payload = token ? decodeJwt(token) : null;
    setUsernameFromToken(payload?.sub || "");
  }, [token]);

  useEffect(() => {
    if (messages.length > 0) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  useEffect(() => {
    activeChatIdRef.current = selectedChatId;
  }, [selectedChatId]);

  useEffect(() => {
    if (!token) {
      disconnectSocket();
      setCurrentUser(null);
      setUsers([]);
      setActiveUsers([]);
      setSearchUsersResult([]);
      setChats([]);
      setMessages([]);
      setSelectedChatId(null);
      setOpenedMessage(null);
      setOpenedUser(null);
      return;
    }

    void loadInitialData(token);
  }, [token]);

  useEffect(() => {
    if (!token || !selectedChatId) {
      disconnectSocket();
      return;
    }

    void loadMessages(selectedChatId, token);
    connectSocket(selectedChatId, token);

    return () => {
      disconnectSocket();
    };
  }, [selectedChatId, token]);

  async function loadInitialData(currentToken: string) {
    try {
      setError("");
      setInfo("");

      const payload = decodeJwt(currentToken);
      const username = payload?.sub || "";

      const [allUsers, onlyActive, allChats] = await Promise.all([
        api<User[]>("/users", {}, currentToken),
        api<User[]>("/users/active", {}, currentToken),
        api<Chat[]>("/chats", {}, currentToken),
      ]);

      setUsers(allUsers);
      setActiveUsers(onlyActive);
      setChats(allChats);

      const me = allUsers.find((user) => user.username === username) || null;
      setCurrentUser(me);

      if (me) {
        setProfileUsername(me.username);
        setProfileEmail(me.email);
      }

      setSelectedChatId((prev) => {
        if (prev && allChats.some((chat) => chat.id === prev)) return prev;
        return allChats.length > 0 ? allChats[0].id : null;
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки");
    }
  }

  async function loadMessages(chatId: number, currentToken: string) {
    const requestId = ++messagesRequestIdRef.current;

    try {
      setError("");
      const data = await api<Message[]>(`/chats/${chatId}/messages`, {}, currentToken);

      if (requestId !== messagesRequestIdRef.current) return;
      if (activeChatIdRef.current !== chatId) return;

      setMessages(data);
    } catch (err) {
      if (requestId !== messagesRequestIdRef.current) return;
      setError(err instanceof Error ? err.message : "Ошибка загрузки сообщений");
    }
  }

  function disconnectSocket() {
    if (socketRef.current) {
      socketRef.current.onopen = null;
      socketRef.current.onclose = null;
      socketRef.current.onerror = null;
      socketRef.current.onmessage = null;
      socketRef.current.close();
      socketRef.current = null;
    }
    setSocketStatus("disconnected");
  }

  function connectSocket(chatId: number, currentToken: string) {
  disconnectSocket();

  if (!currentToken || !chatId) {
    setSocketStatus("disconnected");
    return;
  }

  const wsUrl = getWsUrl(chatId, currentToken);
  console.log("Connecting WS:", wsUrl);

  try {
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;
    setSocketStatus("connecting");

    ws.onopen = () => {
      console.log("WS connected");
      setSocketStatus("connected");
    };

    ws.onclose = (event) => {
      console.log("WS closed:", event.code, event.reason);
      setSocketStatus("disconnected");
    };

    ws.onerror = (event) => {
      console.log("WS error:", event);
      setSocketStatus("disconnected");
    };

    ws.onmessage = (event) => {
      try {
        const incoming = JSON.parse(event.data);

        if (!incoming || typeof incoming !== "object") return;

        if ("Error" in incoming) {
          setError(String(incoming.Error));
          return;
        }

        if (!("id" in incoming)) return;

        const incomingMessage = incoming as Message;

        if (incomingMessage.chat_id !== activeChatIdRef.current) {
          return;
        }

        setMessages((prev) => {
          const exists = prev.some((msg) => msg.id === incomingMessage.id);
          if (exists) return prev;
          return [...prev, incomingMessage];
        });
      } catch (error) {
        console.log("WS parse error:", error);
      }
    };
  } catch (error) {
    console.log("WS create error:", error);
    setSocketStatus("disconnected");
  }
}

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();

    try {
      setError("");
      setInfo("");

      const body = new URLSearchParams();
      body.append("username", loginUsername);
      body.append("password", loginPassword);

      const response = await api<LoginResponse>("/auth/login", {
        method: "POST",
        body,
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      localStorage.setItem("lyra_token", response.access_token);
      setToken(response.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка логина");
    }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();

    try {
      setError("");
      setInfo("");

      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          username: regUsername,
          email: regEmail,
          password: regPassword,
          is_active: true,
        }),
      });

      setLoginUsername(regUsername);
      setLoginPassword(regPassword);
      setRegUsername("");
      setRegEmail("");
      setRegPassword("");
      setInfo("Аккаунт создан. Теперь войди.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка регистрации");
    }
  }

  async function handleCreateChat() {
    try {
      setError("");
      setInfo("");

      const created = await api<Chat>(
        "/chats",
        {
          method: "POST",
          body: JSON.stringify({
            title: newChatTitle || (newChatIsGroup ? "Новая группа" : "Личный чат"),
            is_group: newChatIsGroup,
            member_ids: newChatMembers,
          }),
        },
        token
      );

      setChats((prev) => [created, ...prev]);
      setSelectedChatId(created.id);
      setNewChatTitle("");
      setNewChatMembers([]);
      setNewChatIsGroup(true);
      setMessages([]);
      setInfo("Чат создан");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка создания чата");
    }
  }

  async function handleDeleteChat() {
    if (!selectedChatId) return;
    if (!window.confirm("Удалить чат?")) return;

    try {
      setError("");
      setInfo("");

      await api(`/chats/${selectedChatId}`, { method: "DELETE" }, token);
      setChats((prev) => prev.filter((chat) => chat.id !== selectedChatId));
      setMessages([]);
      setSelectedChatId(null);
      setInfo("Чат удалён");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка удаления чата");
    }
  }

  async function handleAddMember() {
    if (!selectedChatId || !memberToAdd.trim()) return;

    try {
      setError("");
      setInfo("");

      const updated = await api<Chat>(
        `/chats/${selectedChatId}/members/${memberToAdd.trim()}`,
        { method: "POST" },
        token
      );

      setChats((prev) => prev.map((chat) => (chat.id === updated.id ? updated : chat)));
      setMemberToAdd("");
      setInfo("Участник добавлен");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка добавления участника");
    }
  }

  async function handleRemoveMember() {
    if (!selectedChatId || !memberToRemove.trim()) return;

    try {
      setError("");
      setInfo("");

      const updated = await api<Chat>(
        `/chats/${selectedChatId}/members/${memberToRemove.trim()}`,
        { method: "DELETE" },
        token
      );

      setChats((prev) => prev.map((chat) => (chat.id === updated.id ? updated : chat)));
      setMemberToRemove("");
      setInfo("Участник удалён");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка удаления участника");
    }
  }

  async function handleSendMessage() {
    const text = messageText.trim();
    if (!text || !selectedChatId) return;

    try {
      setError("");
      setInfo("");

      if (socketRef.current && socketStatus === "connected") {
        socketRef.current.send(text);
        setMessageText("");
        return;
      }

      const created = await api<Message>(
        "/messages",
        {
          method: "POST",
          body: JSON.stringify({
            chat_id: selectedChatId,
            text,
          }),
        },
        token
      );

      setMessages((prev) => {
        const exists = prev.some((msg) => msg.id === created.id);
        if (exists) return prev;
        return [...prev, created];
      });

      setMessageText("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка отправки сообщения");
    }
  }

  async function handleDeleteMessage(messageId: number) {
    if (!window.confirm("Удалить сообщение?")) return;

    try {
      setError("");
      setInfo("");

      await api(`/messages/${messageId}`, { method: "DELETE" }, token);
      setMessages((prev) => prev.filter((msg) => msg.id !== messageId));
      if (openedMessage?.id === messageId) {
        setOpenedMessage(null);
      }
      setInfo("Сообщение удалено");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка удаления сообщения");
    }
  }

  async function handleMarkAsRead(messageId: number) {
    try {
      setError("");
      const updated = await api<Message>(`/messages/${messageId}/read`, { method: "PATCH" }, token);
      setMessages((prev) => prev.map((msg) => (msg.id === updated.id ? updated : msg)));
      if (openedMessage?.id === messageId) {
        setOpenedMessage(updated);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка отметки сообщения");
    }
  }

  async function handleOpenMessage() {
    if (!selectedMessageId.trim()) return;

    try {
      setError("");
      const msg = await api<Message>(`/messages/${selectedMessageId.trim()}`, {}, token);
      setOpenedMessage(msg);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка получения сообщения");
    }
  }

  async function handleOpenUser() {
    if (!selectedUserId.trim()) return;

    try {
      setError("");
      const user = await api<User>(`/users/${selectedUserId.trim()}`, {}, token);
      setOpenedUser(user);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка получения пользователя");
    }
  }

  async function handleSearchUsers() {
    try {
      setError("");
      const result = await api<User[]>(
        `/users/search?username=${encodeURIComponent(userSearch.trim())}`,
        {},
        token
      );
      setSearchUsersResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка поиска пользователей");
    }
  }

  async function handleRefreshUsers() {
    try {
      setError("");
      const [allUsers, onlyActive] = await Promise.all([
        api<User[]>("/users", {}, token),
        api<User[]>("/users/active", {}, token),
      ]);
      setUsers(allUsers);
      setActiveUsers(onlyActive);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка обновления пользователей");
    }
  }

  async function handleUpdateProfile() {
    if (!currentUser) return;

    try {
      setError("");
      setInfo("");

      const body: Record<string, string> = {
        username: profileUsername,
        email: profileEmail,
      };

      if (profilePassword.trim()) {
        body.password = profilePassword;
      }

      const updated = await api<User>(
        `/users/${currentUser.id}`,
        {
          method: "PUT",
          body: JSON.stringify(body),
        },
        token
      );

      setCurrentUser(updated);
      setProfilePassword("");
      setInfo("Профиль обновлён");
      await loadInitialData(token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка обновления профиля");
    }
  }

  async function handleDeleteProfile() {
    if (!currentUser) return;
    if (!window.confirm("Удалить профиль?")) return;

    try {
      await api(`/users/${currentUser.id}`, { method: "DELETE" }, token);
      handleLogout();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка удаления профиля");
    }
  }

  function handleLogout() {
    disconnectSocket();
    localStorage.removeItem("lyra_token");
    setToken("");
  }

  function toggleMember(userId: number) {
    setNewChatMembers((prev) =>
      prev.includes(userId) ? prev.filter((id) => id !== userId) : [...prev, userId]
    );
  }

  function getUsernameById(userId: number) {
    return usersMap.get(userId)?.username || `user #${userId}`;
  }

  function getMessageBubbleStyle(message: Message, mine: boolean) {
    if (mine) {
      return {
        background: "linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%)",
      };
    }

    const username = getUsernameById(message.sender_id);
    const hue = hashStringToHue(username);

    return {
      background: `linear-gradient(135deg, hsla(${hue}, 45%, 28%, 1) 0%, hsla(${(hue + 18) % 360}, 42%, 20%, 1) 100%)`,
    };
  }

  if (!token) {
    return (
      <div className="auth-page">
        <div className="auth-shell">
          <div className="brand-panel">
            <div className="brand-badge">LYRA</div>
            <h1>Lyra Messenger</h1>
            <p>
              Тёмный мессенджер в фиолетово-серой теме с чатами, пользователями,
              сообщениями и realtime через WebSocket.
            </p>
          </div>

          <div className="auth-box">
            <div className="auth-grid">
              <form onSubmit={handleLogin} className="panel">
                <h2>Вход</h2>
                <input
                  placeholder="Username"
                  value={loginUsername}
                  onChange={(e) => setLoginUsername(e.target.value)}
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                />
                <button type="submit">Войти</button>
              </form>

              <form onSubmit={handleRegister} className="panel">
                <h2>Регистрация</h2>
                <input
                  placeholder="Username"
                  value={regUsername}
                  onChange={(e) => setRegUsername(e.target.value)}
                />
                <input
                  placeholder="Email"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                />
                <button type="submit">Создать аккаунт</button>
              </form>
            </div>

            {info && <div className="info-box">{info}</div>}
            {error && <div className="error-box">{error}</div>}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app app-layout">
      <aside className="sidebar">
        <div className="panel glow-panel">
          <h2>Профиль</h2>
          <p className="profile-name">{currentUser?.username || usernameFromToken}</p>
          <p className="muted">{currentUser?.email}</p>
          <p className="muted">WebSocket: {socketStatus}</p>
          <button onClick={handleLogout}>Выйти</button>
        </div>

        <div className="panel">
          <h2>Редактировать профиль</h2>
          <input
            placeholder="Username"
            value={profileUsername}
            onChange={(e) => setProfileUsername(e.target.value)}
          />
          <input
            placeholder="Email"
            value={profileEmail}
            onChange={(e) => setProfileEmail(e.target.value)}
          />
          <input
            type="password"
            placeholder="Новый пароль"
            value={profilePassword}
            onChange={(e) => setProfilePassword(e.target.value)}
          />
          <div className="row">
            <button onClick={handleUpdateProfile}>Сохранить</button>
            <button className="danger" onClick={handleDeleteProfile}>Удалить</button>
          </div>
        </div>

        <div className="panel">
          <h2>Создать чат</h2>
          <input
            placeholder="Название чата"
            value={newChatTitle}
            onChange={(e) => setNewChatTitle(e.target.value)}
          />

          <div className="row">
            <button
              type="button"
              className={newChatIsGroup ? "active-btn" : ""}
              onClick={() => setNewChatIsGroup(true)}
            >
              Группа
            </button>
            <button
              type="button"
              className={!newChatIsGroup ? "active-btn" : ""}
              onClick={() => setNewChatIsGroup(false)}
            >
              Личный
            </button>
          </div>

          <div className="users-list small-list">
            {users
              .filter((u) => u.id !== currentUser?.id)
              .map((user) => (
                <label key={user.id} className="user-row selectable-row">
                  <input
                    type="checkbox"
                    checked={newChatMembers.includes(user.id)}
                    onChange={() => toggleMember(user.id)}
                  />
                  <span>{user.username}</span>
                  <span className="muted tiny">id: {user.id}</span>
                </label>
              ))}
          </div>

          <button onClick={handleCreateChat}>Создать чат</button>
        </div>

        <div className="panel">
          <h2>Чаты</h2>
          <div className="chat-list">
            {chats.map((chat) => (
              <button
                key={chat.id}
                className={`chat-item ${selectedChatId === chat.id ? "chat-item-active" : ""}`}
                onClick={() => setSelectedChatId(chat.id)}
              >
                <strong>{chat.title}</strong>
                <span>
                  {chat.is_group ? "Группа" : "Личный"} · участников: {chat.member_ids.length}
                </span>
                <span className="tiny">id: {chat.id}</span>
              </button>
            ))}
          </div>
        </div>
      </aside>

      <main className="chat-area">
        <div className="chat-header">
          <div>
            <h2>{selectedChat ? selectedChat.title : "Выбери чат"}</h2>
            <p>{selectedChat ? `Chat ID: ${selectedChat.id}` : "Нет выбранного чата"}</p>
            {selectedChat && (
              <p className="muted">
                Участники: {selectedChat.member_ids.map((id) => getUsernameById(id)).join(", ")}
              </p>
            )}
          </div>
          <div className="chat-header-actions">
            <button className="danger" onClick={handleDeleteChat} disabled={!selectedChat}>
              Удалить чат
            </button>
          </div>
        </div>

        <div className="chat-toolbar">
          <input
            placeholder="ID пользователя для добавления"
            value={memberToAdd}
            onChange={(e) => setMemberToAdd(e.target.value)}
            disabled={!selectedChat}
          />
          <button onClick={handleAddMember} disabled={!selectedChat}>Добавить</button>

          <input
            placeholder="ID пользователя для удаления"
            value={memberToRemove}
            onChange={(e) => setMemberToRemove(e.target.value)}
            disabled={!selectedChat}
          />
          <button className="secondary" onClick={handleRemoveMember} disabled={!selectedChat}>
            Удалить участника
          </button>
        </div>

        <div className="messages">
          {!selectedChat && <div className="empty">Слева выбери чат</div>}

          {selectedChat &&
            messages.map((message) => {
              const mine = message.sender_id === currentUser?.id;
              const senderName = getUsernameById(message.sender_id);

              return (
                <div key={message.id} className={`message-row ${mine ? "mine" : "other"}`}>
                  <div
                    className={`message-bubble ${mine ? "mine-bubble" : "other-bubble"}`}
                    style={getMessageBubbleStyle(message, mine)}
                  >
                    <div className="message-meta">
                      <span className="sender-name">{senderName}</span>
                      <span className="muted tiny">#{message.id}</span>
                    </div>

                    <div className="message-text">{message.text}</div>

                    <div className="message-time-row">
                      <span className="message-time">{formatDate(message.created_at)}</span>
                      <span className={`read-badge ${message.is_read ? "read" : "unread"}`}>
                        {message.is_read ? "read" : "unread"}
                      </span>
                    </div>

                    <div className="message-actions">
                      <button
                        className="secondary"
                        onClick={() => {
                          setSelectedMessageId(String(message.id));
                          void handleOpenMessage();
                        }}
                      >
                        Открыть
                      </button>
                      <button
                        className="secondary"
                        onClick={() => handleMarkAsRead(message.id)}
                      >
                        Read
                      </button>
                      {mine && (
                        <button
                          className="danger"
                          onClick={() => handleDeleteMessage(message.id)}
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}

          <div ref={bottomRef} />
        </div>

        {selectedChat && (
          <div className="send-box">
            <input
              placeholder="Напиши сообщение..."
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  void handleSendMessage();
                }
              }}
            />
            <button onClick={() => void handleSendMessage()}>Отправить</button>
          </div>
        )}

        {info && <div className="info-box chat-error">{info}</div>}
        {error && <div className="error-box chat-error">{error}</div>}
      </main>

      <aside className="rightbar">
        <div className="panel">
          <h2>Пользователи</h2>
          <div className="row">
            <input
              placeholder="Поиск по username"
              value={userSearch}
              onChange={(e) => setUserSearch(e.target.value)}
            />
            <button onClick={handleSearchUsers}>Найти</button>
          </div>
          <div className="row">
            <input
              placeholder="Получить user по ID"
              value={selectedUserId}
              onChange={(e) => setSelectedUserId(e.target.value)}
            />
            <button onClick={handleOpenUser}>Открыть</button>
          </div>
          <button className="secondary full-width" onClick={handleRefreshUsers}>
            Обновить списки
          </button>

          {openedUser && (
            <div className="inspect-card">
              <div><strong>{openedUser.username}</strong></div>
              <div className="muted">{openedUser.email}</div>
              <div className="tiny">id: {openedUser.id}</div>
              <div className="tiny">{openedUser.is_active ? "active" : "inactive"}</div>
            </div>
          )}

          <h3>Результаты поиска</h3>
          <div className="users-list small-list">
            {searchUsersResult.map((user) => (
              <div key={user.id} className="user-row">
                <span>{user.username}</span>
                <span className="muted tiny">id: {user.id}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2>Активные пользователи</h2>
          <div className="users-list small-list">
            {activeUsers.map((user) => (
              <div key={user.id} className="user-row">
                <span>{user.username}</span>
                <span className="muted tiny">id: {user.id}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <h2>Одно сообщение</h2>
          <div className="row">
            <input
              placeholder="Message ID"
              value={selectedMessageId}
              onChange={(e) => setSelectedMessageId(e.target.value)}
            />
            <button onClick={handleOpenMessage}>Открыть</button>
          </div>

          {openedMessage && (
            <div className="inspect-card">
              <div><strong>{getUsernameById(openedMessage.sender_id)}</strong></div>
              <div>{openedMessage.text}</div>
              <div className="tiny">id: {openedMessage.id}</div>
              <div className="tiny">chat: {openedMessage.chat_id}</div>
              <div className="tiny">{formatDate(openedMessage.created_at)}</div>
              <div className="tiny">{openedMessage.is_read ? "read" : "unread"}</div>
            </div>
          )}
        </div>

        <div className="panel">
          <h2>Все пользователи</h2>
          <div className="users-list small-list">
            {users.map((user) => (
              <div key={user.id} className="user-row">
                <span>{user.username}</span>
                <span className="muted tiny">{user.email}</span>
              </div>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}

export default App;