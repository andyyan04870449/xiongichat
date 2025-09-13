-- Migration: Add missing columns to upload_records
-- Date: 2025-01-07

-- 新增缺少的欄位
ALTER TABLE upload_records 
ADD COLUMN IF NOT EXISTS mime_type VARCHAR(100),
ADD COLUMN IF NOT EXISTS description TEXT;

-- 新增註解
COMMENT ON COLUMN upload_records.mime_type IS 'MIME類型';
COMMENT ON COLUMN upload_records.description IS '檔案描述';