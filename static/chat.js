const socket = io({
  transports: ["websocket", "polling"]
});

const form = document.getElementById("chatForm");
const msg = document.getElementById("msg");
const messages = document.getElementById("messages");
const connStatus = document.getElementById("connStatus");

const CURRENT_USERNAME = window.CURRENT_USERNAME;

function escapeText(s) {
  // prevent HTML injection
  const div = document.createElement("div");
  div.innerText = s ?? "";
  return div.innerHTML;
}

function addMessage(m) {
  const isMe = (m.username === CURRENT_USERNAME);

  const row = document.createElement("div");
  row.className = `bubble-row ${isMe ? "me" : "other"}`;

  const bubble = document.createElement("div");
  bubble.className = `bubble ${isMe ? "me" : "other"}`;

  // message text
  const text = document.createElement("div");
  text.innerHTML = escapeText(m.text);

  // meta (name + timestamp)
  const meta = document.createElement("div");
  meta.className = "meta";

  const name = document.createElement("div");
  name.className = "name";
  name.textContent = isMe ? "You" : m.username;

  const ts = document.createElement("div");
  ts.textContent = m.ts || "";

  meta.appendChild(name);
  meta.appendChild(ts);

  bubble.appendChild(text);
  bubble.appendChild(meta);
  row.appendChild(bubble);
  messages.appendChild(row);

  // auto-scroll
  messages.scrollTop = messages.scrollHeight;
}

// connection status
socket.on("connect", () => {
  connStatus.textContent = "Online";
  connStatus.style.borderColor = "rgba(40,167,69,0.45)";
  connStatus.style.background = "rgba(40,167,69,0.18)";
});

socket.on("disconnect", () => {
  connStatus.textContent = "Offline";
  connStatus.style.borderColor = "rgba(220,53,69,0.45)";
  connStatus.style.background = "rgba(220,53,69,0.18)";
});

socket.on("new_message", (m) => addMessage(m));

// Send message
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = msg.value.trim();
  if (!text) return;
  socket.emit("send_message", { text });
  msg.value = "";
  msg.focus();
});

// Enter to send, Shift+Enter newline
msg.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    form.requestSubmit();
  }
});
