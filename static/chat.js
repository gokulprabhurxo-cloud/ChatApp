const socket = io();

const form = document.getElementById("chatForm");
const msg = document.getElementById("msg");
const messages = document.getElementById("messages");

function addMessage(m) {
  const line = document.createElement("div");
  line.textContent = `[${m.ts}] ${m.username}: ${m.text}`;
  messages.appendChild(line);
  messages.scrollTop = messages.scrollHeight;
}

socket.on("new_message", (m) => addMessage(m));

form.addEventListener("submit", (e) => {
  e.preventDefault();
  const text = msg.value.trim();
  if (!text) return;
  socket.emit("send_message", { text });
  msg.value = "";
});
