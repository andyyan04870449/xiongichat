// API 配置選項
const API_ENDPOINTS = {
  LOCAL: 'http://localhost:8002/api/v1', // 更新為實際的本地端口
  NGROK_AI: 'https://xiongichat-ai.ngrok.io/api/v1', // AI 聊天伺服器
  NGROK_BACKEND: 'https://xiongichat-backend.ngrok.io/api/v1', // 備用後端
  NGROK_LEGACY: 'https://xiongichat.ngrok.io/api/v1', // 保留舊的通道作為備用
  // 可以在這裡添加更多端點
}

// 智能選擇初始端點：根據訪問來源自動選擇
function getInitialEndpoint(): string {
  const hostname = window.location.hostname

  // 如果是 localhost 或 127.0.0.1，優先使用本地端點
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    console.log('🏠 檢測到本地環境，嘗試使用本地後端')
    return API_ENDPOINTS.LOCAL
  }

  // 如果是其他域名（包括手機訪問），使用 AI ngrok 端點
  console.log('🤖 檢測到遠端訪問，使用 AI 聊天伺服器')
  return API_ENDPOINTS.NGROK_AI
}

// API 基礎設定 - 根據環境智能選擇
let API_BASE_URL = getInitialEndpoint()

// 開發模式切換器
const isDevelopment = true // 設為 true 來使用本地API
const useFallbackOnError = true // CORS錯誤時自動降級到Mock API
const autoSwitchEndpoints = true // 自動嘗試不同端點

// API 請求和回應的型別定義
export interface ChatRequest {
  user_id: string
  message: string
  conversation_id: string | null // 明確指定為 string | null
}

export interface ChatResponse {
  conversation_id: string
  user_message_id: string
  assistant_message_id: string
  reply: string
  timestamp: string
}

export interface ApiError {
  message: string
  status?: number
  isCorsError?: boolean
  isNetworkError?: boolean
}

export interface ConversationHistory {
  id: string
  user_id: string
  started_at: string
  ended_at: string | null
  last_message_at: string
  messages: any[]
}

export interface GetConversationsRequest {
  user_id: string
  limit?: number
  offset?: number
}

export interface ConversationMessage {
  id: string
  conversation_id: string
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

export interface ConversationDetail extends ConversationHistory {
  messages: ConversationMessage[]
}

// 簡單的字串雜湊函數
function hashString(str: string): string {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  return Math.abs(hash).toString(36)
}

// 生成基於密碼的使用者ID
export function generateUserId(password?: string): string {
  if (password) {
    // 基於密碼生成固定的 userId
    const hashedPassword = hashString(password)
    const userId = `user_${hashedPassword}`
    
    // 儲存到 localStorage 以便記住
    localStorage.setItem('chat_user_id', userId)
    localStorage.setItem('chat_user_password_hash', hashedPassword)
    
    return userId
  }
  
  // 如果沒有提供密碼，檢查 localStorage
  let userId = localStorage.getItem('chat_user_id')
  if (!userId) {
    // 如果沒有儲存的 userId，生成一個臨時的
    userId = `user_temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    localStorage.setItem('chat_user_id', userId)
  }
  return userId
}

// 檢測是否為CORS錯誤
function isCorsError(error: any): boolean {
  // CORS錯誤通常表現為 TypeError: Failed to fetch
  return error instanceof TypeError && error.message.includes('fetch')
}

// 檢測是否為網路錯誤
function isNetworkError(error: any): boolean {
  return error instanceof TypeError || 
         (error.message && (
           error.message.includes('Network') ||
           error.message.includes('fetch') ||
           error.message.includes('CORS')
         ))
}

// 使用指定端點發送聊天訊息
async function sendChatMessageToEndpoint(request: ChatRequest, endpoint: string): Promise<ChatResponse> {
  console.log(`📤 嘗試發送訊息到: ${endpoint}/chat`)
  console.log('📝 請求內容:', { user_id: request.user_id, message: request.message.substring(0, 50) + '...', conversation_id: request.conversation_id })
  
  const response = await fetch(`${endpoint}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    mode: 'cors', // 明確指定CORS模式
    body: JSON.stringify({
      user_id: request.user_id,
      message: request.message,
      conversation_id: request.conversation_id // 使用 null 而不是 undefined
    }),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError({
      message: errorData.detail || errorData.message || `API錯誤: ${response.status} ${response.statusText}`,
      status: response.status,
    })
  }

  const data: ChatResponse = await response.json()
  console.log('✅ API回應成功')
  return data
}

// 聊天API調用函數（支援自動端點切換）
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  let lastError: any = null
  
