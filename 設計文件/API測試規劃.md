# API 測試規劃文件

## 測試策略總覽

採用分層測試策略，從單元測試到端對端測試，確保系統穩定性與正確性。

---

## 🧪 測試工具選擇

### Python 測試框架
```bash
# 安裝測試套件
pip install pytest pytest-asyncio pytest-cov httpx faker
```

### 測試工具
- **pytest**: 主要測試框架
- **pytest-asyncio**: 非同步測試支援
- **httpx**: API 客戶端測試
- **faker**: 測試資料生成
- **locust**: 壓力測試

---

## 📘 第一階段測試：基礎聊天功能

### 1. 單元測試

```python
# tests/test_chat_agent.py
import pytest
from unittest.mock import Mock, patch

class TestChatAgent:
    @pytest.fixture
    def chat_agent(self):
        return ChatAgentNode()
    
    @pytest.mark.asyncio
    async def test_generate_reply(self, chat_agent):
        """測試回覆生成"""
        state = {
            "input_text": "你好",
            "profile": {"lang": "zh-TW"},
            "_memory": []
        }
        
        with patch('openai.ChatCompletion.create') as mock_openai:
            mock_openai.return_value = Mock(
                choices=[Mock(message=Mock(content="你好！有什麼可以幫助你的嗎？"))]
            )
            
            result = await chat_agent(state)
            assert "reply" in result
            assert len(result["reply"]) > 0
    
    @pytest.mark.asyncio
    async def test_memory_management(self, chat_agent):
        """測試記憶管理"""
        state = {
            "_memory": [{"role": "user", "content": "msg"} for _ in range(15)]
        }
        
        # 應該只保留最近10輪
        processed = chat_agent._process_memory(state["_memory"])
        assert len(processed) == 10
```

### 2. API 端點測試

```python
# tests/test_chat_api.py
import httpx
import pytest
from fastapi.testclient import TestClient

class TestChatAPI:
    @pytest.fixture
    def client(self):
        from main import app
        return TestClient(app)
    
    def test_chat_endpoint(self, client):
        """測試聊天端點"""
        response = client.post("/chat", json={
            "user_id": "test_user",
            "message": "你好"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "reply" in data
        assert len(data["reply"]) > 0
    
    def test_chat_with_existing_conversation(self, client):
        """測試延續對話"""
        # 第一次對話
        response1 = client.post("/chat", json={
            "user_id": "test_user",
            "message": "我叫小明"
        })
        conv_id = response1.json()["conversation_id"]
        
        # 延續對話
        response2 = client.post("/chat", json={
            "user_id": "test_user",
            "message": "我叫什麼名字？",
            "conversation_id": conv_id
        })
        
        assert "小明" in response2.json()["reply"]
    
    def test_conversation_history(self, client):
        """測試對話歷史"""
        # 創建對話
        chat_response = client.post("/chat", json={
            "user_id": "test_user",
            "message": "測試訊息"
        })
        conv_id = chat_response.json()["conversation_id"]
        
        # 取得歷史
        history_response = client.get(f"/conversations/{conv_id}")
        assert history_response.status_code == 200
        
        messages = history_response.json()["messages"]
        assert len(messages) >= 2  # 至少有user和assistant訊息
```

### 3. 整合測試

```python
# tests/test_workflow_integration.py
class TestWorkflowIntegration:
    @pytest.mark.asyncio
    async def test_complete_chat_flow(self):
        """測試完整聊天流程"""
        workflow = create_workflow()
        
        result = await workflow.ainvoke({
            "user_id": "test_user",
            "input_text": "你好，我最近壓力很大"
        })
        
        assert result["reply"] is not None
        assert result["user_message_id"] is not None
        assert result["assistant_message_id"] is not None
        
        # 驗證資料庫儲存
        messages = await get_messages(result["conversation_id"])
        assert len(messages) == 2
```

---

## 📗 第二階段測試：RAG 檢索功能

### 1. 檢索準確性測試

```python
# tests/test_rag_retriever.py
class TestRAGRetriever:
    @pytest.fixture
    async def retriever(self):
        return RAGRetriever()
    
    @pytest.mark.asyncio
    async def test_relevant_retrieval(self, retriever):
        """測試相關性檢索"""
        query = "高雄市毒防中心在哪裡？"
        results = await retriever.search(query, k=5)
        
        assert len(results) > 0
        assert results[0]["relevance_score"] > 0.7
        assert "地址" in results[0]["content"] or "位置" in results[0]["content"]
    
    @pytest.mark.asyncio
    async def test_no_results(self, retriever):
        """測試無結果情況"""
        query = "完全無關的查詢內容xyz123"
        results = await retriever.search(query, k=5)
        
        assert len(results) == 0 or results[0]["relevance_score"] < 0.5
```

