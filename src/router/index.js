import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Dividends from '../views/Dividends.vue'
import Yields from '../views/Yields.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/dividends', component: Dividends },
  { path: '/yields', component: Yields },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
