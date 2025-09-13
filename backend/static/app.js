/**
 * 雄i聊知識管理系統 - 簡化版
 * 這個版本確保不會有任何 null 錯誤
 */

console.log('Loading app-simple.js...');

// 等待 DOM 完全載入
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing app...');
    
    // API 基礎設置
    const API_BASE = '/api/v1';
    
    // 當前頁面
    let currentPage = 'upload';
    
    // ========== 工具函數 ==========
    
    // 安全獲取元素
    function getEl(id) {
        return document.getElementById(id);
    }
    
    // 安全添加事件
    function addEvent(id, event, handler) {
        const el = getEl(id);
        if (el) {
            el.addEventListener(event, handler);
            console.log(`Event added: ${id}.${event}`);
        } else {
            console.log(`Element not found: ${id}`);
        }
    }
    
    // 顯示消息
    function showMessage(msg, type = 'info') {
        console.log(`${type}: ${msg}`);
        // 可以在這裡添加 UI 通知
        alert(msg);
    }
    
    // ========== 頁面導航 ==========
    
    function switchPage(pageName) {
        console.log(`Switching to page: ${pageName}`);
        
        // 隱藏所有頁面
        const pages = document.querySelectorAll('.page');
        pages.forEach(p => {
            p.style.display = 'none';
        });
        
        // 顯示目標頁面
        const targetPage = getEl(pageName + 'Page');
        if (targetPage) {
            targetPage.style.display = 'block';
        }
        
        // 更新導航選中狀態
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.dataset.page === pageName) {
                item.classList.add('active');
            }
        });
        
        currentPage = pageName;
    }
    
    // ========== 搜尋功能 ==========
    
    function doSearch() {
        const searchInput = getEl('globalSearch');
        if (!searchInput) return;
        
        const query = searchInput.value.trim();
        if (!query) {
            showMessage('請輸入搜尋關鍵字', 'warning');
            return;
        }
        
        console.log(`Searching for: ${query}`);
        
        // 切換到搜尋頁面
        switchPage('search');
        
        // 設置搜尋框內容
        const searchQuery = getEl('searchQuery');
        if (searchQuery) {
            searchQuery.value = query;
        }
        
        // 執行搜尋
        performSearch(query);
    }
    
    async function performSearch(query) {
        const resultsDiv = getEl('searchResults');
        if (!resultsDiv) return;
        
        resultsDiv.innerHTML = '<p>搜尋中...</p>';
        
        try {
            const response = await fetch(`${API_BASE}/knowledge/search`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    k: 10,
                    threshold: 0.7
                })
            });
            
            if (!response.ok) {
                throw new Error('Search failed');
            }
            
            const results = await response.json();
            displaySearchResults(results);
            
        } catch (error) {
            console.error('Search error:', error);
            resultsDiv.innerHTML = '<p style="color: red;">搜尋失敗，請稍後再試</p>';
        }
    }
    
    function displaySearchResults(results) {
        const resultsDiv = getEl('searchResults');
        if (!resultsDiv) return;
        
        if (!results || results.length === 0) {
            resultsDiv.innerHTML = '<p>沒有找到相關結果</p>';
            return;
        }
        
        let html = '<div class="results-list">';
        results.forEach(result => {
            html += `
                <div class="result-item">
                    <h3>${result.title || '無標題'}</h3>
                    <p>${result.content || ''}</p>
                    <small>相似度: ${(result.similarity_score * 100).toFixed(1)}%</small>
                </div>
            `;
        });
        html += '</div>';
        
        resultsDiv.innerHTML = html;
    }
    
    // ========== 上傳功能 ==========
    
    let uploadedFiles = [];
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    function formatDate(date) {
        const d = new Date(date);
        const year = d.getFullYear();
        const month = d.getMonth() + 1;
        const day = d.getDate();
        const hours = d.getHours();
        const minutes = d.getMinutes().toString().padStart(2, '0');
        const seconds = d.getSeconds().toString().padStart(2, '0');
        const period = hours >= 12 ? '下午' : '上午';
        const displayHours = hours % 12 || 12;
        return `${year}/${month}/${day} ${period}${displayHours}:${minutes}:${seconds}`;
    }
    
    function getFileIcon(fileName) {
        const ext = fileName.split('.').pop().toLowerCase();
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) return '🖼️';
        if (['pdf'].includes(ext)) return '📕';
        if (['doc', 'docx'].includes(ext)) return '📘';
        if (['xls', 'xlsx', 'csv'].includes(ext)) return '📊';
        if (['txt', 'md'].includes(ext)) return '📝';
        return '📄';
    }
    
    function getFileType(fileName) {
        const ext = fileName.split('.').pop().toLowerCase();
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(ext)) return '圖片';
        if (['pdf'].includes(ext)) return 'PDF';
        if (['doc', 'docx'].includes(ext)) return '文件';
        if (['xls', 'xlsx', 'csv'].includes(ext)) return '表格';
        if (['txt', 'md'].includes(ext)) return '文字';
        return '文章';
    }
    
    function renderFileList() {
        const fileList = getEl('fileList');
        if (!fileList || uploadedFiles.length === 0) return;
        
        let html = '';
        uploadedFiles.forEach((file, index) => {
            html += `
                <div class="file-item" data-index="${index}">
                    <div class="file-info">
                        <div class="file-icon">${getFileIcon(file.name)}</div>
                        <div class="file-details">
                            <div class="file-name">${file.name}</div>
                            <div class="file-meta">類型: ${getFileType(file.name)} | 大小: ${formatFileSize(file.size)} | ${formatDate(file.uploadTime)}</div>
                        </div>
                    </div>
                    <div class="file-actions">
                        <span class="status-badge ${file.status}">${file.statusText}</span>
                        <button class="detail-btn" onclick="showFileDetail(${index})">
                            <span>ℹ️</span>
                            <span>詳情</span>
                        </button>
                    </div>
                </div>
            `;
        });
        
        fileList.innerHTML = html;
    }
    
    function addFile(file) {
        const fileObj = {
            name: file.name,
            size: file.size,
            type: file.type,
            uploadTime: new Date(),
            status: 'processing',
            statusText: '處理中'
        };
        
        uploadedFiles.unshift(fileObj);
        renderFileList();
        
        // 模擬上傳完成
        setTimeout(() => {
            fileObj.status = 'completed';
            fileObj.statusText = '已完成';
            renderFileList();
        }, 1500);
    }
    
    function setupUploadArea() {
        const area = getEl('uploadArea');
        const input = getEl('fileInput');
        
        if (!area || !input) {
            console.log('Upload area or input not found');
            return;
        }
        
        // 點擊上傳
        area.addEventListener('click', () => {
            input.click();
        });
        
        // 檔案選擇
        input.addEventListener('change', (e) => {
            const files = e.target.files;
            if (files.length > 0) {
                Array.from(files).forEach(file => addFile(file));
                input.value = ''; // 清空輸入
            }
        });
        
        // 拖放
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
                Array.from(files).forEach(file => addFile(file));
            }
        });
    }
    
    // 全域函數供 HTML 調用
    window.showFileDetail = function(index) {
        const file = uploadedFiles[index];
        if (file) {
            alert(`檔案詳情:\n\n名稱: ${file.name}\n大小: ${formatFileSize(file.size)}\n類型: ${file.type}\n上傳時間: ${formatDate(file.uploadTime)}\n狀態: ${file.statusText}`);
        }
    };
    
    // ========== 初始化 ==========
    
    console.log('Setting up event handlers...');
    
    // 搜尋功能
    addEvent('searchBtn', 'click', doSearch);
    addEvent('globalSearch', 'keypress', (e) => {
        if (e.key === 'Enter') {
            doSearch();
        }
    });
    
    // 頁面導航
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const page = item.dataset.page;
            if (page) {
                switchPage(page);
            }
        });
    });
    
    // 上傳區域
    setupUploadArea();
    
    // 上傳按鈕
    addEvent('uploadBtn', 'click', () => {
        const input = getEl('fileInput');
        if (input) {
            input.click();
        }
    });
    
    // 初始化示例檔案（可選）
    // 這些是示例檔案，實際應用中應該從後端載入
    /*
    uploadedFiles = [
        { name: 'test_data.csv', size: 86, type: 'text/csv', uploadTime: new Date('2025-09-07T17:07:43'), status: 'completed', statusText: '已完成' },
        { name: 'test_data.csv', size: 86, type: 'text/csv', uploadTime: new Date('2025-09-07T17:07:43'), status: 'completed', statusText: '已完成' },
        { name: 'test_data.csv', size: 86, type: 'text/csv', uploadTime: new Date('2025-09-07T17:07:43'), status: 'completed', statusText: '已完成' }
    ];
    renderFileList();
    */
    
    // ========== 機構資訊功能 ==========
    
    let orgData = [];
    let filteredOrgData = [];
    let orgPage = 1;
    const orgPerPage = 20;
    let isLoadingOrg = false;
    let searchTerm = '';
    
    // 載入機構資料
    async function loadOrganizations(reset = false) {
        if (isLoadingOrg) return;
        
        if (reset) {
            orgPage = 1;
            filteredOrgData = searchTerm ? 
                orgData.filter(org => searchOrganization(org, searchTerm)) : 
                [...orgData];
        }
        
        const orgResults = getEl('orgResults');
        const orgLoading = getEl('orgLoading');
        
        if (!orgResults || !orgLoading) return;
        
        isLoadingOrg = true;
        orgLoading.style.display = 'block';
        
        try {
            // 如果還沒有載入過資料，從 API 載入
            if (orgData.length === 0) {
                const response = await fetch(`${API_BASE}/contacts/authoritative`);
                if (response.ok) {
                    const data = await response.json();
                    orgData = data.contacts || [];
                    filteredOrgData = searchTerm ? 
                        orgData.filter(org => searchOrganization(org, searchTerm)) : 
                        [...orgData];
                }
            }
            
            // 分頁顯示
            const startIdx = (orgPage - 1) * orgPerPage;
            const endIdx = startIdx + orgPerPage;
            const pageData = filteredOrgData.slice(startIdx, endIdx);
            
            if (orgPage === 1) {
                orgResults.innerHTML = '';
            }
            
            if (pageData.length === 0 && orgPage === 1) {
                orgResults.innerHTML = '<div class="no-results">沒有找到相關的機構資訊</div>';
            } else {
                pageData.forEach(org => {
                    orgResults.appendChild(createOrgCard(org));
                });
            }
            
            orgPage++;
            
        } catch (error) {
            console.error('載入機構資料失敗:', error);
            if (orgPage === 1) {
                orgResults.innerHTML = '<div class="no-results">載入失敗，請稍後再試</div>';
            }
        } finally {
            isLoadingOrg = false;
            orgLoading.style.display = 'none';
        }
    }
    
    // 搜尋機構
    function searchOrganization(org, term) {
        const searchStr = term.toLowerCase();
        const fields = [
            org.name || '',
            org.category || '',
            org.phone || '',
            org.address || '',
            org.services || '',
            org.contact_person || '',
            org.notes || ''
        ];
        
        return fields.some(field => 
            field.toLowerCase().includes(searchStr)
        );
    }
    
    // 建立機構卡片
    function createOrgCard(org) {
        const card = document.createElement('div');
        card.className = 'org-card';
        
        const highlightText = (text) => {
            if (!searchTerm || !text) return text;
            const regex = new RegExp(`(${searchTerm})`, 'gi');
            return text.replace(regex, '<span class="highlight">$1</span>');
        };
        
        card.innerHTML = `
            <div class="org-header">
                <div>
                    <div class="org-name">${highlightText(org.name || '未命名機構')}</div>
                </div>
                <span class="org-category">${highlightText(org.category || '其他')}</span>
            </div>
            <div class="org-info">
                ${org.phone ? `
                    <div class="org-info-item">
                        <span class="org-info-icon">📞</span>
                        <span>${highlightText(org.phone)}</span>
                    </div>
                ` : ''}
                ${org.address ? `
                    <div class="org-info-item">
                        <span class="org-info-icon">📍</span>
                        <span>${highlightText(org.address)}</span>
                    </div>
                ` : ''}
                ${org.contact_person ? `
                    <div class="org-info-item">
                        <span class="org-info-icon">👤</span>
                        <span>聯絡人：${highlightText(org.contact_person)}</span>
                    </div>
                ` : ''}
                ${org.email ? `
                    <div class="org-info-item">
                        <span class="org-info-icon">✉️</span>
                        <span>${highlightText(org.email)}</span>
                    </div>
                ` : ''}
            </div>
            ${org.services ? `
                <div class="org-services">
                    <div class="org-services-title">服務項目</div>
                    <div class="org-services-list">${highlightText(org.services)}</div>
                </div>
            ` : ''}
        `;
        
        return card;
    }
    
    // 設置無限滾動
    function setupInfiniteScroll() {
        const content = document.querySelector('.content');
        if (!content) return;
        
        content.addEventListener('scroll', () => {
            if (currentPage !== 'organization') return;
            
            const scrollHeight = content.scrollHeight;
            const scrollTop = content.scrollTop;
            const clientHeight = content.clientHeight;
            
            // 當滾動到底部附近時載入更多
            if (scrollHeight - scrollTop - clientHeight < 100) {
                if (!isLoadingOrg && filteredOrgData.length > (orgPage - 1) * orgPerPage) {
                    loadOrganizations();
                }
            }
        });
    }
    
    // 機構搜尋功能
    addEvent('orgSearchBtn', 'click', () => {
        const input = getEl('orgSearch');
        if (input) {
            searchTerm = input.value.trim();
            loadOrganizations(true);
        }
    });
    
    addEvent('orgSearch', 'keypress', (e) => {
        if (e.key === 'Enter') {
            const input = getEl('orgSearch');
            if (input) {
                searchTerm = input.value.trim();
                loadOrganizations(true);
            }
        }
    });
    
    addEvent('orgClearBtn', 'click', () => {
        const input = getEl('orgSearch');
        if (input) {
            input.value = '';
            searchTerm = '';
            loadOrganizations(true);
        }
    });
    
    // 修改 switchPage 函數以支援機構頁面
    const originalSwitchPage = switchPage;
    switchPage = function(pageName) {
        originalSwitchPage(pageName);
        
        if (pageName === 'organization') {
            // 首次進入機構頁面時載入資料
            if (orgData.length === 0) {
                loadOrganizations(true);
            }
        }
    };
    
    // 初始化無限滾動
    setupInfiniteScroll();
    
    // 初始化頁面顯示
    switchPage('upload');
    
    console.log('App initialization complete!');
});

// 全域錯誤捕獲
window.addEventListener('error', (e) => {
    console.error('Global error:', e);
    // 不讓錯誤阻止其他功能
    return true;
});