<!--cd traffic_light_web-->
<!--npm run serve-->
<template>
  <div>
    <div class="header">
      Smart Traffic Light System
    </div>

    <div class="app-container">
      <div class="sidebar">
        <div class="status">
          <p>
            <strong>Traffic Light Status:</strong>
            <span :style="{ color: statusColor }">{{ trafficStatus }}</span>
            <span class="dot" :style="{ backgroundColor: statusColor }"></span>
          </p>
          <p><strong>Last Update:</strong> {{ lastUpdate }}</p>
          <p><strong>Connectivity:</strong> <span class="connected">Connected</span></p>
        </div>

        <hr />

        <div class="control">
          <h3>Control</h3>
          <button
            v-for="cmd in commands"
            :key="cmd"
            @click="handleControl(cmd)"
          >
            {{ cmd }}
          </button>
        </div>
      </div>

      <div class="main-content">
            <ViolationList />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import ViolationList from './ViolationList.vue'

const trafficStatus = ref('Red')
const lastUpdate = ref('2025-06-05 00:00:00')
const commands = ['Red', 'Green', 'Yellow', 'Auto']

const statusColor = computed(() => {
  switch (trafficStatus.value) {
    case 'Red': return 'red'
    case 'Green': return 'green'
    case 'Yellow': return 'gold'
    case 'Auto': return 'gray'  
    default: return 'gray'
  }
})

function handleControl(cmd) {
  axios.post('http://localhost:5000/api/control', {
    command: cmd,
    intersection_id: "0"
  })
  .then(res => {
    console.log(" Control command sent:", res.data)
  })
  .catch(err => {
    console.error(" Control command failed:", err)
  })

}

function fetchLightStatus() {
  axios.get('http://localhost:5000/api/light_status/0')
    .then(res => {
      trafficStatus.value = res.data.status || 'Unknown'
      lastUpdate.value = new Date().toLocaleString()
    })
    .catch(err => {
      console.error('Failed to fetch light status:', err)
    })
}

onMounted(() => {
  fetchLightStatus()
  setInterval(fetchLightStatus, 2000)  
})

</script>


<style scoped>

button.active {
  background-color: #007bff;
  color: white;
}

.page-input {
  width: 60px;
  padding: 4px;
  border: 1px solid #aaa;
  border-radius: 4px;
}

.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 50px;
  background-color: #333;
  color: white;
  font-size: 20px;
  font-weight: bold;
  padding: 10px 20px;
  z-index: 1000;
  display: flex;
  align-items: center;
}


.app-container {
  display: flex;
  padding-top: 50px; 
  height: calc(100vh - 50px);
}

.sidebar {
  width: 250px;
  padding: 20px;
  border-right: 1px solid #ccc;
  background-color: #f9f9f9;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.status p {
  margin: 6px 0;
}

.dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  margin-left: 6px;
  border-radius: 50%;
  vertical-align: middle;
}

.connected {
  color: green;
  font-weight: bold;
}

.control {
  margin-top: 20px;
  display: flex;
  flex-direction: column; 
  gap: 10px;
}

.control button {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #888;
  background-color: white;
  cursor: pointer;
  transition: background-color 0.2s;
  width: 100%;
}

.control button:hover {
  background-color: #eee;
}

.main-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
</style>


