import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Search from '@/views/Search.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
      meta: {
        title: '儿童汽车学习卡片'
      }
    },
    {
      path: '/search',
      name: 'search',
      component: Search,
      meta: {
        title: '搜索汽车'
      }
    },
    {
      // 捕获所有未匹配的路由，重定向到首页
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// 路由守卫，用于设置页面标题
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 儿童汽车学习卡片`
  } else {
    document.title = '儿童汽车学习卡片'
  }
  next()
})

export default router