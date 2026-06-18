import { createRouter, createWebHistory } from 'vue-router'
import Overview from '../views/Overview.vue'
import RouteList from '../views/RouteList.vue'
import RouteDetail from '../views/RouteDetail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'overview', component: Overview },
    { path: '/routes', name: 'routes', component: RouteList },
    { path: '/routes/:id', name: 'route-detail', component: RouteDetail, props: true },
  ],
})

export default router
