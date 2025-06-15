<template>
    <div class="violation-list">
  
      
      <div class="pagination sticky">
      <div class="pagination">
        <button @click="goToPage(1)" :disabled="page === 1">≪ first</button>
        <button @click="goToPage(page - 1)" :disabled="page === 1">&lt; prev</button>
  
        <button
          v-for="p in pageWindow"
          :key="p"
          :class="{ active: page === p }"
          @click="goToPage(p)"
        >
          {{ p }}
        </button>
  
        <button @click="goToPage(page + 1)" :disabled="page === totalPages">next &gt;</button>
        <button @click="goToPage(totalPages)" :disabled="page === totalPages">last ≫</button>
  
        <input
          type="number"
          v-model.number="inputPage"
          min="1"
          :max="totalPages"
          @keydown.enter="goToPage(inputPage)"
          class="page-input"
        />
      </div>
     </div>

            <ViolationCard
        v-for="record in paginatedRecords"
        :key="record.id"
        :record="record"
      />

    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import axios from 'axios'
  import ViolationCard from './ViolationCard.vue'
  
  // 
  //const mockRecords = Array.from({ length: 60 }, (_, i) => ({
  //  id: i + 1,
  //  image: `https://via.placeholder.com/240x320.png?text=Car+${i + 1}`,
  // type: 'Running Red',
  //  timestamp: '2025-06-03 12:31:54',
   // plate: `ON2SPD${i + 1}`,
   // location: i % 3
  //}))
  


  const page = ref(1)
  const perPage = ref(6)
  const inputPage = ref('')

  const total = ref(0)
  const records = ref([])

  const totalPages = computed(() => Math.ceil(total.value / perPage.value))
  const paginatedRecords = computed(() => records.value)
  
  //const total = computed(() => mockRecords.length)
  //const totalPages = computed(() => Math.ceil(total.value / perPage.value))
  
  //const paginatedRecords = computed(() => {
  //  const start = (page.value - 1) * perPage.value
  //  return mockRecords.slice(start, start + perPage.value)
  //})
  
  const pageWindow = computed(() => {
    const windowSize = 5
    let start = Math.max(1, page.value - 2)
    let end = start + windowSize - 1
  
    if (end > totalPages.value) {
      end = totalPages.value
      start = Math.max(1, end - windowSize + 1)
    }
  
    return Array.from({ length: end - start + 1 }, (_, i) => start + i)
  })

  async function fetchPage(p = page.value) {
  try {
    const res = await axios.get(`http://localhost:5000/api/violations?page=1&limit=6`)
    records.value = res.data.data
    total.value = res.data.total
  } catch (err) {
    console.error('err:', err)
    console.error('err:', p)
  }
}
  
  function goToPage(p) {
    const num = Number(p)
    if (Number.isInteger(num) && num >= 1 && num <= totalPages.value) {
      page.value = num
      fetchPage(num) // new
      inputPage.value = ''
    }
  }

  onMounted(() => {
  fetchPage()
  })

  </script>
  
  <style scoped>
.sticky {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: white;
  padding: 10px 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.violation-list {
  padding: 10px;
}

.pagination {
  margin-bottom: 20px; 
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.pagination button {
  padding: 4px 8px;
  border: 1px solid #aaa;
  background: white;
  cursor: pointer;
}

.pagination button.active {
  background-color: #007bff;
  color: white;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-input {
  width: 60px;
  padding: 4px;
  border: 1px solid #aaa;
  border-radius: 4px;
}
</style>

  
