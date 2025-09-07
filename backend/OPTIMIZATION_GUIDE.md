# 工作流程優化指南

## 概述

本系統實現了智能路由優化，可根據對話複雜度自動選擇執行流程，在保證品質的前提下提升效能。

## 優化內容

### 1. 智能路由器 (IntelligentRouterNode)
- 評估對話複雜度（simple/moderate/complex）
- 分析記憶依賴關係
- 識別風險信號
- 決定最優執行路徑

### 2. 三種執行流程

#### Simple Flow (簡單流程)
- **場景**：簡單問候、基本查詢
- **LLM呼叫**：2次（路由 + 回應）
- **條件**：
  - 無歷史依賴
  - 無風險信號
  - 高信心度

#### Moderate Flow (中等流程)
- **場景**：一般對話、輕度情緒支持
- **LLM呼叫**：3次（路由 + 合併分析 + 回應）
- **條件**：
  - 有歷史參照
  - 低風險
  - 中等信心度

#### Complex Flow (複雜流程)
- **場景**：毒品相關、心理危機、深度對話
- **LLM呼叫**：4-5次（完整原始流程）
- **條件**：
  - 涉及毒品
  - 情緒累積
  - 低信心度
  - 多輪對話

## 使用方式

### 1. 啟用優化版本

```bash
# 環境變數控制
export USE_OPTIMIZED_WORKFLOW=true  # 使用優化版（預設）
export USE_OPTIMIZED_WORKFLOW=false # 使用原始版
```

### 2. 測試優化效果

```bash
cd backend
python scripts/test_optimized_workflow.py
```

## 效能提升

### 預期效果
- **平均LLM呼叫**：4次 → 2.9次（-27.5%）
- **簡單對話**：4次 → 2次（-50%）
- **處理時間**：平均減少30-40%
- **成本降低**：25-30%

### 品質保證
- 複雜對話仍走完整流程
- 記憶依賴完整處理
- 風險自動升級機制
- 低信心度自動升級

## 監控指標

### 複雜度分布（預估）
- Simple: 30%
- Moderate: 50%
- Complex: 20%

### 關鍵指標
```python
{
    "avg_llm_calls": 2.9,        # 平均LLM呼叫次數
    "response_time": 1.8,         # 平均響應時間(秒)
    "complexity_accuracy": 0.95,  # 複雜度判斷準確率
    "quality_score": 0.98         # 回應品質分數
}
```

## 配置參數

### 環境變數
```bash
# 工作流程選擇
USE_OPTIMIZED_WORKFLOW=true

# 模型配置
OPENAI_MODEL_CHAT=gpt-4o
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=800

# 記憶深度
LANGGRAPH_MAX_MEMORY_TURNS=10
```

### 調整閾值

在 `intelligent_router.py` 中可調整：

```python
# 信心度閾值
CONFIDENCE_THRESHOLD = 0.7  # 低於此值自動升級

# 長對話閾值
LONG_CONVERSATION_THRESHOLD = 10  # 超過10輪自動升級

# 情緒累積閾值
EMOTIONAL_BUILDUP_THRESHOLD = 2  # 2條負面訊息升級
```

## 注意事項

1. **毒品相關內容**：永遠走complex流程，不可簡化
2. **記憶依賴**：有代詞引用時不能用simple流程
3. **情緒累積**：檢測到負面情緒累積自動升級
4. **低信心度**：信心度<0.7自動升級處理

## 回滾方案

如發現問題，可立即回滾：

```bash
# 方法1：環境變數
export USE_OPTIMIZED_WORKFLOW=false

# 方法2：直接修改 workflow.py
# 將 USE_OPTIMIZED_WORKFLOW 預設值改為 "false"
```

## 未來優化方向

1. **快取機制**：相似問題重用分析結果
2. **模型分級**：分析用gpt-4o-mini，回應用gpt-4o
3. **並行執行**：獨立節點並行處理
4. **動態調整**：根據負載自動調整策略

## 聯絡資訊

如有問題或建議，請聯繫開發團隊。