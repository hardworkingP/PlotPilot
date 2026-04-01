import axios from 'axios'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 180000,
})

request.interceptors.response.use(response => response.data)

// Types
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  ts: string
  meta?: {
    tools?: Array<{
      name: string
      ok: boolean
      detail: string
    }>
  } | null
}

export interface GetMessagesResponse {
  messages: ChatMessage[]
}

export interface SendMessageResponse {
  ok: boolean
  reply: string
}

export interface SendMessageOptions {
  use_cast_tools?: boolean
  history_mode?: 'full' | 'fresh'
  clear_thread?: boolean
}

export interface SimpleResponse {
  ok: boolean
  message: string
}

// API Methods
export const chatApi = {
  /**
   * 获取聊天消息
   */
  getMessages: (novelId: string) =>
    request.get(`/novels/${novelId}/chat/messages`) as Promise<GetMessagesResponse>,

  /**
   * 发送消息（非流式）
   */
  send: (novelId: string, message: string, opts?: SendMessageOptions) =>
    request.post(
      `/novels/${novelId}/chat`,
      {
        message,
        use_cast_tools: opts?.use_cast_tools ?? true,
        history_mode: opts?.history_mode ?? 'full',
        clear_thread: opts?.clear_thread ?? false,
      }
    ) as Promise<SendMessageResponse>,

  /**
   * 发送消息（流式 SSE）
   */
  sendStream: (novelId: string, message: string, opts?: SendMessageOptions) => {
    return fetch(`/api/v1/novels/${novelId}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        use_cast_tools: opts?.use_cast_tools ?? true,
        history_mode: opts?.history_mode ?? 'full',
        clear_thread: opts?.clear_thread ?? false,
      }),
    })
  },

  /**
   * 清空聊天线程
   */
  clearThread: (novelId: string, digestToo = false) =>
    request.post(
      `/novels/${novelId}/chat/clear`,
      { digest_too: digestToo }
    ) as Promise<SimpleResponse>,
}
