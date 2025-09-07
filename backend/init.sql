-- 建立 UUID 擴充
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 建立 PGVector 擴充
CREATE EXTENSION IF NOT EXISTS vector;

-- 建立對話表
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    last_message_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT conversations_user_id_check CHECK (user_id != '')
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);

-- 建立對話訊息表
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 第三階段會加入的欄位（先註解）
    -- risk_level TEXT CHECK (risk_level IN ('NONE', 'LOW', 'MEDIUM', 'HIGH', 'IMMINENT')),
    -- risk_categories TEXT[] DEFAULT '{}',
    
    -- 第二階段會加入的欄位（先註解）
    -- rag_sources JSONB,
    
    -- 索引
    CONSTRAINT conversation_messages_content_check CHECK (content != '')
);

CREATE INDEX idx_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX idx_messages_created_at ON conversation_messages(conversation_id, created_at);

-- 建立 LangGraph checkpoints 表（用於對話記憶）
CREATE TABLE IF NOT EXISTS langgraph_checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_id TEXT NOT NULL,
    parent_id TEXT,
    checkpoint JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (thread_id, checkpoint_id)
);

CREATE INDEX idx_checkpoints_thread_id ON langgraph_checkpoints(thread_id);
CREATE INDEX idx_checkpoints_created_at ON langgraph_checkpoints(created_at DESC);

-- 建立更新時間觸發器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON conversations 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- 第二階段：RAG 知識庫相關表
-- ==============================================

-- 建立知識文件表
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    category TEXT NOT NULL,
    lang TEXT NOT NULL DEFAULT 'zh-TW',
    published_date DATE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT knowledge_documents_title_check CHECK (title != ''),
    CONSTRAINT knowledge_documents_content_check CHECK (content != ''),
    CONSTRAINT knowledge_documents_source_check CHECK (source != ''),
    CONSTRAINT knowledge_documents_category_check CHECK (category != ''),
    CONSTRAINT knowledge_documents_lang_check CHECK (lang IN ('zh-TW', 'en', 'vi', 'id', 'th'))
);

CREATE INDEX idx_knowledge_documents_category ON knowledge_documents(category);
CREATE INDEX idx_knowledge_documents_lang ON knowledge_documents(lang);
CREATE INDEX idx_knowledge_documents_created_at ON knowledge_documents(created_at DESC);

-- 建立知識向量嵌入表
CREATE TABLE IF NOT EXISTS knowledge_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- OpenAI text-embedding-3-small 的維度
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT knowledge_embeddings_content_check CHECK (content != ''),
    CONSTRAINT knowledge_embeddings_chunk_index_check CHECK (chunk_index >= 0)
);

-- 建立向量索引（使用 ivfflat 算法）
CREATE INDEX idx_knowledge_embeddings_vector ON knowledge_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

CREATE INDEX idx_knowledge_embeddings_document_id ON knowledge_embeddings(document_id);
CREATE INDEX idx_knowledge_embeddings_created_at ON knowledge_embeddings(created_at DESC);

-- 建立個案檔案表（第三階段會用到，先建立）
CREATE TABLE IF NOT EXISTS cases (
    user_id TEXT PRIMARY KEY,
    nickname TEXT,
    lang TEXT DEFAULT 'zh-TW',
    stage TEXT DEFAULT 'assessment',
    goals JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT cases_user_id_check CHECK (user_id != ''),
    CONSTRAINT cases_lang_check CHECK (lang IN ('zh-TW', 'en', 'vi', 'id', 'th')),
    CONSTRAINT cases_stage_check CHECK (stage IN ('assessment', 'treatment', 'recovery'))
);

CREATE INDEX idx_cases_stage ON cases(stage);
CREATE INDEX idx_cases_updated_at ON cases(updated_at DESC);

-- 更新對話訊息表，添加 RAG 相關欄位
ALTER TABLE conversation_messages 
ADD COLUMN IF NOT EXISTS rag_sources JSONB DEFAULT NULL;

-- 建立更新時間觸發器
CREATE TRIGGER update_knowledge_documents_updated_at 
    BEFORE UPDATE ON knowledge_documents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cases_updated_at 
    BEFORE UPDATE ON cases 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- 管理網頁相關表
-- ==============================================

-- 建立上傳記錄表
CREATE TABLE IF NOT EXISTS upload_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    upload_type TEXT NOT NULL CHECK (upload_type IN ('authority_media', 'authority_contacts', 'article')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    file_path TEXT,
    file_size INTEGER,
    metadata JSONB,
    error_message TEXT,
    processing_log JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT upload_records_filename_check CHECK (filename != ''),
    CONSTRAINT upload_records_file_size_check CHECK (file_size >= 0)
);

CREATE INDEX idx_upload_records_status ON upload_records(status);
CREATE INDEX idx_upload_records_type ON upload_records(upload_type);
CREATE INDEX idx_upload_records_created_at ON upload_records(created_at DESC);

-- 建立權威媒體表
CREATE TABLE IF NOT EXISTS authoritative_media (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    upload_id UUID,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type TEXT,
    tags JSONB,
    description TEXT,
    exif_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT authoritative_media_filename_check CHECK (filename != ''),
    CONSTRAINT authoritative_media_file_size_check CHECK (file_size >= 0)
);

CREATE INDEX idx_authoritative_media_upload_id ON authoritative_media(upload_id);
CREATE INDEX idx_authoritative_media_created_at ON authoritative_media(created_at DESC);

-- 建立權威機構聯絡資訊表
CREATE TABLE IF NOT EXISTS authoritative_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    upload_id UUID,
    organization TEXT NOT NULL,  -- 機構名稱（必填）
    phone TEXT,  -- 聯絡電話
    email TEXT,  -- 電子郵件
    address VARCHAR(500),  -- 地址
    tags JSONB,  -- 標籤分類（如：戒毒諮詢、醫療、法律援助）
    notes TEXT,  -- 備註（服務時間、服務內容等）
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- 索引
    CONSTRAINT authoritative_contacts_organization_check CHECK (organization != '')
);

CREATE INDEX idx_authoritative_contacts_upload_id ON authoritative_contacts(upload_id);
CREATE INDEX idx_authoritative_contacts_organization ON authoritative_contacts(organization);
CREATE INDEX idx_authoritative_contacts_created_at ON authoritative_contacts(created_at DESC);

-- 建立更新時間觸發器
CREATE TRIGGER update_upload_records_updated_at 
    BEFORE UPDATE ON upload_records 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_authoritative_media_updated_at 
    BEFORE UPDATE ON authoritative_media 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_authoritative_contacts_updated_at 
    BEFORE UPDATE ON authoritative_contacts 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();