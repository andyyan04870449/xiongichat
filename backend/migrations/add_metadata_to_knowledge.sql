-- 新增 metadata 欄位到 knowledge_documents 表
-- 用於儲存結構化的毒品資訊（俗名、管制等級等）

-- 檢查欄位是否存在，避免重複執行
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'knowledge_documents' 
        AND column_name = 'metadata'
    ) THEN
        ALTER TABLE knowledge_documents 
        ADD COLUMN metadata JSONB DEFAULT '{}';
        
        -- 建立 GIN 索引以加速 JSONB 查詢
        CREATE INDEX idx_knowledge_documents_metadata 
        ON knowledge_documents USING GIN (metadata);
        
        -- 建立特定欄位的索引（針對毒品資訊查詢優化）
        CREATE INDEX idx_knowledge_documents_metadata_formal_name 
        ON knowledge_documents ((metadata->>'formal_name'));
        
        CREATE INDEX idx_knowledge_documents_metadata_control_level 
        ON knowledge_documents ((metadata->>'control_level'));
        
        RAISE NOTICE 'Successfully added metadata column to knowledge_documents table';
    ELSE
        RAISE NOTICE 'metadata column already exists in knowledge_documents table';
    END IF;
END $$;