### 2. Router 判斷測試

```python
# tests/test_router.py
class TestRouter:
    @pytest.mark.parametrize("input_text,expected_rag", [
        ("你好", False),
        ("高雄毒防中心電話", True),
        ("美沙冬服用時間", True),
        ("我今天心情不好", False),
        ("戒毒相關法律", True)
    ])
    @pytest.mark.asyncio
    async def test_routing_decision(self, input_text, expected_rag):
        """測試路由判斷"""
        router = RouterNode()
        state = {"input_text": input_text, "profile": {"lang": "zh-TW"}}
        
        result = await router(state)
        assert result["needs_rag"] == expected_rag
```

---

## 📙 第三階段測試：風險偵測

### 1. 風險分級測試

```python
# tests/test_risk_detector.py
class TestRiskDetector:
    @pytest.mark.parametrize("text,expected_level", [
        ("今天天氣真好", "NONE"),
        ("我有點想用藥", "MEDIUM"),
        ("我想自殺", "HIGH"),
        ("我現在就要結束生命", "IMMINENT")
    ])
    @pytest.mark.asyncio
    async def test_risk_levels(self, text, expected_level):
        """測試風險等級判斷"""
        detector = RiskDetectorNode()
        state = {"input_text": text, "profile": {"lang": "zh-TW"}}
        
        result = await detector(state)
        assert result["risk"]["level"] == expected_level
    
    @pytest.mark.asyncio
    async def test_risk_categories(self):
        """測試風險類別識別"""
        detector = RiskDetectorNode()
        state = {
            "input_text": "我想用海洛因然後去打人",
            "profile": {"lang": "zh-TW"}
        }
        
        result = await detector(state)
        categories = result["risk"]["categories"]
        assert "drug_use" in categories
        assert "violence" in categories
```

### 2. 高風險事件記錄測試

```python
# tests/test_risk_events.py
class TestRiskEvents:
    @pytest.mark.asyncio
    async def test_high_risk_logging(self, db_session):
        """測試高風險事件記錄"""
        # 觸發高風險
        response = await client.post("/chat", json={
            "user_id": "test_user",
            "message": "我想自殺"
        })
        
        # 檢查風險事件表
        events = await db_session.query(RiskEvent).filter_by(
            user_id="test_user"
        ).all()
        
        assert len(events) > 0
        assert events[0].risk_level in ["HIGH", "IMMINENT"]
```

---

## 🔐 第四階段測試：安全機制

### 1. 認證測試

```python
# tests/test_authentication.py
class TestAuthentication:
    def test_no_auth(self, client):
        """測試無認證請求"""
        response = client.get("/api/v1/conversations")
        assert response.status_code == 401
    
    def test_invalid_api_key(self, client):
        """測試無效 API Key"""
        response = client.get(
            "/api/v1/conversations",
            headers={"X-API-Key": "invalid_key"}
        )
        assert response.status_code == 401
    
    def test_valid_api_key(self, client, valid_api_key):
        """測試有效 API Key"""
        response = client.get(
            "/api/v1/conversations",
            headers={"X-API-Key": valid_api_key}
        )
        assert response.status_code == 200
```

### 2. 權限測試

```python
# tests/test_authorization.py
class TestAuthorization:
    def test_scope_restriction(self, client):
        """測試權限範圍限制"""
        # 只有 messages.read 權限的 token
        limited_token = create_token(["messages.read"])
        
        # 嘗試取得完整內容（需要 messages.read_full）
        response = client.get(
            "/api/v1/messages/123?include=content",
            headers={"Authorization": f"Bearer {limited_token}"}
        )
        
        assert response.status_code == 403
        assert "messages.read_full" in response.json()["required_scope"]
```

### 3. 審計測試

```python
# tests/test_audit.py
class TestAuditLogging:
    @pytest.mark.asyncio
    async def test_audit_log_creation(self, db_session):
        """測試審計日誌生成"""
        # 執行需要審計的操作
        response = await client.get(
            "/api/v1/messages/123?include=content",
            headers={"Authorization": f"Bearer {full_access_token}"}
        )
        
        # 檢查審計日誌
        logs = await db_session.query(AuditLog).filter_by(
            action="full_content_access"
        ).all()
        
        assert len(logs) > 0
        assert logs[0].resource == "message:123"
```

---

## 🔒 第五階段測試：脫敏機制

### 1. 脫敏準確性測試

