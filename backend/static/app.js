/**
 * 雄i聊知識管理系統 - 前端應用程式
 */

class KnowledgeManager {
    constructor() {
        this.apiBase = '/api/v1';
        this.currentPage = 'upload';
        this.uploadProgress = new Map();
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadRecentUploads();
        this.setupFileUploads();
        this.setupSearch();
    }

    // 事件監聽器設置
    setupEventListeners() {
        // 導航菜單
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const page = e.currentTarget.dataset.page;
                this.navigateToPage(page);
            });
        });

        // 上傳標籤切換
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchTab(e.currentTarget.closest('.upload-card'), tab);
            });
        });

        // 全域搜尋
        document.getElementById('searchBtn').addEventListener('click', () => {
            const query = document.getElementById('globalSearch').value;
            if (query.trim()) {
                this.navigateToPage('search');
                document.getElementById('searchQuery').value = query;
                this.performSearch();
            }
        });

        document.getElementById('globalSearch').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                document.getElementById('searchBtn').click();
            }
        });

        // 進階選項切換
        document.getElementById('toggleAdvanced').addEventListener('click', () => {
            const options = document.getElementById('advancedOptions');
            const isVisible = options.style.display !== 'none';
            options.style.display = isVisible ? 'none' : 'block';
        });

        // 相似度閾值滑桿
        const thresholdSlider = document.getElementById('searchThreshold');
        const thresholdValue = document.getElementById('thresholdValue');
        if (thresholdSlider && thresholdValue) {
            thresholdSlider.addEventListener('input', (e) => {
                thresholdValue.textContent = e.target.value;
            });
        }

        // 設定頁面滑桿
        const defaultThresholdSlider = document.getElementById('defaultThreshold');
        const defaultThresholdValue = document.getElementById('defaultThresholdValue');
        if (defaultThresholdSlider && defaultThresholdValue) {
            defaultThresholdSlider.addEventListener('input', (e) => {
                defaultThresholdValue.textContent = e.target.value;
            });
        }
    }

    // 頁面導航
    navigateToPage(page) {
        // 更新導航狀態
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-page="${page}"]`).classList.add('active');

        // 顯示對應頁面
        document.querySelectorAll('.page').forEach(p => {
            p.classList.remove('active');
        });
        document.getElementById(`${page}Page`).classList.add('active');

        this.currentPage = page;

        // 載入頁面特定資料
        switch (page) {
            case 'knowledge':
                this.loadKnowledgeOverview();
                break;
            case 'upload':
                this.loadRecentUploads();
                break;
            case 'search':
                this.setupSearch();
                break;
            case 'contacts':
                this.loadContacts();
                this.setupContactsEvents();
                break;
            case 'history':
                this.loadUploadHistory();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }
    }

    // 標籤切換
    switchTab(card, tab) {
        // 更新標籤按鈕狀態
        card.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        card.querySelector(`[data-tab="${tab}"]`).classList.add('active');

        // 顯示對應內容
        card.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        card.querySelector(`#${tab}Tab`).classList.add('active');
    }

    // 檔案上傳設置
    setupFileUploads() {
        // 媒體上傳
        this.setupFileUpload('mediaUploadArea', 'mediaFile', (files) => {
            this.handleMediaUpload(files);
        });

        // 聯絡人上傳
        this.setupFileUpload('contactsUploadArea', 'contactsFile', (files) => {
            this.handleContactsUpload(files);
        });

        // 文章上傳
        this.setupFileUpload('articleUploadArea', 'articleFile', (files) => {
            this.handleArticleUpload(files);
        });

        // 上傳按鈕
        document.getElementById('uploadMediaBtn').addEventListener('click', () => {
            this.uploadMedia();
        });

        document.getElementById('uploadContactsBtn').addEventListener('click', () => {
            this.uploadContacts();
        });

        document.getElementById('uploadArticleBtn').addEventListener('click', () => {
            this.uploadArticle();
        });

        document.getElementById('uploadTextBtn').addEventListener('click', () => {
            this.uploadText();
        });
    }

    // 通用檔案上傳設置
    setupFileUpload(areaId, inputId, callback) {
        const area = document.getElementById(areaId);
        const input = document.getElementById(inputId);

        // 點擊上傳區域
        area.addEventListener('click', () => {
            input.click();
        });

        // 檔案選擇
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                callback(e.target.files);
            }
        });

        // 拖放功能
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });

        area.addEventListener('dragleave', () => {
            area.classList.remove('dragover');
        });

        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                callback(files);
            }
        });
    }

    // 媒體上傳處理
    handleMediaUpload(files) {
        const file = files[0];
        if (file) {
            const area = document.getElementById('mediaUploadArea');
            area.innerHTML = `
                <i class="fas fa-check-circle" style="color: #28a745;"></i>
                <p>已選擇: ${file.name}</p>
                <p style="font-size: 0.9rem; color: #7f8c8d;">大小: ${this.formatFileSize(file.size)}</p>
            `;
        }
    }

    // 聯絡人上傳處理
    handleContactsUpload(files) {
        const file = files[0];
        if (file) {
            const area = document.getElementById('contactsUploadArea');
            area.innerHTML = `
                <i class="fas fa-check-circle" style="color: #28a745;"></i>
                <p>已選擇: ${file.name}</p>
                <p style="font-size: 0.9rem; color: #7f8c8d;">大小: ${this.formatFileSize(file.size)}</p>
            `;

            // 顯示欄位映射
            document.getElementById('fieldMapping').style.display = 'block';
            document.getElementById('uploadContactsBtn').style.display = 'block';

            // 預覽檔案內容
            this.previewContactsFile(file);
        }
    }

    // 文章上傳處理
    handleArticleUpload(files) {
        const file = files[0];
        if (file) {
            const area = document.getElementById('articleUploadArea');
            area.innerHTML = `
                <i class="fas fa-check-circle" style="color: #28a745;"></i>
                <p>已選擇: ${file.name}</p>
                <p style="font-size: 0.9rem; color: #7f8c8d;">大小: ${this.formatFileSize(file.size)}</p>
            `;
        }
    }

    // 預覽聯絡人檔案
    async previewContactsFile(file) {
        try {
            const text = await this.readFileAsText(file);
            const lines = text.split('\n').slice(0, 5); // 只取前5行
            const headers = lines[0].split(',').map(h => h.trim());

            // 更新欄位選擇器
            document.querySelectorAll('.field-select').forEach(select => {
                select.innerHTML = '<option value="">選擇欄位...</option>';
                headers.forEach(header => {
                    const option = document.createElement('option');
                    option.value = header;
                    option.textContent = header;
                    select.appendChild(option);
                });
            });

            // 顯示預覽
            const preview = document.createElement('div');
            preview.className = 'file-preview';
            preview.innerHTML = `
                <h4>檔案預覽 (前5行)</h4>
                <pre style="background: #f8f9fa; padding: 1rem; border-radius: 4px; font-size: 0.9rem;">${lines.join('\n')}</pre>
            `;
            
            const mapping = document.getElementById('fieldMapping');
            if (mapping.querySelector('.file-preview')) {
                mapping.querySelector('.file-preview').remove();
            }
            mapping.appendChild(preview);

        } catch (error) {
            this.showToast('預覽檔案失敗', 'error');
        }
    }

    // 上傳媒體
    async uploadMedia() {
        const fileInput = document.getElementById('mediaFile');
        const tags = document.getElementById('mediaTags').value;
        const description = document.getElementById('mediaDescription').value;

        if (!fileInput.files[0]) {
            this.showToast('請選擇檔案', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        if (tags) formData.append('tags', tags);
        if (description) formData.append('description', description);

        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBase}/upload/media`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showToast('媒體上傳成功', 'success');
                this.trackUploadProgress(result.id);
                this.resetMediaForm();
            } else {
                throw new Error(result.detail || '上傳失敗');
            }
        } catch (error) {
            this.showToast(`上傳失敗: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // 上傳聯絡人
    async uploadContacts() {
        const fileInput = document.getElementById('contactsFile');
        
        if (!fileInput.files[0]) {
            this.showToast('請選擇檔案', 'warning');
            return;
        }

        // 收集欄位映射
        const fieldMapping = {};
        document.querySelectorAll('.field-select').forEach(select => {
            const field = select.dataset.field;
            const value = select.value;
            if (value) {
                fieldMapping[field] = value;
            }
        });

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('field_mapping', JSON.stringify(fieldMapping));

        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBase}/upload/contacts`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showToast('聯絡人匯入成功', 'success');
                this.trackUploadProgress(result.id);
                this.resetContactsForm();
            } else {
                throw new Error(result.detail || '匯入失敗');
            }
        } catch (error) {
            this.showToast(`匯入失敗: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // 上傳文章
    async uploadArticle() {
        const fileInput = document.getElementById('articleFile');
        const category = document.getElementById('articleCategory').value;
        const source = document.getElementById('articleSource').value;
        const lang = document.getElementById('articleLang').value;
        const date = document.getElementById('articleDate').value;

        if (!fileInput.files[0]) {
            this.showToast('請選擇檔案', 'warning');
            return;
        }

        if (!category || !source) {
            this.showToast('請填寫分類和來源', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('category', category);
        formData.append('source', source);
        formData.append('lang', lang);
        if (date) formData.append('published_date', date);

        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBase}/upload/article`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showToast('文章上傳成功', 'success');
                this.trackUploadProgress(result.id);
                this.resetArticleForm();
            } else {
                throw new Error(result.detail || '上傳失敗');
            }
        } catch (error) {
            this.showToast(`上傳失敗: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // 上傳文字
    async uploadText() {
        const title = document.getElementById('textTitle').value;
        const content = document.getElementById('textContent').value;
        const category = document.getElementById('textCategory').value;
        const source = document.getElementById('textSource').value;
        const lang = document.getElementById('textLang').value;
        const date = document.getElementById('textDate').value;

        if (!title || !content || !category || !source) {
            this.showToast('請填寫所有必填欄位', 'warning');
            return;
        }

        const requestData = {
            title,
            content,
            category,
            source,
            lang
        };

        if (date) {
            requestData.published_date = date;
        }

        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBase}/upload/text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.showToast('文字儲存成功', 'success');
                this.trackUploadProgress(result.id);
                this.resetTextForm();
            } else {
                throw new Error(result.detail || '儲存失敗');
            }
        } catch (error) {
            this.showToast(`儲存失敗: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // 追蹤上傳進度
    trackUploadProgress(uploadId) {
        this.uploadProgress.set(uploadId, 'processing');
        
        const checkStatus = async () => {
            try {
                const response = await fetch(`${this.apiBase}/upload/status/${uploadId}`);
                const status = await response.json();
                
                if (status.status === 'completed') {
                    this.uploadProgress.set(uploadId, 'completed');
                    this.loadRecentUploads();
                    this.showToast('處理完成', 'success');
                } else if (status.status === 'failed') {
                    this.uploadProgress.set(uploadId, 'failed');
                    this.showToast(`處理失敗: ${status.error_message}`, 'error');
                } else {
                    // 繼續檢查
                    setTimeout(checkStatus, 2000);
                }
            } catch (error) {
                console.error('檢查上傳狀態失敗:', error);
            }
        };

        checkStatus();
    }

    // 搜尋設置
    setupSearch() {
        document.getElementById('searchSubmitBtn').addEventListener('click', () => {
            this.performSearch();
        });

        document.getElementById('searchQuery').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });
    }

    // 執行搜尋
    async performSearch() {
        const query = document.getElementById('searchQuery').value;
        const k = parseInt(document.getElementById('searchK').value) || 10;
        const threshold = parseFloat(document.getElementById('searchThreshold').value) || 0.7;
        const filterType = document.getElementById('searchFilter').value;
        const category = document.getElementById('searchCategory').value;

        if (!query.trim()) {
            this.showToast('請輸入搜尋關鍵字', 'warning');
            return;
        }

        const searchRequest = {
            query: query.trim(),
            k,
            threshold,
            filter_type: filterType || null,
            category: category || null
        };

        try {
            this.showLoading(true);
            const response = await fetch(`${this.apiBase}/upload/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(searchRequest)
            });

            const result = await response.json();
            
            if (response.ok) {
                this.displaySearchResults(result);
            } else {
                throw new Error(result.detail || '搜尋失敗');
            }
        } catch (error) {
            this.showToast(`搜尋失敗: ${error.message}`, 'error');
        } finally {
            this.showLoading(false);
        }
    }

    // 顯示搜尋結果
    displaySearchResults(results) {
        const container = document.getElementById('searchResults');
        
        if (results.results.length === 0) {
            container.innerHTML = `
                <div class="text-center" style="padding: 3rem; color: #7f8c8d;">
                    <i class="fas fa-search" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                    <p>沒有找到相關結果</p>
                </div>
            `;
            return;
        }

        const resultsHtml = results.results.map(result => `
            <div class="result-card">
                <div class="result-header">
                    <span class="result-badge ${result.type}">${result.type === 'authority' ? '權威資料' : '文章'}</span>
                    <div class="result-title">${result.title}</div>
                    ${result.similarity_score ? `<div class="result-score">相似度: ${(result.similarity_score * 100).toFixed(1)}%</div>` : ''}
                </div>
                <div class="result-content">${result.content}</div>
                <div class="result-meta">
                    ${result.source ? `<span>來源: ${result.source}</span>` : ''}
                    ${result.category ? `<span>分類: ${result.category}</span>` : ''}
                    ${result.published_date ? `<span>日期: ${new Date(result.published_date).toLocaleDateString()}</span>` : ''}
                </div>
                <div class="result-actions">
                    <button onclick="knowledgeManager.viewDetails('${result.id}', '${result.type}')">
                        <i class="fas fa-eye"></i> 查看詳情
                    </button>
                    <button onclick="knowledgeManager.copyToClipboard('${result.id}')">
                        <i class="fas fa-copy"></i> 複製ID
                    </button>
                </div>
            </div>
        `).join('');

        container.innerHTML = resultsHtml;
    }

    // 載入最近上傳
    async loadRecentUploads() {
        try {
            const response = await fetch(`${this.apiBase}/upload/recent?limit=5`);
            const uploads = await response.json();
            
            const container = document.getElementById('recentUploadsList');
            if (uploads.length === 0) {
                container.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 2rem;">暫無上傳記錄</p>';
                return;
            }

            const uploadsHtml = uploads.map(upload => `
                <div class="upload-item">
                    <i class="fas fa-${this.getUploadIcon(upload.upload_type)}"></i>
                    <div class="upload-info">
                        <h4>${upload.filename}</h4>
                        <p>${new Date(upload.created_at).toLocaleString()}</p>
                    </div>
                    <span class="upload-status ${upload.status}">${this.getStatusText(upload.status)}</span>
                </div>
            `).join('');

            container.innerHTML = uploadsHtml;
        } catch (error) {
            console.error('載入最近上傳失敗:', error);
        }
    }

    // 載入上傳歷史
    async loadUploadHistory() {
        try {
            const response = await fetch(`${this.apiBase}/upload/recent?limit=50`);
            const uploads = await response.json();
            
            const container = document.getElementById('historyList');
            if (uploads.length === 0) {
                container.innerHTML = '<p style="color: #7f8c8d; text-align: center; padding: 2rem;">暫無歷史記錄</p>';
                return;
            }

            const historyHtml = uploads.map(upload => `
                <div class="history-item">
                    <i class="fas fa-${this.getUploadIcon(upload.upload_type)}"></i>
                    <div class="history-info">
                        <h4>${upload.filename}</h4>
                        <p>類型: ${this.getTypeText(upload.upload_type)} | 大小: ${this.formatFileSize(upload.file_size || 0)} | ${new Date(upload.created_at).toLocaleString()}</p>
                    </div>
                    <div class="history-actions">
                        <span class="upload-status ${upload.status}">${this.getStatusText(upload.status)}</span>
                        <button onclick="knowledgeManager.viewUploadDetails('${upload.id}')">
                            <i class="fas fa-info-circle"></i> 詳情
                        </button>
                    </div>
                </div>
            `).join('');

            container.innerHTML = historyHtml;
        } catch (error) {
            console.error('載入上傳歷史失敗:', error);
        }
    }

    // 載入設定
    loadSettings() {
        // 從 localStorage 載入設定
        const settings = JSON.parse(localStorage.getItem('knowledgeManagerSettings') || '{}');
        
        if (settings.maxFileSize) {
            document.getElementById('maxFileSize').value = settings.maxFileSize;
        }
        if (settings.allowedTypes) {
            document.getElementById('allowedTypes').value = settings.allowedTypes;
        }
        if (settings.defaultK) {
            document.getElementById('defaultK').value = settings.defaultK;
        }
        if (settings.defaultThreshold) {
            document.getElementById('defaultThreshold').value = settings.defaultThreshold;
            document.getElementById('defaultThresholdValue').textContent = settings.defaultThreshold;
        }
    }

    // 儲存設定
    saveSettings() {
        const settings = {
            maxFileSize: document.getElementById('maxFileSize').value,
            allowedTypes: document.getElementById('allowedTypes').value,
            defaultK: document.getElementById('defaultK').value,
            defaultThreshold: document.getElementById('defaultThreshold').value
        };
        
        localStorage.setItem('knowledgeManagerSettings', JSON.stringify(settings));
        this.showToast('設定已儲存', 'success');
    }

    // 工具函數
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    getUploadIcon(type) {
        switch (type) {
            case 'authority_media': return 'image';
            case 'authority_contacts': return 'address-book';
            case 'article': return 'file-alt';
            default: return 'file';
        }
    }

    getTypeText(type) {
        switch (type) {
            case 'authority_media': return '權威媒體';
            case 'authority_contacts': return '權威聯絡人';
            case 'article': return '文章';
            default: return '未知';
        }
    }

    getStatusText(status) {
        switch (status) {
            case 'pending': return '等待中';
            case 'processing': return '處理中';
            case 'completed': return '已完成';
            case 'failed': return '失敗';
            default: return '未知';
        }
    }

    async readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = e => resolve(e.target.result);
            reader.onerror = reject;
            reader.readAsText(file);
        });
    }

    // 表單重置
    resetMediaForm() {
        document.getElementById('mediaFile').value = '';
        document.getElementById('mediaTags').value = '';
        document.getElementById('mediaDescription').value = '';
        document.getElementById('mediaUploadArea').innerHTML = `
            <i class="fas fa-cloud-upload-alt"></i>
            <p>拖放圖片檔案到這裡，或點擊選擇檔案</p>
            <input type="file" id="mediaFile" accept="image/*,video/*,audio/*" multiple>
            <button class="upload-btn">選擇檔案</button>
        `;
        this.setupFileUpload('mediaUploadArea', 'mediaFile', (files) => {
            this.handleMediaUpload(files);
        });
    }

    resetContactsForm() {
        document.getElementById('contactsFile').value = '';
        document.getElementById('fieldMapping').style.display = 'none';
        document.getElementById('uploadContactsBtn').style.display = 'none';
        document.getElementById('contactsUploadArea').innerHTML = `
            <i class="fas fa-file-csv"></i>
            <p>拖放 CSV/Excel 檔案到這裡，或點擊選擇檔案</p>
            <input type="file" id="contactsFile" accept=".csv,.xlsx,.json">
            <button class="upload-btn">選擇檔案</button>
        `;
        this.setupFileUpload('contactsUploadArea', 'contactsFile', (files) => {
            this.handleContactsUpload(files);
        });
    }

    resetArticleForm() {
        document.getElementById('articleFile').value = '';
        document.getElementById('articleCategory').value = '';
        document.getElementById('articleSource').value = '';
        document.getElementById('articleLang').value = 'zh-TW';
        document.getElementById('articleDate').value = '';
        document.getElementById('articleUploadArea').innerHTML = `
            <i class="fas fa-file-upload"></i>
            <p>拖放文件檔案到這裡，或點擊選擇檔案</p>
            <input type="file" id="articleFile" accept=".pdf,.docx,.txt,.md,.html">
            <button class="upload-btn">選擇檔案</button>
        `;
        this.setupFileUpload('articleUploadArea', 'articleFile', (files) => {
            this.handleArticleUpload(files);
        });
    }

    resetTextForm() {
        document.getElementById('textTitle').value = '';
        document.getElementById('textContent').value = '';
        document.getElementById('textCategory').value = '';
        document.getElementById('textSource').value = '';
        document.getElementById('textLang').value = 'zh-TW';
        document.getElementById('textDate').value = '';
    }

    // 查看詳情
    viewDetails(id, type) {
        // 這裡可以實作詳情查看功能
        this.showToast(`查看 ${type} 詳情: ${id}`, 'info');
    }

    // 複製到剪貼簿
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('已複製到剪貼簿', 'success');
        } catch (error) {
            this.showToast('複製失敗', 'error');
        }
    }

    // 查看上傳詳情
    viewUploadDetails(uploadId) {
        // 這裡可以實作上傳詳情查看功能
        this.showToast(`查看上傳詳情: ${uploadId}`, 'info');
    }

    // 顯示載入狀態
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }

    // 顯示 Toast 通知
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        container.appendChild(toast);

        // 自動移除
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    getToastIcon(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': return 'exclamation-circle';
            case 'warning': return 'exclamation-triangle';
            default: return 'info-circle';
        }
    }

    // ========== 聯絡管理功能 ==========
    
    setupContactsEvents() {
        // 聯絡管理標籤切換
        document.querySelectorAll('.contact-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                this.switchContactsTab(tab);
            });
        });

        // 聯絡表單提交
        const contactForm = document.getElementById('contactForm');
        if (contactForm) {
            contactForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveContact();
            });
        }

        // 批次上傳區域
        const batchUploadArea = document.getElementById('contactsBatchUploadArea');
        const batchFileInput = document.getElementById('contactsBatchFile');
        
        if (batchUploadArea && batchFileInput) {
            batchUploadArea.addEventListener('click', () => batchFileInput.click());
            
            batchUploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                batchUploadArea.classList.add('dragover');
            });
            
            batchUploadArea.addEventListener('dragleave', () => {
                batchUploadArea.classList.remove('dragover');
            });
            
            batchUploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                batchUploadArea.classList.remove('dragover');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.uploadContactsBatch(files[0]);
                }
            });
            
            batchFileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.uploadContactsBatch(e.target.files[0]);
                }
            });
        }
    }

    switchContactsTab(tab) {
        // 更新標籤按鈕狀態
        document.querySelectorAll('.contact-tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });
        
        // 顯示對應內容
        document.querySelectorAll('.contact-tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        const tabMap = {
            'contactsList': 'contactsListTab',
            'contactsUpload': 'contactsUploadTab',
            'contactsStats': 'contactsStatsTab'
        };
        
        const tabElement = document.getElementById(tabMap[tab]);
        if (tabElement) {
            tabElement.classList.add('active');
        }
        
        // 載入對應資料
        if (tab === 'contactsStats') {
            this.loadContactsStats();
        }
    }

    async loadContacts() {
        try {
            const response = await fetch(`${this.apiBase}/contacts?limit=1000`);
            if (!response.ok) throw new Error('載入失敗');
            
            this.allContacts = await response.json();
            this.renderContacts();
            this.loadContactsStats();
            
        } catch (error) {
            console.error('載入聯絡人失敗:', error);
            this.showToast('載入聯絡人資料失敗', 'error');
        }
    }

    renderContacts() {
        const tbody = document.getElementById('contactsTableBody');
        if (!tbody) return;
        
        if (!this.allContacts || this.allContacts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">尚無聯絡資訊</td></tr>';
            return;
        }
        
        console.log('渲染聯絡人資料，第一筆:', this.allContacts[0]);
        console.log('地址欄位:', this.allContacts[0]?.address);
        
        tbody.innerHTML = this.allContacts.map(contact => `
            <tr>
                <td><strong>${this.escapeHtml(contact.organization)}</strong></td>
                <td>${contact.phone || '-'}</td>
                <td>${contact.email ? `<a href="mailto:${contact.email}">${contact.email}</a>` : '-'}</td>
                <td>${contact.address ? this.escapeHtml(contact.address) : '-'}</td>
                <td>${this.renderContactTags(contact.tags)}</td>
                <td>${contact.notes ? this.escapeHtml(contact.notes).substring(0, 50) + '...' : '-'}</td>
                <td>
                    <button class="btn-sm" onclick="knowledgeManager.editContact('${contact.id}')">編輯</button>
                    <button class="btn-sm btn-danger" onclick="knowledgeManager.deleteContact('${contact.id}')">刪除</button>
                </td>
            </tr>
        `).join('');
    }

    renderContactTags(tags) {
        if (!tags || tags.length === 0) return '-';
        return tags.map(tag => `<span class="tag">${this.escapeHtml(tag)}</span>`).join(' ');
    }

    async loadContactsStats() {
        if (!this.allContacts) return;
        
        const totalContacts = this.allContacts.length;
        const medicalContacts = this.allContacts.filter(c => 
            c.tags && c.tags.some(tag => tag.includes('醫療'))
        ).length;
        const counselingContacts = this.allContacts.filter(c => 
            c.tags && c.tags.some(tag => tag.includes('諮詢') || tag.includes('諮商'))
        ).length;
        const phoneContacts = this.allContacts.filter(c => c.phone).length;
        
        // 更新統計卡片
        document.getElementById('totalContactsCount').textContent = totalContacts;
        document.getElementById('medicalContactsCount').textContent = medicalContacts;
        document.getElementById('counselingContactsCount').textContent = counselingContacts;
        document.getElementById('phoneContactsCount').textContent = phoneContacts;
        
        // 計算標籤分布
        const tagCounts = {};
        this.allContacts.forEach(contact => {
            if (contact.tags) {
                contact.tags.forEach(tag => {
                    tagCounts[tag] = (tagCounts[tag] || 0) + 1;
                });
            }
        });
        
        // 顯示標籤統計
        const tagDistribution = document.getElementById('tagDistribution');
        if (tagDistribution) {
            const sortedTags = Object.entries(tagCounts).sort((a, b) => b[1] - a[1]);
            
            tagDistribution.innerHTML = sortedTags.map(([tag, count]) => `
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>${this.escapeHtml(tag)}</span>
                        <span>${count} 個機構</span>
                    </div>
                    <div style="background: #e0e0e0; height: 20px; border-radius: 10px; overflow: hidden;">
                        <div style="background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; width: ${(count / totalContacts) * 100}%;"></div>
                    </div>
                </div>
            `).join('');
        }
    }

    async saveContact() {
        const contactId = document.getElementById('contactId').value;
        const formData = {
            organization: document.getElementById('contactOrganization').value,
            phone: document.getElementById('contactPhone').value,
            email: document.getElementById('contactEmail').value,
            address: document.getElementById('contactAddress').value,
            notes: document.getElementById('contactNotes').value,
            tags: Array.from(document.querySelectorAll('#contactForm input[type="checkbox"]:checked'))
                .map(cb => cb.value)
        };
        
        try {
            const url = contactId 
                ? `${this.apiBase}/contacts/${contactId}`
                : `${this.apiBase}/contacts`;
            
            const method = contactId ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) throw new Error('儲存失敗');
            
            this.showToast(contactId ? '更新成功' : '新增成功', 'success');
            closeContactModal();
            this.loadContacts();
            
        } catch (error) {
            console.error('儲存失敗:', error);
            this.showToast('儲存失敗，請稍後再試', 'error');
        }
    }

    async deleteContact(id) {
        if (!confirm('確定要刪除這筆聯絡資訊嗎？')) return;
        
        try {
            const response = await fetch(`${this.apiBase}/contacts/${id}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('刪除失敗');
            
            this.showToast('刪除成功', 'success');
            this.loadContacts();
            
        } catch (error) {
            console.error('刪除失敗:', error);
            this.showToast('刪除失敗，請稍後再試', 'error');
        }
    }

    editContact(id) {
        const contact = this.allContacts.find(c => c.id === id);
        if (!contact) return;
        
        document.getElementById('contactModalTitle').textContent = '編輯聯絡資訊';
        document.getElementById('contactId').value = id;
        document.getElementById('contactOrganization').value = contact.organization;
        document.getElementById('contactPhone').value = contact.phone || '';
        document.getElementById('contactEmail').value = contact.email || '';
        document.getElementById('contactAddress').value = contact.address || '';
        document.getElementById('contactNotes').value = contact.notes || '';
        
        // 設置標籤
        document.querySelectorAll('#contactForm input[type="checkbox"]').forEach(checkbox => {
            checkbox.checked = contact.tags && contact.tags.includes(checkbox.value);
        });
        
        document.getElementById('contactModal').style.display = 'block';
    }

    async uploadContactsBatch(file) {
        if (!file.name.match(/\.(csv|xlsx|xls)$/)) {
            this.showToast('請上傳 CSV 或 Excel 檔案', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        // 設置欄位映射
        const fieldMapping = {
            organization: 'organization',
            phone: 'phone',
            email: 'email',
            address: 'address',
            tags: 'tags',
            notes: 'notes'
        };
        formData.append('field_mapping', JSON.stringify(fieldMapping));
        
        this.showLoadingOverlay();
        
        try {
            const response = await fetch(`${this.apiBase}/upload/contacts`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('上傳失敗');
            
            this.showToast('檔案上傳成功，正在處理...', 'success');
            
            // 等待處理完成後重新載入
            setTimeout(() => {
                this.loadContacts();
                this.hideLoadingOverlay();
            }, 2000);
            
        } catch (error) {
            console.error('上傳失敗:', error);
            this.showToast('上傳失敗，請檢查檔案格式', 'error');
            this.hideLoadingOverlay();
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.toString().replace(/[&<>"']/g, m => map[m]);
    }

    showLoadingOverlay() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoadingOverlay() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    // ========== 知識庫管理功能 ==========
    
    async loadKnowledgeOverview() {
        try {
            const response = await fetch(`${this.apiBase}/knowledge/`);
            if (!response.ok) throw new Error('載入失敗');
            
            const data = await response.json();
            
            // 更新統計
            this.updateKnowledgeStats(data.stats);
            
            // 顯示權威資料
            this.renderAuthorityData(data.authority_data);
            
            // 顯示檔案
            this.renderFiles(data.recent_files);
            
        } catch (error) {
            console.error('載入知識庫失敗:', error);
            this.showToast('載入知識庫資料失敗', 'error');
        }
    }

    updateKnowledgeStats(stats) {
        document.getElementById('totalFiles').textContent = stats.total_files || 0;
        document.getElementById('pdfCount').textContent = stats.pdf_count || 0;
        document.getElementById('imageCount').textContent = stats.image_count || 0;
        document.getElementById('authorityCount').textContent = stats.authority_count || 0;
    }

    renderAuthorityData(authorityData) {
        const container = document.getElementById('authorityList');
        if (!container) return;
        
        if (!authorityData.contacts || authorityData.contacts.length === 0) {
            container.innerHTML = '<p style="color: #999; text-align: center;">尚無權威資料</p>';
            return;
        }
        
        container.innerHTML = authorityData.contacts.map(contact => `
            <div class="authority-item">
                <div class="authority-left">
                    <h4>${this.escapeHtml(contact.organization)}</h4>
                    <div class="authority-info">
                        ${contact.phone ? `
                            <span>
                                <i class="fas fa-phone"></i>
                                ${contact.phone}
                            </span>
                        ` : ''}
                        ${contact.email ? `
                            <span>
                                <i class="fas fa-envelope"></i>
                                ${contact.email}
                            </span>
                        ` : ''}
                    </div>
                </div>
                ${contact.tags && contact.tags.length > 0 ? `
                    <div class="authority-tags">
                        ${contact.tags.map(tag => `<span class="authority-tag">${tag}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `).join('');
    }

    renderFiles(files) {
        const container = document.getElementById('filesList');
        if (!container) return;
        
        if (!files || files.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #999;">尚無檔案</p>';
            return;
        }
        
        container.innerHTML = files.map(file => this.createFileListItem(file)).join('');
    }

    createFileCard(file) {
        const isPDF = file.mime_type === 'application/pdf';
        const isImage = file.mime_type && file.mime_type.startsWith('image/');
        
        return `
            <div class="file-card" onclick="knowledgeManager.previewFile('${file.id}')">
                <div class="file-icon ${isPDF ? 'pdf' : isImage ? 'image' : ''}">
                    <i class="fas fa-${isPDF ? 'file-pdf' : isImage ? 'file-image' : 'file'}"></i>
                </div>
                <div class="file-name" title="${this.escapeHtml(file.filename)}">
                    ${this.escapeHtml(file.filename)}
                </div>
                <div class="file-meta">
                    ${this.formatFileSize(file.size)} • ${this.formatDate(file.created_at)}
                </div>
                <div class="file-actions">
                    <button class="btn-icon" onclick="event.stopPropagation(); knowledgeManager.downloadFile('${file.id}')">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn-icon" onclick="event.stopPropagation(); knowledgeManager.deleteFile('${file.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    createFileListItem(file) {
        const isPDF = file.mime_type === 'application/pdf';
        const isImage = file.mime_type && file.mime_type.startsWith('image/');
        const fileSize = this.formatFileSize(file.size);
        const fileDate = this.formatDate(file.created_at);
        
        return `
            <div class="file-item" onclick="knowledgeManager.previewFile('${file.id}')">
                <div class="file-left">
                    <div class="file-icon ${isPDF ? 'pdf' : isImage ? 'image' : 'default'}">
                        <i class="fas fa-${isPDF ? 'file-pdf' : isImage ? 'file-image' : 'file'}"></i>
                    </div>
                    <div class="file-info">
                        <div class="file-name">${this.escapeHtml(file.filename)}</div>
                        <div class="file-meta">
                            <span><i class="fas fa-hdd"></i> ${fileSize}</span>
                            <span><i class="fas fa-calendar"></i> ${fileDate}</span>
                            <span><i class="fas fa-tag"></i> ${file.type}</span>
                        </div>
                    </div>
                </div>
                <div class="file-actions">
                    <button onclick="event.stopPropagation(); knowledgeManager.previewFile('${file.id}')">
                        <i class="fas fa-eye"></i> 預覽
                    </button>
                    <button onclick="event.stopPropagation(); knowledgeManager.deleteFile('${file.id}')">
                        <i class="fas fa-trash"></i> 刪除
                    </button>
                </div>
            </div>
        `;
    }

    setView(viewMode) {
        // Deprecated - now using list view only
        return;
    }

    async search() {
        const query = document.getElementById('knowledgeSearch').value;
        if (!query.trim()) {
            this.loadKnowledgeOverview();
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBase}/knowledge/search?query=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error('搜尋失敗');
            
            const results = await response.json();
            
            // 顯示搜尋結果
            this.renderFiles(results.files);
            
            // 如果有權威資料結果，更新顯示
            if (results.authority_data && results.authority_data.length > 0) {
                this.renderAuthorityData({ contacts: results.authority_data });
            }
            
            this.showToast(`找到 ${results.total_results} 筆結果`, 'success');
            
        } catch (error) {
            console.error('搜尋失敗:', error);
            this.showToast('搜尋失敗', 'error');
        }
    }

    filterFiles() {
        const filter = document.getElementById('fileFilter').value;
        // 實作篩選邏輯
        this.loadKnowledgeOverview();
    }

    // 上傳Modal相關
    openUploadModal() {
        document.getElementById('uploadModal').style.display = 'block';
        this.setupUploadArea();
    }

    closeUploadModal() {
        document.getElementById('uploadModal').style.display = 'none';
        this.resetUploadForm();
    }

    setupUploadArea() {
        const area = document.getElementById('modalUploadArea');
        const input = document.getElementById('modalFileInput');
        const uploadBtn = area.querySelector('.upload-btn');
        
        uploadBtn.addEventListener('click', () => input.click());
        
        input.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files);
        });
        
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });
        
        area.addEventListener('dragleave', () => {
            area.classList.remove('dragover');
        });
        
        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            this.handleFileSelect(e.dataTransfer.files);
        });
    }

    handleFileSelect(files) {
        const preview = document.getElementById('uploadPreview');
        const filesList = document.getElementById('filesList');
        
        if (files.length > 0) {
            preview.style.display = 'block';
            filesList.innerHTML = Array.from(files).map(file => `
                <div class="file-item">
                    <i class="fas fa-file"></i>
                    <span>${file.name}</span>
                    <span>${this.formatFileSize(file.size)}</span>
                </div>
            `).join('');
            
            this.pendingFiles = files;
        }
    }

    async uploadFiles() {
        if (!this.pendingFiles || this.pendingFiles.length === 0) {
            this.showToast('請選擇檔案', 'warning');
            return;
        }
        
        const formData = new FormData();
        for (let file of this.pendingFiles) {
            formData.append('files', file);
        }
        
        formData.append('category', document.getElementById('fileCategory').value);
        formData.append('tags', document.getElementById('fileTags').value);
        formData.append('description', document.getElementById('fileDescription').value);
        
        try {
            this.showLoadingOverlay();
            
            const response = await fetch(`${this.apiBase}/upload/multiple`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error('上傳失敗');
            
            this.showToast('檔案上傳成功', 'success');
            this.closeUploadModal();
            this.loadKnowledgeOverview();
            
        } catch (error) {
            console.error('上傳失敗:', error);
            this.showToast('上傳失敗', 'error');
        } finally {
            this.hideLoadingOverlay();
        }
    }

    resetUploadForm() {
        document.getElementById('modalFileInput').value = '';
        document.getElementById('fileCategory').value = '';
        document.getElementById('fileTags').value = '';
        document.getElementById('fileDescription').value = '';
        document.getElementById('uploadPreview').style.display = 'none';
        this.pendingFiles = null;
    }

    // 檔案預覽
    async previewFile(fileId) {
        try {
            const response = await fetch(`${this.apiBase}/knowledge/file/${fileId}/preview`);
            if (!response.ok) throw new Error('無法預覽');
            
            const preview = await response.json();
            
            const modal = document.getElementById('previewModal');
            const content = document.getElementById('previewContent');
            
            if (preview.type === 'pdf') {
                content.innerHTML = `<iframe src="${preview.url}" style="width: 100%; height: 100%;"></iframe>`;
            } else if (preview.type === 'image') {
                content.innerHTML = `<img src="${preview.url}" style="max-width: 100%; max-height: 100%; object-fit: contain;">`;
            }
            
            modal.style.display = 'block';
            this.currentFileId = fileId;
            
        } catch (error) {
            console.error('預覽失敗:', error);
            this.showToast('此檔案無法預覽', 'error');
        }
    }

    closePreview() {
        document.getElementById('previewModal').style.display = 'none';
        document.getElementById('previewContent').innerHTML = '';
        this.currentFileId = null;
    }

    async downloadFile(fileId) {
        const id = fileId || this.currentFileId;
        if (!id) return;
        
        window.open(`${this.apiBase}/upload/download/${id}`, '_blank');
    }

    async deleteFile(fileId) {
        if (!confirm('確定要刪除此檔案嗎？')) return;
        
        try {
            const response = await fetch(`${this.apiBase}/knowledge/file/${fileId}`, {
                method: 'DELETE'
            });
            
            if (!response.ok) throw new Error('刪除失敗');
            
            this.showToast('檔案已刪除', 'success');
            this.loadKnowledgeOverview();
            
        } catch (error) {
            console.error('刪除失敗:', error);
            this.showToast('刪除失敗', 'error');
        }
    }

    // 工具函數
    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-TW');
    }
}

