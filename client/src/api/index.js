const BASE = '/api'

async function request(url, options = {}) {
  const res = await fetch(BASE + url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || '请求失败')
  }
  return res.json()
}

export const llmApi = {
  getProviders: () => request('/llm/providers'),
  createProvider: (data) => request('/llm/providers', { method: 'POST', body: JSON.stringify(data) }),
  updateProvider: (id, data) => request(`/llm/providers/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProvider: (id) => request(`/llm/providers/${id}`, { method: 'DELETE' }),
  testConnection: (data) => request('/llm/test', { method: 'POST', body: JSON.stringify(data) }),
  getBindings: () => request('/llm/bindings'),
  updateBindings: (data) => request('/llm/bindings', { method: 'PUT', body: JSON.stringify(data) }),
}

export const projectApi = {
  list: () => request('/projects/'),
  create: (data) => request('/projects/', { method: 'POST', body: JSON.stringify(data) }),
  get: (id) => request(`/projects/${id}`),
  update: (id, data) => request(`/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (id) => request(`/projects/${id}`, { method: 'DELETE' }),
}

export const outlineApi = {
  get: (pid) => request(`/projects/${pid}/outline/`),
  update: (pid, data) => request(`/projects/${pid}/outline/`, { method: 'PUT', body: JSON.stringify(data) }),
}

export const characterApi = {
  list: (pid) => request(`/projects/${pid}/characters/`),
  create: (pid, data) => request(`/projects/${pid}/characters/`, { method: 'POST', body: JSON.stringify(data) }),
  update: (pid, cid, data) => request(`/projects/${pid}/characters/${cid}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (pid, cid) => request(`/projects/${pid}/characters/${cid}`, { method: 'DELETE' }),
}

export const worldviewApi = {
  get: (pid) => request(`/projects/${pid}/worldview/`),
  update: (pid, data) => request(`/projects/${pid}/worldview/`, { method: 'PUT', body: JSON.stringify(data) }),
}

export const chapterApi = {
  list: (pid) => request(`/projects/${pid}/chapters/`),
  create: (pid, data) => request(`/projects/${pid}/chapters/`, { method: 'POST', body: JSON.stringify(data) }),
  update: (pid, cid, data) => request(`/projects/${pid}/chapters/${cid}`, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (pid, cid) => request(`/projects/${pid}/chapters/${cid}`, { method: 'DELETE' }),
}

export function createChatStream(projectId, data) {
  return fetch(BASE + `/chat/${projectId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}