  // 嘗試當前設定的端點
  try {
    return await sendChatMessageToEndpoint(request, API_BASE_URL)
  } catch (error) {
    lastError = error
    console.warn(`當前端點 ${API_BASE_URL} 不可用`)
    
    // 如果啟用自動切換，嘗試其他端點
    if (autoSwitchEndpoints) {
      const endpoints = Object.values(API_ENDPOINTS).filter(ep => ep !== API_BASE_URL)
      
      for (const endpoint of endpoints) {
        try {
          console.log(`🔄 嘗試備用端點: ${endpoint}`)
          const result = await sendChatMessageToEndpoint(request, endpoint)
          
          // 成功後更新當前端點
          API_BASE_URL = endpoint
          console.log(`✅ 已切換到工作端點: ${API_BASE_URL}`)
          
          return result
        } catch (endpointError) {
          console.warn(`備用端點 ${endpoint} 也不可用`)
          lastError = endpointError
        }
      }
    }
  }
  
  // 所有端點都失敗，進行錯誤處理
  if (lastError instanceof ApiError) {
    throw lastError
  }
  
  // 所有端點都失敗，進行降級處理
  if (useFallbackOnError) {
    console.log('🔄 API服務不可用，自動切換到離線模式')
    return await sendChatMessageMock(request)
  }
  
  // 根據錯誤類型創建適當的錯誤訊息
  let errorMessage = '所有API服務都無法連接，請稍後再試。'
  let isSpecificError = false
  
  if (lastError && isCorsError(lastError)) {
    errorMessage = 'API服務連接受限，可能是跨域設定問題。'
    isSpecificError = true
  } else if (lastError && isNetworkError(lastError)) {
    errorMessage = '網路連線有問題，請檢查您的網路連線狀態。'
    isSpecificError = true
  } else if (lastError instanceof ApiError) {
    errorMessage = lastError.message
    isSpecificError = true
  } else if (lastError instanceof Error) {
    errorMessage = `連接失敗: ${lastError.message}`
    isSpecificError = true
  }
  
  const error = new ApiError({
    message: errorMessage,
    isCorsError: isSpecificError && lastError && isCorsError(lastError),
    isNetworkError: isSpecificError && lastError && isNetworkError(lastError),
  })
  
  throw error
}