```python
# tests/test_redaction.py
class TestRedaction:
    @pytest.mark.parametrize("input_text,expected", [
        ("我的身分證是A123456789", "我的身分證是[身分證]"),
        ("打給我0912345678", "打給我09XX-XXX-XXX"),
        ("信箱test@example.com", "信箱[email]")
    ])
    def test_redaction_patterns(self, input_text, expected):
        """測試脫敏模式"""
        redactor = Redactor()
        result = redactor.redact(input_text)
        assert result.redacted == expected
    
    def test_name_redaction(self):
        """測試姓名脫敏"""
        text = "我是王大明，李小華是我朋友"
        result = redactor.redact(text)
        
        assert "王○○" in result.redacted
        assert "李○○" in result.redacted
        assert "王大明" not in result.redacted
```

### 2. 動態脫敏測試

```python
# tests/test_dynamic_redaction.py
class TestDynamicRedaction:
    def test_permission_based_response(self):
        """測試基於權限的回應"""
        message_id = "test_msg_123"
        
        # 一般權限
        response1 = client.get(
            f"/messages/{message_id}",
            headers={"Authorization": f"Bearer {basic_token}"}
        )
        assert "[身分證]" in response1.json()["content"]
        
        # 完整權限
        response2 = client.get(
            f"/messages/{message_id}?include=content",
            headers={"Authorization": f"Bearer {full_token}"}
        )
        assert "A123456789" in response2.json()["content"]
```

---

## 🚀 性能測試

### 1. 回應時間測試

```python
# tests/test_performance.py
class TestPerformance:
    @pytest.mark.benchmark
    def test_chat_response_time(self, benchmark):
        """測試聊天回應時間"""
        result = benchmark(make_chat_request, "測試訊息")
        assert benchmark.stats["mean"] < 2.0  # 平均小於2秒
    
    @pytest.mark.benchmark
    def test_rag_search_time(self, benchmark):
        """測試檢索速度"""
        result = benchmark(search_knowledge, "毒防中心")
        assert benchmark.stats["mean"] < 0.5  # 平均小於500ms
```

### 2. 壓力測試

```python
# locustfile.py
from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def chat(self):
        self.client.post("/chat", json={
            "user_id": f"user_{self.user_id}",
            "message": "測試訊息"
        })
    
    @task(2)
    def search(self):
        self.client.post("/knowledge/search", json={
            "query": "毒防服務"
        })

# 執行壓力測試
# locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10
```

---

## 📊 測試覆蓋率目標

| 階段 | 單元測試 | 整合測試 | E2E測試 | 覆蓋率目標 |
|-----|---------|---------|---------|-----------|
| 第一階段 | 20個 | 5個 | 3個 | >80% |
| 第二階段 | 15個 | 5個 | 3個 | >75% |
| 第三階段 | 15個 | 4個 | 2個 | >75% |
| 第四階段 | 20個 | 6個 | 4個 | >80% |
| 第五階段 | 15個 | 4個 | 2個 | >70% |

---

## 🔄 持續整合配置

### GitHub Actions CI/CD

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 📝 測試資料管理

### 1. 測試資料生成

```python
# tests/factories.py
from faker import Faker
fake = Faker('zh_TW')

def create_test_user():
    return {
        "user_id": fake.uuid4(),
        "nickname": fake.name(),
        "lang": "zh-TW"
    }

def create_test_conversation():
    return {
        "id": fake.uuid4(),
        "user_id": create_test_user()["user_id"],
        "messages": [
            {"role": "user", "content": fake.sentence()},
            {"role": "assistant", "content": fake.sentence()}
        ]
    }
```

### 2. 測試資料清理

```python
# tests/conftest.py
@pytest.fixture
async def clean_db():
    """每個測試後清理資料庫"""
    yield
    async with get_db() as session:
        await session.execute("TRUNCATE TABLE conversations CASCADE")
        await session.commit()
```

---

## 🎯 測試執行指南

### 執行所有測試
```bash
pytest tests/
```

### 執行特定階段測試
```bash
pytest tests/test_chat_*.py  # 第一階段
pytest tests/test_rag_*.py   # 第二階段
pytest tests/test_risk_*.py  # 第三階段
```

### 生成覆蓋率報告
```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

### 執行性能測試
```bash
pytest tests/test_performance.py --benchmark-only
```

---

## ⚠️ 測試注意事項

1. **測試隔離**：每個測試應該獨立，不依賴其他測試
2. **Mock 外部服務**：測試時 Mock OpenAI API 呼叫
3. **測試資料庫**：使用獨立的測試資料庫
4. **並行執行**：使用 pytest-xdist 加速測試
5. **定期執行**：每次提交前執行完整測試套件

---

*測試是品質的保證，每個功能都應有對應的測試覆蓋*