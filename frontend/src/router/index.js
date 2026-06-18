import { createRouter, createWebHistory } from 'vue-router'
import RouteList from '../views/RouteList.vue'
import RouteDetail from '../views/RouteDetail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'routes', component: RouteList },
    { path: '/routes/:id', name: 'route-detail', component: RouteDetail, props: true },
  ],
})

export default router