// Mock API 函數（開發測試用）
export async function sendChatMessageMock(request: ChatRequest): Promise<ChatResponse> {
  console.log('使用Mock API回應')
  
  // 模擬API延遲
  await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000))

  // 模擬可能的錯誤（降低機率）
  if (Math.random() < 0.05) { // 5% 機率發生錯誤
    throw new ApiError({
      message: 'Mock API服務暫時不可用，請稍後再試。',
      status: 500,
    })
  }

  // 生成更智能的模擬回應（支援Markdown格式）
  const mockReplies = [
    '感謝您的分享。我理解您現在的感受，讓我們一起來討論如何處理這個狀況。\n\n**在康復的路上，每一步都很重要。**\n\n以下是一些建議：\n\n• 保持積極的心態\n• 尋求專業協助\n• 與支持團體保持聯繫\n\n如需更多幫助，請參考：[康復資源中心](https://example.com/recovery)',
    
    '我聽到了您的困擾，您的感受很重要。\n\n**面對挑戰需要很大的勇氣，我會陪伴您一起度過這段時間。**\n\n建議的應對方式：\n\n1. 深呼吸練習\n2. 正念冥想\n3. 與可信任的人交談\n4. 尋求專業諮詢\n\n記住：**您並不孤單。**',
    
    '您願意���享這些很不容易，我很感謝您的信任。\n\n**這些感受在康復過程中都是很正常的，請不要責怪自己。**\n\n讓我們一起來制定行動計畫：\n\n• **短期目標** - 建立每日健康��息\n• **中期目標** - 參加支持團體活動\n• **長期目標** - 重建穩定的生活模式\n\n需要協助時，隨時可以聯繫：[24小時諮詢熱線](https://example.com/hotline)',
    
    '我理解您的擔憂，讓我們來談談一些具體的應對策略。\n\n**每個人的康復路徑都不同，我們會找到最適合您的方式。**\n\n以下資源可能對您有幫助：\n\n1. **心理諮商** - 專業心理師一對一諮詢\n2. **團體治療** - 與同路人互相支持\n3. **家庭治療** - 修復重要的人際關係\n4. **醫療協助** - 必要時的藥物治療\n\n詳細資訊請參考：[完整治療方案](https://example.com/treatment)',
    
    '您現在身邊有支持您的人嗎？\n\n**建立支持網絡對康復非常重要。**\n\n以下是可以尋求的幫助：\n\n• 家庭成員和朋友\n• 專業諮詢師\n• 康復支持團體\n• 社工服務\n• 醫療團隊\n\n**記住，尋求幫助是勇敢的表現，不是軟弱。**\n\n如果您需要聯繫支持團體，請參考：[支持網絡資源](https://example.com/support)'
  ]

  // 根據用戶訊息內容選擇更相關的回應（支援Markdown格式）
  const userMessage = request.message.toLowerCase()
  let selectedReply

  if (userMessage.includes('難過') || userMessage.includes('傷心') || userMessage.includes('憂鬱')) {
    selectedReply = '我理解您現在的感受很複雜。\n\n**難過和傷心都是人之常情，特別是在康復過程中。**\n\n讓我們一起來找到一些能幫助您的方法：\n\n• **情緒日記** - 記錄每天的感受變化\n• **運動療法** - 透過運動釋放負面情緒\n• **藝術治療** - 用創作表達內心感受\n• **音樂療法** - 聆聽或創作舒緩音樂\n\n如果情緒持續低落，建議尋求專業協助：[心理健康資源](https://example.com/mental-health)'
  } else if (userMessage.includes('焦慮') || userMessage.includes('緊張') || userMessage.includes('擔心')) {
    selectedReply = '我聽到您的焦慮和擔心。\n\n**這些感受在康復路上很常見，我們可以學習一些放鬆技巧來幫助您管理這些情緒。**\n\n有效的放鬆方法：\n\n1. **4-7-8呼吸法** - 吸氣4秒，憋氣7秒，呼氣8秒\n2. **漸進式肌肉放鬆** - 依序放鬆身體各部位\n3. **正念冥想** - 專注當下，觀察思緒不加批判\n4. **接地技巧** - 運用五感回到當下\n\n更多焦慮管理技巧：[焦慮自助指南](https://example.com/anxiety-help)'
  } else if (userMessage.includes('戒斷') || userMessage.includes('戒毒') || userMessage.includes('康復')) {
    selectedReply = '**康復是一個勇敢的決定，也是一個過程。**\n\n每個人的路徑都不同，重要的是要有耐心和自我關懷。\n\n康復階段與應對策略：\n\n• **初期階段** - 處理生理戒斷症狀\n• **穩定期** - 建立新的生活模式\n• **維持期** - 預防復發，持續成長\n\n**我會陪伴您走過這段路。**\n\n完整康復指南：[康復路線圖](https://example.com/recovery-roadmap)'
  } else if (userMessage.includes('家人') || userMessage.includes('朋友') || userMessage.includes('關係')) {
    selectedReply = '**人際關係在康復過程中扮演重要角色。**\n\n修復和維護健康的關係需要時間，讓我們討論一些溝通的技巧：\n\n重建關係的步驟：\n\n1. **承認過錯** - 誠實面對過去的傷害\n2. **表達歉意** - 真誠的道歉和悔意\n3. **展現改變** - 用行動證明決心\n4. **建立信任** - 保持透明和一致性\n5. **設立界限** - 建立健康的相處模式\n\n**記住，關係修復是雙向的過程，需要時間和耐心。**\n\n家庭治療資源：[關係修復指南](https://example.com/relationships)'
  } else {
    selectedReply = mockReplies[Math.floor(Math.random() * mockReplies.length)]
  }

  const conversation_id = request.conversation_id || 
    `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

  return {
    conversation_id,
    user_message_id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    assistant_message_id: `msg_${Date.now() + 1}_${Math.random().toString(36).substr(2, 9)}`,
    reply: selectedReply,
    timestamp: new Date().toISOString()
  }
}

// 手動設定API端點
export function setApiEndpoint(endpoint: keyof typeof API_ENDPOINTS | string) {
  if (typeof endpoint === 'string' && endpoint in API_ENDPOINTS) {
    API_BASE_URL = API_ENDPOINTS[endpoint as keyof typeof API_ENDPOINTS]
  } else if (typeof endpoint === 'string' && endpoint.startsWith('http')) {
    API_BASE_URL = endpoint
  } else {
    console.warn('無效的API端點:', endpoint)
    return false
  }
  
  console.log(`🔧 手動設定API端點為: ${API_BASE_URL}`)
  return true
}

// 獲取當前API端點
export function getCurrentApiEndpoint(): string {
  return API_BASE_URL
}

// 獲取所有可用端點
export function getAvailableEndpoints() {
  return API_ENDPOINTS
}

// 檢查當前API狀態
export async function getApiStatus(silent = false): Promise<{
  currentEndpoint: string
  isConnected: boolean
  availableEndpoints: string[]
  testedEndpoints: { [key: string]: boolean }
}> {
  const testedEndpoints: { [key: string]: boolean } = {}
  const availableEndpoints: string[] = []
  
  // 測試所有端點
  for (const [name, endpoint] of Object.entries(API_ENDPOINTS)) {
    const isAvailable = await testEndpointConnection(endpoint, silent)
    testedEndpoints[endpoint] = isAvailable
    if (isAvailable) {
      availableEndpoints.push(endpoint)
    }
  }
  
  return {
    currentEndpoint: API_BASE_URL,
    isConnected: testedEndpoints[API_BASE_URL] || false,
    availableEndpoints,
    testedEndpoints
  }
}

// 主要聊天函數 - 智能選擇API或Mock
export async function sendChatMessageSmart(request: ChatRequest): Promise<ChatResponse> {
  // 開發模式也嘗試真實API
  if (isDevelopment) {
    console.log('🧪 開發模式：嘗試真實API')
  }
  
  // 生產模式嘗試真實API，失敗時可能降級
  try {
    return await sendChatMessage(request)
  } catch (error) {
    console.warn('真實API失敗，檢查是否需要降級到Mock API')
    
    // 如果啟用降級且錯誤是網路相關的，自動使用Mock API
    if (useFallbackOnError && error instanceof ApiError && 
        (error.isCorsError || error.isNetworkError)) {
      console.log('🔄 自動降級到Mock API')
      return await sendChatMessageMock(request)
    }
    
    // 其他情況拋出錯誤
    throw error
  }
}

// 測試特定端點的連接性
async function testEndpointConnection(endpoint: string, silent = false): Promise<boolean> {
  try {
    if (!silent) console.log(`🔍 測試API端點: ${endpoint}`)
    // 設定短超時以快速檢測不可用的端點
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 2000) // 縮短為2秒超時，加快切換速度

    const response = await fetch(`${endpoint}/chat`, {
      method: 'OPTIONS',
      mode: 'cors',
      signal: controller.signal
    })

    clearTimeout(timeoutId)
    if (!silent) console.log(`✅ 端點 ${endpoint} 連接成功`)
    return true
  } catch (error) {
    // 只在非靜默模式下顯示詳細錯誤
    if (!silent) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.warn(`⏱️ 端點 ${endpoint} 連接超時`)
      } else {
        console.warn(`❌ 端點 ${endpoint} 連接失敗`)
      }
    }
    return false
  }
}

// 自動選擇可用的API端點
async function findAvailableEndpoint(silent = false): Promise<string | null> {
  const endpoints = Object.values(API_ENDPOINTS)
  
  for (const endpoint of endpoints) {
    const isAvailable = await testEndpointConnection(endpoint, silent)
    if (isAvailable) {
      if (!silent) console.log(`🎯 選擇API端點: ${endpoint}`)
      return endpoint
    }
  }
  
  if (!silent) console.warn('⚠️ 所有API端點都無法連接，將使用Mock API')
  return null
}

// 測試API連接性（支援自動切換）
export async function testApiConnection(silent = false): Promise<boolean> {
  // 首先測試當前端點
  const currentEndpointWorks = await testEndpointConnection(API_BASE_URL, silent)
  if (currentEndpointWorks) {
    return true
  }
  
  // 如果當前端點失敗且啟用自動切換，嘗試其他端點
  if (autoSwitchEndpoints) {
    const availableEndpoint = await findAvailableEndpoint(silent)
    if (availableEndpoint) {
      API_BASE_URL = availableEndpoint
      if (!silent) console.log(`🔄 已切換到可用端點: ${API_BASE_URL}`)
      return true
    }
  }
  
  return false
}

// 獲取對話記錄API函數
export async function getConversationHistory(params: GetConversationsRequest): Promise<ConversationHistory[]> {
  let lastError: any = null
  
  // 嘗試當前設定的端點
  try {
    return await getConversationHistoryFromEndpoint(params, API_BASE_URL)
  } catch (error) {
    lastError = error
    console.warn(`當前端點 ${API_BASE_URL} 不可用於獲取對話記錄`)
    
    // 如果啟用自動切換，嘗試其他端點
    if (autoSwitchEndpoints) {
      const endpoints = Object.values(API_ENDPOINTS).filter(ep => ep !== API_BASE_URL)
      
      for (const endpoint of endpoints) {
        try {
          console.log(`🔄 嘗試備用端點獲取對話記錄: ${endpoint}`)
          const result = await getConversationHistoryFromEndpoint(params, endpoint)
          
          // 成功後更新當前端點
          API_BASE_URL = endpoint
          console.log(`✅ 已切換到工作端點: ${API_BASE_URL}`)
          
          return result
        } catch (endpointError) {
          console.warn(`備用端點 ${endpoint} 也不可用`)
          lastError = endpointError
        }
      }
    }
  }
  
  // 所有端點都失敗，進行錯誤處理
  if (lastError instanceof ApiError) {
    throw lastError
  }
  
  // 所有端點都失敗，進行降級處理（返回模擬數據）
  if (useFallbackOnError) {
    console.log('🔄 API服務不可用，使用模擬對話記錄')
    return await getConversationHistoryMock(params)
  }
  
  // 根據錯誤類型創建適當的錯誤訊息
  let errorMessage = '無法獲取對話記錄，請稍後再試。'
  
  if (lastError && isCorsError(lastError)) {
    errorMessage = '獲取對話記錄時遇到連接問題，可能是跨域設定問題。'
  } else if (lastError && isNetworkError(lastError)) {
    errorMessage = '網路連線有問題，無法獲取對話記錄。'
  } else if (lastError instanceof ApiError) {
    errorMessage = lastError.message
  } else if (lastError instanceof Error) {
    errorMessage = `獲取對話記錄失敗: ${lastError.message}`
  }
  
  throw new ApiError({
    message: errorMessage,
    isCorsError: lastError && isCorsError(lastError),
    isNetworkError: lastError && isNetworkError(lastError),
  })
}

// 使用指定端點獲取對話記錄
async function getConversationHistoryFromEndpoint(params: GetConversationsRequest, endpoint: string): Promise<ConversationHistory[]> {
  const { user_id, limit = 20, offset = 0 } = params
  const queryParams = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString()
  })
  
  const url = `${endpoint}/conversations/user/${user_id}?${queryParams}`
  console.log(`📤 嘗試獲取對話記錄: ${url}`)
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    mode: 'cors',
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError({
      message: errorData.detail || errorData.message || `獲取對話記錄失敗: ${response.status} ${response.statusText}`,
      status: response.status,
    })
  }

  const data: ConversationHistory[] = await response.json()
  console.log('✅ 獲取對話記錄成功', data.length, '筆記錄')
  return data
}

// 模擬對話記錄API函數（開發測試用）
export async function getConversationHistoryMock(params: GetConversationsRequest): Promise<ConversationHistory[]> {
  console.log('使用模擬對話記錄API')
  
  // 模擬API延遲
  await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200))

  // 模擬可能的錯誤（降低機率）
  if (Math.random() < 0.03) { // 3% 機率發生錯誤
    throw new ApiError({
      message: '模擬API服務暫時不可用，請稍後再試。',
      status: 500,
    })
  }

  // 生成模擬對話記錄 - 使用新格式
  const mockConversations: ConversationHistory[] = [
    {
      id: '1d625f51-8f29-4226-896e-8bd95111a180',
      user_id: params.user_id,
      started_at: '2025-01-14T10:30:45.255716Z',
      ended_at: null,
      last_message_at: '2025-01-14T11:15:29.343438Z',
      messages: []
    },
    {
      id: '2c735e62-9e3a-5337-897f-9ce06c22b291',
      user_id: params.user_id,
      started_at: '2025-01-13T15:20:12.189543Z',
      ended_at: null,
      last_message_at: '2025-01-13T16:45:56.721892Z',
      messages: []
    },
    {
      id: '3f846d73-ae4b-6448-9a8g-adfa7d33c3a2',
      user_id: params.user_id,
      started_at: '2025-01-12T09:00:33.567891Z',
      ended_at: null,
      last_message_at: '2025-01-12T10:30:17.829473Z',
      messages: []
    },
    {
      id: '4g957e84-bf5c-7559-ab9h-befd8e44d4b3',
      user_id: params.user_id,
      started_at: '2025-01-11T14:15:08.123456Z',
      ended_at: null,
      last_message_at: '2025-01-11T15:00:42.654321Z',
      messages: []
    }
  ]

  // 應用分頁
  const { limit = 20, offset = 0 } = params
  return mockConversations.slice(offset, offset + limit)
}

// 獲取單個對話詳細訊息 API 函數
export async function getConversationDetail(conversationId: string): Promise<ConversationDetail> {
  let lastError: any = null
  
  // 嘗試當前設定的端點
  try {
    return await getConversationDetailFromEndpoint(conversationId, API_BASE_URL)
  } catch (error) {
    lastError = error
    console.warn(`當前端點 ${API_BASE_URL} 不可用於獲取對話詳情`)
    
    // 如果啟用自動切換，嘗試其他端點
    if (autoSwitchEndpoints) {
      const endpoints = Object.values(API_ENDPOINTS).filter(ep => ep !== API_BASE_URL)
      
      for (const endpoint of endpoints) {
        try {
          console.log(`🔄 嘗試備用端點獲取對話詳情: ${endpoint}`)
          const result = await getConversationDetailFromEndpoint(conversationId, endpoint)
          
          // 成功後更新當前端點
          API_BASE_URL = endpoint
          console.log(`✅ 已切換到工作端點: ${API_BASE_URL}`)
          
          return result
        } catch (endpointError) {
          console.warn(`備用端點 ${endpoint} 也不可用`)
          lastError = endpointError
        }
      }
    }
  }
  
  // 所有端點都失敗，進行降級處理（返回模擬數據）
  if (useFallbackOnError) {
    console.log('🔄 API服務不可用，使用模擬對話詳情')
    return await getConversationDetailMock(conversationId)
  }
  
  // 根據錯誤類型創建適當的錯誤訊息
  let errorMessage = '無法獲取對話詳情，請稍後再試。'
  
  if (lastError && isCorsError(lastError)) {
    errorMessage = '獲取對話詳情時遇到連接問題，可能是跨域設定問題。'
  } else if (lastError && isNetworkError(lastError)) {
    errorMessage = '網路連線有問題，無法獲取對話詳情。'
  } else if (lastError instanceof ApiError) {
    errorMessage = lastError.message
  } else if (lastError instanceof Error) {
    errorMessage = `獲取對話詳情失敗: ${lastError.message}`
  }
  
  throw new ApiError({
    message: errorMessage,
    isCorsError: lastError && isCorsError(lastError),
    isNetworkError: lastError && isNetworkError(lastError),
  })
}

// 使用指定端點獲取單個對話詳細訊息
async function getConversationDetailFromEndpoint(conversationId: string, endpoint: string): Promise<ConversationDetail> {
  const url = `${endpoint}/conversations/${conversationId}`
  console.log(`📤 嘗試獲取對話詳情: ${url}`)
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    mode: 'cors',
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new ApiError({
      message: errorData.detail || errorData.message || `獲取對話詳情失敗: ${response.status} ${response.statusText}`,
      status: response.status,
    })
  }

  const data: ConversationDetail = await response.json()
  console.log('✅ 獲取對話詳情成功', data.messages?.length || 0, '條訊息')
  return data
}

// 模擬對話詳細訊息API函數（開發測試用）
export async function getConversationDetailMock(conversationId: string): Promise<ConversationDetail> {
  console.log('使用模擬對話詳情API')
  
  // 模擬API延遲
  await new Promise(resolve => setTimeout(resolve, 600 + Math.random() * 800))

  // 模擬可能的錯誤（降低機率）
  if (Math.random() < 0.02) { // 2% 機率發生錯誤
    throw new ApiError({
      message: '模擬API服務暫時不可用，請稍後再試。',
      status: 500,
    })
  }

  // 生成模擬對話詳情
  const mockMessages: ConversationMessage[] = [
    {
      id: 'msg_1',
      conversation_id: conversationId,
      role: 'user',
      content: '你好，我最近感到很困擾，想要尋求一些幫助。',
      created_at: '2025-08-13T05:38:45.255716Z'
    },
    {
      id: 'msg_2',
      conversation_id: conversationId,
      role: 'assistant',
      content: '您好！很感謝您願意主動尋求幫助，這是非常勇敢的第一步。\\n\\n**我是雄i聊智能諮詢師，我會陪伴您一起面對困擾。**\\n\\n請告訴我，您遇到了什麼樣的困擾呢？我會仔細聆聽，並提供專業的建議和支持。\\n\\n以下是我能協助您的範圍：\\n\\n• **情緒支持** - 焦慮、憂鬱、壓力管理\\n• **行為改變** - 戒癮支持、生活習慣調整\\n• **人際關係** - 家庭、朋友、職場關係\\n• **危機介入** - 緊急情況的專業轉介\\n\\n**記住，您並不孤單，我們一起面對。**',
      created_at: '2025-08-13T05:39:12.345678Z'
    },
    {
      id: 'msg_3',
      conversation_id: conversationId,
      role: 'user',
      content: '我最近有在使用一些物質，想要戒掉但是很困難，家人也因此很擔心我。',
      created_at: '2025-08-13T05:40:28.567890Z'
    },
    {
      id: 'msg_4',
      conversation_id: conversationId,
      role: 'assistant',
      content: '感謝您的信任，願意與我分享這麼重要的事情。\\n\\n**戒癮是一個需要勇氣和毅力的過程，您已經邁出了最重要的第一步 - 意識到問題並尋求幫助。**\\n\\n我理解您現在的困難，這是很多人在康復路上都會經歷的挑戰。讓我們一起來看看一些可以幫助您的策略：\\n\\n**立即可行的步驟：**\\n\\n1. **建立支持網絡** - 與可信任的家人朋友分享您的決心\\n2. **避免觸發情境** - 識別並避免可能引發使用的人事物\\n3. **健康替代活動** - 運動、冥想、閱讀等正面活動\\n4. **規律作息** - 建立穩定的日常routine\\n\\n**專業資源：**\\n\\n• [戒癮門診預約](https://example.com/clinic) - 專業醫療團隊協助\\n• [支持團體聚會](https://example.com/support) - 同路人互相支持\\n• [24小時諮詢專線](tel:0800-123-456) - 隨時提供協助\\n\\n關於家人的擔心，這也是可以理解的。**您的康復決心會是給他們最好的安心。**\\n\\n現在您最想從哪個方面開始改變呢？',
      created_at: '2025-08-13T05:42:29.343438Z'
    }
  ]

  const baseConversation = {
    id: conversationId,
    user_id: 'user_001',
    started_at: '2025-08-13T05:38:45.255716Z',
    ended_at: null,
    last_message_at: '2025-08-13T05:42:29.343438Z'
  }

  return {
    ...baseConversation,
    messages: mockMessages
  }
}

// 錯誤類別
export class ApiError extends Error {
  status?: number
  isCorsError?: boolean
  isNetworkError?: boolean

  constructor({ message, status, isCorsError, isNetworkError }: { 
    message: string
    status?: number
    isCorsError?: boolean
    isNetworkError?: boolean
  }) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.isCorsError = isCorsError
    this.isNetworkError = isNetworkError
    
    // 確保錯誤堆疊正確顯示
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiError)
    }
  }

  // 覆寫 toString 方法以正確顯示錯誤訊息
  toString(): string {
    return `${this.name}: ${this.message}`
  }

  // 覆寫 toJSON 方法以便正確序列化
  toJSON() {
    return {
      name: this.name,
      message: this.message,
      status: this.status,
      isCorsError: this.isCorsError,
      isNetworkError: this.isNetworkError
    }
  }
}