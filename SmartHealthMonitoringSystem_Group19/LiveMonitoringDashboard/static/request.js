console.log("🚀 Request page script loaded");

const socket = io("http://localhost:5050", { transports: ["websocket"] });

const btn = document.getElementById("requestBtn");
const statusMsg = document.getElementById("statusMsg");

btn.addEventListener("click", () => {
  socket.emit("send_mqtt", { request: true });
});

socket.on("token_issued", (data) => {
  statusMsg.textContent = `🪪 Your Token Number is: #${data.patientID}`;
  statusMsg.classList.remove("hidden");
});
