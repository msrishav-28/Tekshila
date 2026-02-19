const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class ApiClient {
  private token: string | null = null

  constructor() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token')
    }
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const url = `${API_URL}${endpoint}`
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(url, {
      ...options,
      headers
    })

    if (response.status === 401) {
      const refreshed = await this.refreshToken()
      if (refreshed) {
        return this.request(endpoint, options)
      }
      throw new Error('Unauthorized')
    }

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Request failed')
    }

    return response.json()
  }

  private async refreshToken(): Promise<boolean> {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) return false

    try {
      const response = await fetch(`${API_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
        this.token = data.access_token
        return true
      }
    } catch (error) {
      console.error('Token refresh failed:', error)
    }
    return false
  }

  async getUser() {
    return this.request('/api/user/me')
  }

  async getProjects() {
    return this.request('/api/projects')
  }

  async createProject(name: string, description?: string) {
    const formData = new FormData()
    formData.append('name', name)
    if (description) formData.append('description', description)

    return this.request('/api/projects', {
      method: 'POST',
      body: formData
    })
  }

  async getGitHubRepos() {
    return this.request('/api/github/repos')
  }

  async uploadFiles(files: File[]) {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))

    return this.request('/api/upload', {
      method: 'POST',
      body: formData
    })
  }

  async generateDocumentation(files: Record<string, string>, docType: string = 'readme', stream: boolean = false) {
    return this.request('/api/documentation/generate', {
      method: 'POST',
      body: JSON.stringify({ files, doc_type: docType, stream })
    })
  }

  async streamDocumentation(
    files: Record<string, string>,
    docType: string = 'readme',
    onChunk: (chunk: { step?: string; content?: string; complete?: boolean }) => void
  ) {
    const response = await fetch(`${API_URL}/api/documentation/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`
      },
      body: JSON.stringify({ files, doc_type: docType, stream: true })
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Stream failed')
    }

    const reader = response.body?.getReader()
    if (!reader) throw new Error('No response body')

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))
            onChunk(data)
          } catch (e) {
            console.error('Failed to parse SSE data:', line)
          }
        }
      }
    }
  }

  async getDocumentationJobs(limit: number = 20) {
    return this.request(`/api/documentation/jobs?limit=${limit}`)
  }

  async getDocumentation(jobId: string) {
    return this.request(`/api/documentation/${jobId}`)
  }
}

export const api = new ApiClient()
