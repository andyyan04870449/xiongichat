-- Migration: Add batch upload support (minimal version)
-- Date: 2025-01-07

-- 1. 建立批次任務表（精簡版）
CREATE TABLE IF NOT EXISTS batch_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    total_files INTEGER NOT NULL,
    completed_files INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_batch_tasks_status ON batch_tasks(status);
CREATE INDEX IF NOT EXISTS idx_batch_tasks_created_at ON batch_tasks(created_at DESC);

-- 2. 修改 upload_records 表，新增批次相關欄位
ALTER TABLE upload_records 
ADD COLUMN IF NOT EXISTS batch_id UUID REFERENCES batch_tasks(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS relative_path VARCHAR(500),  -- 保留原始目錄結構
ADD COLUMN IF NOT EXISTS processing_progress INTEGER DEFAULT 0;  -- 0-100 處理進度

-- 建立索引
CREATE INDEX IF NOT EXISTS idx_upload_records_batch_id ON upload_records(batch_id);
CREATE INDEX IF NOT EXISTS idx_upload_records_batch_status ON upload_records(batch_id, status);

-- 3. 新增註解說明
COMMENT ON TABLE batch_tasks IS '批次上傳任務表';
COMMENT ON COLUMN batch_tasks.total_files IS '批次中的總檔案數';
COMMENT ON COLUMN batch_tasks.completed_files IS '已完成處理的檔案數';
COMMENT ON COLUMN batch_tasks.status IS '批次狀態: pending(等待中), processing(處理中), completed(已完成), failed(失敗)';

COMMENT ON COLUMN upload_records.batch_id IS '關聯的批次任務ID';
COMMENT ON COLUMN upload_records.relative_path IS '檔案的相對路徑，保留原始目錄結構';
COMMENT ON COLUMN upload_records.processing_progress IS '單一檔案的處理進度 (0-100)';