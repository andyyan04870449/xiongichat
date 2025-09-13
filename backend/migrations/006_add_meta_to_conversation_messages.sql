-- 在conversation_messages表中加入meta欄位，用於存儲策略追蹤和擴展數據
-- 執行時間: 2025-09-12

-- 新增meta欄位（JSON格式）
ALTER TABLE conversation_messages 
ADD COLUMN meta JSON NULL;

-- 加入註釋說明meta欄位的用途
COMMENT ON COLUMN conversation_messages.meta IS '存儲策略追蹤、用戶情緒狀態、AI行為分析等擴展數據的JSON欄位';

-- 可選：建立索引以提升meta欄位的查詢性能（如果需要頻繁查詢JSON內容）
-- CREATE INDEX idx_conversation_messages_meta_care_stage ON conversation_messages USING gin ((meta->>'care_stage_used'));
-- CREATE INDEX idx_conversation_messages_meta_risk_level ON conversation_messages USING gin ((meta->>'risk_level'));