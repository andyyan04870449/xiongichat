-- 移除 authoritative_contacts 表中不必要的欄位
-- 移除: name, position, department, region
-- 保留: organization, phone, email, tags, notes

-- 先備份現有資料（如果需要）
-- CREATE TABLE authoritative_contacts_backup AS SELECT * FROM authoritative_contacts;

-- 移除相關索引
DROP INDEX IF EXISTS idx_authoritative_contacts_name;

-- 移除不必要的欄位
ALTER TABLE authoritative_contacts 
    DROP COLUMN IF EXISTS name,
    DROP COLUMN IF EXISTS position,
    DROP COLUMN IF EXISTS department,
    DROP COLUMN IF EXISTS region;

-- 確保 organization 欄位有適當的約束
ALTER TABLE authoritative_contacts 
    ALTER COLUMN organization SET NOT NULL,
    ADD CONSTRAINT authoritative_contacts_organization_check CHECK (organization != '');

-- 重新建立或確認索引存在
CREATE INDEX IF NOT EXISTS idx_authoritative_contacts_organization ON authoritative_contacts(organization);

-- 添加註解說明欄位用途
COMMENT ON TABLE authoritative_contacts IS '權威機構聯絡資訊表';
COMMENT ON COLUMN authoritative_contacts.organization IS '機構/單位名稱';
COMMENT ON COLUMN authoritative_contacts.phone IS '聯絡電話';
COMMENT ON COLUMN authoritative_contacts.email IS '電子郵件';
COMMENT ON COLUMN authoritative_contacts.tags IS '標籤分類（如：戒毒諮詢、醫療、法律援助）';
COMMENT ON COLUMN authoritative_contacts.notes IS '備註（服務時間、服務內容等）';