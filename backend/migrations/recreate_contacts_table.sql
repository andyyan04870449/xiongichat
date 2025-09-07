-- 備份現有資料（如果有）
CREATE TEMP TABLE authoritative_contacts_backup AS 
SELECT id, upload_id, organization, phone, email, tags, notes, created_at, updated_at 
FROM authoritative_contacts 
WHERE organization IS NOT NULL;

-- 刪除舊表
DROP TABLE IF EXISTS authoritative_contacts CASCADE;

-- 建立新表（只包含必要欄位）
CREATE TABLE authoritative_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    upload_id UUID,
    organization TEXT NOT NULL,  -- 機構名稱（必填）
    phone TEXT,  -- 聯絡電話
    email TEXT,  -- 電子郵件
    tags JSONB,  -- 標籤分類
    notes TEXT,  -- 備註
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    CONSTRAINT authoritative_contacts_organization_check CHECK (organization != '')
);

-- 建立索引
CREATE INDEX idx_authoritative_contacts_upload_id ON authoritative_contacts(upload_id);
CREATE INDEX idx_authoritative_contacts_organization ON authoritative_contacts(organization);
CREATE INDEX idx_authoritative_contacts_created_at ON authoritative_contacts(created_at DESC);

-- 建立觸發器
CREATE TRIGGER update_authoritative_contacts_updated_at 
    BEFORE UPDATE ON authoritative_contacts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- 還原資料（如果有）
INSERT INTO authoritative_contacts (id, upload_id, organization, phone, email, tags, notes, created_at, updated_at)
SELECT id, upload_id, organization, phone, email, tags, notes, created_at, updated_at
FROM authoritative_contacts_backup;

-- 顯示結果
SELECT '表已重建完成' as message;
\d authoritative_contacts