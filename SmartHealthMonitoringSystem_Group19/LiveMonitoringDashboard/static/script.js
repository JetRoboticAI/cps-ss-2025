console.log("✅ Script loaded");

const socket = io("http://localhost:5050", { transports: ["websocket"] });

const queueDiv = document.getElementById("queue-container");
const patientContainer = document.getElementById("patient-container");

window.patients = {};

socket.on("connect", () => {
  console.log("🔌 Connected to socket.io server");
});

socket.on("mqtt_data", (data) => {
  window.patients[data.patientID] = data;

  renderQueue();
  renderPatients();
});

function renderQueue() {
  queueDiv.innerHTML = "";

  const sortedPatients = Object.values(window.patients).sort(
    (a, b) => a.queuePosition - b.queuePosition
  );

  sortedPatients.forEach((patient) => {
    const healthColors = {
      Excellent: "bg-green-100 text-green-800",
      Average: "bg-yellow-100 text-yellow-800",
      Poor: "bg-orange-100 text-orange-800",
      Critical: "bg-red-100 text-red-800",
    };

    const badgeColor = healthColors[patient.healthStatus] || "bg-gray-200 text-gray-700";

    const queueItem = document.createElement("div");
    queueItem.className = `flex justify-between items-center p-3 rounded-lg shadow-md border ${badgeColor} mb-2`;

    queueItem.innerHTML = `
      <span class="font-semibold">Patient #${patient.patientID}</span>
      <span class="text-sm font-medium px-2 py-1 rounded bg-white bg-opacity-70">${patient.waitingTime} min</span>
    `;

    queueDiv.appendChild(queueItem);
  });
}


function renderPatients() {
  patientContainer.innerHTML = "";

  Object.values(window.patients).forEach((patient) => {
    const healthColors = {
      Excellent: "bg-green-50 border-green-500 text-green-900",
      Average: "bg-yellow-50 border-yellow-500 text-yellow-900",
      Poor: "bg-orange-50 border-orange-500 text-orange-900"
    };

    const isBeingCalled = patient.waitingTime === 0;
    const isEmergency = patient.emergencyState === true;

    const colorClass = isEmergency
      ? "bg-red-100 border-red-600 text-red-900 animate-pulse"
      : healthColors[patient.healthStatus] || "bg-gray-50 border-gray-400 text-gray-800";

    const card = document.createElement("div");
    card.className = `
      relative rounded-2xl shadow-lg p-5 border-l-8 flex flex-col gap-2
      transition-transform transform hover:scale-[1.01]
      ${colorClass}
      ${isBeingCalled && !isEmergency ? "animate-pulse-slow" : ""}
    `;
    card.style.minHeight = "200px";

    card.innerHTML = `
      <div class="flex justify-between items-start">
        <h3 class="text-xl font-bold tracking-wide">Patient #${patient.patientID}</h3>
        ${
          isEmergency
            ? `<span class="absolute top-3 right-3 bg-red-700 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md animate-bounce">EMERGENCY</span>`
            : isBeingCalled
              ? `<span class="absolute top-3 right-3 bg-blue-700 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md animate-pulse-slow">Being Called</span>`
              : ""
        }
      </div>
      <div class="mt-2 text-sm space-y-1 leading-relaxed">
        <p><span class="font-semibold">Status:</span> ${patient.healthStatus}</p>
        <div class="grid grid-rows-3 gap-2 text-sm">
          <div><p class="flex items-center gap-2"><span class="text-gray-500">❤️</span><span class="font-semibold">BPM:</span> ${patient.currentBPM}</p></div>
          <div><p class="flex items-center gap-2"><span class="text-gray-500">🫁</span><span class="font-semibold">SpO<sub>2</sub>:</span> ${patient.currentSpO2}</p></div>
          <div><p class="flex items-center gap-2"><span class="text-gray-500">🌡️</span><span class="font-semibold">Temp:</span> ${patient.currentTemp}°F</p></div>
        </div>
        <p><span class="font-semibold">Queue Position:</span> ${patient.queuePosition}</p>
        <p><span class="font-semibold">ETA:</span> ${patient.waitingTime} min</p>
      </div>
    `;

    patientContainer.appendChild(card);
  });
}