// 初始化應用程式
const knowledgeManager = new KnowledgeManager();

// 設定頁面儲存按鈕
document.addEventListener('DOMContentLoaded', () => {
    // 載入知識庫資料（因為知識庫是預設頁面）
    knowledgeManager.loadKnowledgeOverview();
    
    const saveBtn = document.querySelector('.save-settings-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            knowledgeManager.saveSettings();
        });
    }
});

// ========== 聯絡管理全局函數 ==========

function openAddContactModal() {
    document.getElementById('contactModalTitle').textContent = '新增聯絡資訊';
    document.getElementById('contactForm').reset();
    document.getElementById('contactId').value = '';
    document.getElementById('contactModal').style.display = 'block';
}

function closeContactModal() {
    document.getElementById('contactModal').style.display = 'none';
}

function searchContacts() {
    const searchInput = document.getElementById('contactSearchInput');
    const tagFilter = document.getElementById('contactTagFilter');
    
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const selectedTag = tagFilter ? tagFilter.value : '';
    
    const filteredContacts = knowledgeManager.allContacts.filter(contact => {
        const matchSearch = !searchTerm || 
            contact.organization.toLowerCase().includes(searchTerm) ||
            (contact.phone && contact.phone.includes(searchTerm)) ||
            (contact.email && contact.email.toLowerCase().includes(searchTerm)) ||
            (contact.address && contact.address.toLowerCase().includes(searchTerm)) ||
            (contact.notes && contact.notes.toLowerCase().includes(searchTerm));
        
        const matchTag = !selectedTag || 
            (contact.tags && contact.tags.includes(selectedTag));
        
        return matchSearch && matchTag;
    });
    
    knowledgeManager.allContacts = filteredContacts;
    knowledgeManager.renderContacts();
}

function downloadContactTemplate() {
    const csvContent = `organization,phone,email,address,tags,notes
高雄市毒品危害防制中心,07-2134875,khdrugprev@kcg.gov.tw,高雄市前鎮區凱旋四路130號,"戒毒諮詢,個案管理",提供24小時戒毒成功專線及個案管理服務
高雄市立凱旋醫院,07-7513171,info@ksph.kcg.gov.tw,高雄市苓雅區凱旋二路130號,"醫療服務,成癮治療",成癮治療門診、美沙冬替代療法
高雄市生命線協會,07-2815555,khhlifeline@gmail.com,高雄市三民區大昌一路305號,"心理諮商,危機處理",提供情緒支持及危機處理服務`;
    
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'contacts_template.csv';
    link.click();
}
