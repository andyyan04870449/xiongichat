-- 添加聯絡人資料表缺失的欄位
ALTER TABLE authoritative_contacts 
ADD COLUMN IF NOT EXISTS name VARCHAR(255),
ADD COLUMN IF NOT EXISTS category VARCHAR(100),
ADD COLUMN IF NOT EXISTS services TEXT,
ADD COLUMN IF NOT EXISTS contact_person VARCHAR(100);

-- 更新 organization 欄位為可空（因為將使用 name 作為主要欄位）
ALTER TABLE authoritative_contacts 
ALTER COLUMN organization DROP NOT NULL;

-- 移除舊的約束
ALTER TABLE authoritative_contacts 
DROP CONSTRAINT IF EXISTS authoritative_contacts_organization_check;

-- 添加新的約束（確保 name 或 organization 至少有一個）
ALTER TABLE authoritative_contacts 
ADD CONSTRAINT authoritative_contacts_name_or_org_check 
CHECK (name IS NOT NULL OR organization IS NOT NULL);

-- 將現有的 organization 資料複製到 name 欄位
UPDATE authoritative_contacts 
SET name = organization 
WHERE name IS NULL AND organization IS NOT NULL;

-- 添加索引以提升搜尋效能
CREATE INDEX IF NOT EXISTS idx_authoritative_contacts_name ON authoritative_contacts(name);
CREATE INDEX IF NOT EXISTS idx_authoritative_contacts_category ON authoritative_contacts(category);
CREATE INDEX IF NOT EXISTS idx_authoritative_contacts_services ON authoritative_contacts USING gin(to_tsvector('simple', services));