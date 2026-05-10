import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'projects',
    component: () => import('../views/ProjectList.vue'),
  },
  {
    path: '/project/:id',
    name: 'workspace',
    component: () => import('../views/Workspace.vue'),
    children: [
      { path: '', name: 'chat', component: () => import('../views/WorkspaceChat.vue') },
      { path: 'outline', name: 'outline', component: () => import('../views/Outline.vue') },
      { path: 'characters', name: 'characters', component: () => import('../views/Characters.vue') },
      { path: 'worldview', name: 'worldview', component: () => import('../views/Worldview.vue') },
      { path: 'chapters', name: 'chapters', component: () => import('../views/Chapters.vue') },
    ],
  },
  {
    path: '/settings/llm',
    name: 'llm-settings',
    component: () => import('../views/LLMSettings.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
