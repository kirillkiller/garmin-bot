// API Base URL
const API_BASE = '';

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update content
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        
        // Load tab content
        if (tabName === 'websites') loadWebsites();
        if (tabName === 'youtube') loadYouTube();
        if (tabName === 'prompt') loadPrompt();
        if (tabName === 'reports') loadReports();
        if (tabName === 'reports-list') loadReportsList();
        if (tabName === 'emails') loadEmails();
        if (tabName === 'stats') loadStats();
    });
});

// Load initial data
loadStatus();
loadWebsites();

// Status
async function loadStatus() {
    try {
        const res = await fetch(`${API_BASE}/api/status`);
        const data = await res.json();
        if (data.success) {
            document.getElementById('status').textContent = 
                `✅ ${data.stats.total_contents} obsahů | ${data.stats.relevant_contents} relevantních`;
            document.getElementById('status').className = 'success';
        }
    } catch (e) {
        document.getElementById('status').textContent = '❌ Chyba';
        document.getElementById('status').className = 'error';
    }
}

// Websites
async function loadWebsites() {
    try {
        const res = await fetch(`${API_BASE}/api/websites`);
        const data = await res.json();
        if (data.success) {
            const list = document.getElementById('websitesList');
            list.innerHTML = '';
            
            data.websites.forEach((site, index) => {
                const item = document.createElement('div');
                item.className = 'list-item';
                item.innerHTML = `
                    <div>
                        <h3>${site.name}</h3>
                        <p>${site.url}</p>
                    </div>
                    <button class="btn btn-danger" onclick="deleteWebsite(${index})">🗑️ Smazat</button>
                `;
                list.appendChild(item);
            });
        }
    } catch (e) {
        console.error('Chyba při načítání webů:', e);
    }
}

async function deleteWebsite(index) {
    if (!confirm('Opravdu chceš smazat tento web?')) return;
    
    try {
        const res = await fetch(`${API_BASE}/api/websites/${index}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            loadWebsites();
            showMessage('Web smazán', 'success');
        } else {
            showMessage('Chyba: ' + data.error, 'error');
        }
    } catch (e) {
        showMessage('Chyba při mazání', 'error');
    }
}

// Add website modal
const modal = document.getElementById('addWebsiteModal');
const addBtn = document.getElementById('addWebsiteBtn');
const closeBtn = document.querySelector('.close');

addBtn.onclick = () => modal.style.display = 'block';
closeBtn.onclick = () => modal.style.display = 'none';
window.onclick = (e) => {
    if (e.target === modal) modal.style.display = 'none';
};

document.getElementById('addWebsiteForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const data = {
        url: document.getElementById('websiteUrl').value,
        name: document.getElementById('websiteName').value || document.getElementById('websiteUrl').value,
        scroll_depth: parseInt(document.getElementById('scrollDepth').value),
        wait_time: parseFloat(document.getElementById('waitTime').value),
        ai_prompt: document.getElementById('websitePrompt').value
    };
    
    try {
        const res = await fetch(`${API_BASE}/api/websites`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await res.json();
        if (result.success) {
            modal.style.display = 'none';
            loadWebsites();
            showMessage('Web přidán', 'success');
            document.getElementById('addWebsiteForm').reset();
        } else {
            showMessage('Chyba: ' + result.error, 'error');
        }
    } catch (e) {
        showMessage('Chyba při přidávání', 'error');
    }
});

// Prompt
async function loadPrompt() {
    try {
        const res = await fetch(`${API_BASE}/api/prompt`);
        const data = await res.json();
        if (data.success) {
            document.getElementById('promptText').value = data.prompt;
        }
    } catch (e) {
        console.error('Chyba při načítání promptu:', e);
    }
}

document.getElementById('savePromptBtn').addEventListener('click', async () => {
    const prompt = document.getElementById('promptText').value;
    
    try {
        const res = await fetch(`${API_BASE}/api/prompt`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        
        const data = await res.json();
        if (data.success) {
            showMessage('Prompt uložen', 'success');
        } else {
            showMessage('Chyba: ' + data.error, 'error');
        }
    } catch (e) {
        showMessage('Chyba při ukládání', 'error');
    }
});

// Reports
async function loadReports() {
    // Generate month options
    const select = document.getElementById('monthSelect');
    select.innerHTML = '<option value="">Poslední měsíc</option>';
    const now = new Date();
    for (let i = 0; i < 12; i++) {
        const date = new Date(now.getFullYear(), now.getMonth() - i, 1);
        const monthStr = date.toISOString().substring(0, 7);
        const option = document.createElement('option');
        option.value = monthStr;
        option.textContent = date.toLocaleDateString('cs-CZ', { year: 'numeric', month: 'long' });
        select.appendChild(option);
    }
}

document.getElementById('generateReportBtn').addEventListener('click', async () => {
    const month = document.getElementById('monthSelect').value;
    const content = document.getElementById('reportContent');
    content.innerHTML = '<p>⏳ Generuji report s právním shrnutím... (může trvat 1-2 minuty)</p>';
    
    try {
        const res = await fetch(`${API_BASE}/api/reports/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ month: month || '' })
        });
        
        const data = await res.json();
        if (data.success) {
            const report = data.report;
            content.innerHTML = `
                <h3>📊 Report pro ${report.month}</h3>
                <p><strong>Analyzováno ${report.total_contents} obsahů | ${report.relevant_contents || 0} relevantních</strong></p>
                
                <div class="legal-summary">
                    <h4>⭐ HIGHLIGHTS - Pro podnikatele a investory</h4>
                    <div class="summary-content">${formatSummary(report.highlights || report.legal_summary || 'Generuji highlights...')}</div>
                </div>
                
                ${report.top_findings && report.top_findings.length > 0 ? `
                <div class="top-findings">
                    <h4>🔍 Klíčové závěry (${report.top_findings.length})</h4>
                    ${report.top_findings.map(f => `
                        <div class="finding-item">
                            <h5>${f.title || 'Bez nadpisu'}</h5>
                            <p><strong>Kategorie:</strong> ${f.category || 'N/A'} | <strong>Relevance:</strong> ${f.relevance.toFixed(2)}</p>
                            <p>${f.summary || 'N/A'}</p>
                            ${f.key_points && f.key_points.length > 0 ? `<ul>${f.key_points.map(kp => `<li>${kp}</li>`).join('')}</ul>` : ''}
                            <p><a href="${f.url}" target="_blank">📄 Přečíst více</a></p>
                        </div>
                    `).join('')}
                </div>
                ` : ''}
                
                <div class="all-documents">
                    <h4>📚 Všechny analyzované dokumenty (${report.all_contents.length})</h4>
                    <p style="color: #86868B; margin-bottom: 20px;">Kompletní seznam všech dokumentů, které byly analyzovány v tomto měsíci</p>
                    ${report.all_contents.map((c, idx) => `
                        <div class="document-item">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <div style="flex: 1;">
                                    <h5>${idx + 1}. ${c.title || 'Bez nadpisu'}</h5>
                                    <p><strong>Kategorie:</strong> ${c.analysis?.category || 'N/A'} | 
                                       <strong>Relevance:</strong> ${(c.analysis?.relevance_score || 0).toFixed(2)} | 
                                       <strong>Relevantní:</strong> ${c.analysis?.is_relevant ? '✅ Ano' : '❌ Ne'}</p>
                                    <p>${c.analysis?.summary || 'N/A'}</p>
                                    ${c.analysis?.key_points && c.analysis.key_points.length > 0 ? `
                                        <details style="margin-top: 10px;">
                                            <summary style="cursor: pointer; color: var(--apple-blue);">Klíčové body</summary>
                                            <ul style="margin-top: 10px; padding-left: 20px;">
                                                ${c.analysis.key_points.map(kp => `<li>${kp}</li>`).join('')}
                                            </ul>
                                        </details>
                                    ` : ''}
                                </div>
                            </div>
                            <p style="margin-top: 10px;"><a href="${c.url}" target="_blank" style="color: var(--apple-blue);">🔗 ${c.url}</a></p>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            content.innerHTML = `<p class="error">❌ Chyba: ${data.error}</p>`;
        }
    } catch (e) {
        content.innerHTML = `<p class="error">❌ Chyba při generování reportu: ${e.message}</p>`;
    }
});

function formatSummary(text) {
    // Formátování textu s odstavci
    return text.split('\n').map(line => {
        if (line.trim().match(/^\d+\./)) {
            return `<h5>${line}</h5>`;
        } else if (line.trim().startsWith('-')) {
            return `<li>${line.substring(1).trim()}</li>`;
        } else if (line.trim()) {
            return `<p>${line}</p>`;
        }
        return '';
    }).join('');
}

// Reports List
async function loadReportsList() {
    try {
        const res = await fetch(`${API_BASE}/api/reports/list`);
        const data = await res.json();
        if (data.success) {
            const list = document.getElementById('reportsList');
            if (data.reports.length === 0) {
                list.innerHTML = '<p>Žádné reporty zatím nebyly vygenerovány.</p>';
                return;
            }
            
            list.innerHTML = data.reports.map(r => `
                <div class="report-list-item" onclick="showReportDetail('${r.month}')">
                    <h3>📊 Report - ${r.month}</h3>
                    <p>${r.summary_preview}</p>
                    <small>Vytvořeno: ${new Date(r.created_at).toLocaleDateString('cs-CZ')}</small>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('Chyba při načítání reportů:', e);
    }
}

async function showReportDetail(month) {
    try {
        const res = await fetch(`${API_BASE}/api/reports/${month}`);
        const data = await res.json();
        if (data.success) {
            const report = data.report;
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 1000px; max-height: 90vh; overflow-y: auto;">
                    <span class="close" onclick="this.parentElement.parentElement.remove()">&times;</span>
                    <h2>📊 Report - ${report.month}</h2>
                    <p style="color: #86868B; margin-bottom: 20px;">Analyzováno ${report.total_contents} obsahů | ${report.relevant_contents || 0} relevantních</p>
                    
                    <div class="legal-summary">
                        <h4>⭐ HIGHLIGHTS - Pro podnikatele a investory</h4>
                        <div class="summary-content">${formatSummary(report.highlights || report.legal_summary || 'N/A')}</div>
                    </div>
                    
                    ${report.top_findings && report.top_findings.length > 0 ? `
                    <div class="top-findings">
                        <h4>🔍 Klíčové závěry</h4>
                        ${report.top_findings.map(f => `
                            <div class="finding-item">
                                <h5>${f.title || 'N/A'}</h5>
                                <p><strong>Kategorie:</strong> ${f.category || 'N/A'} | <strong>Relevance:</strong> ${f.relevance.toFixed(2)}</p>
                                <p>${f.summary || 'N/A'}</p>
                                <p><a href="${f.url}" target="_blank">📄 Přečíst více</a></p>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                    
                    <div class="all-documents">
                        <h4>📚 Všechny analyzované dokumenty (${report.all_contents.length})</h4>
                        ${report.all_contents.map((c, idx) => `
                            <div class="document-item">
                                <h5>${idx + 1}. ${c.title || 'Bez nadpisu'}</h5>
                                <p><strong>Kategorie:</strong> ${c.analysis?.category || 'N/A'} | 
                                   <strong>Relevance:</strong> ${(c.analysis?.relevance_score || 0).toFixed(2)} | 
                                   <strong>Relevantní:</strong> ${c.analysis?.is_relevant ? '✅' : '❌'}</p>
                                <p>${c.analysis?.summary || 'N/A'}</p>
                                <p><a href="${c.url}" target="_blank">🔗 ${c.url}</a></p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            modal.querySelector('.close').onclick = () => modal.remove();
        }
    } catch (e) {
        alert('Chyba při načítání reportu: ' + e.message);
    }
}

// Emails
async function loadEmails() {
    try {
        const res = await fetch(`${API_BASE}/api/emails`);
        const data = await res.json();
        if (data.success) {
            const list = document.getElementById('emailsList');
            list.innerHTML = '';
            
            if (data.emails.length === 0) {
                list.innerHTML = '<p>Žádné emaily zatím nejsou nastaveny.</p>';
                return;
            }
            
            data.emails.forEach(email => {
                const item = document.createElement('div');
                item.className = 'list-item';
                item.innerHTML = `
                    <div>
                        <h3>${email.email}</h3>
                        <p>Začátek: ${email.start_date} | Perioda: ${email.period_days} dní</p>
                        <p>Status: ${email.is_active ? '✅ Aktivní' : '❌ Neaktivní'}</p>
                    </div>
                    <button class="btn btn-danger" onclick="deleteEmail(${email.id})">🗑️ Smazat</button>
                `;
                list.appendChild(item);
            });
        }
    } catch (e) {
        console.error('Chyba při načítání emailů:', e);
    }
}

async function deleteEmail(id) {
    if (!confirm('Opravdu chceš smazat tento email?')) return;
    
    try {
        const res = await fetch(`${API_BASE}/api/emails/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            loadEmails();
            showMessage('Email smazán', 'success');
        } else {
            showMessage('Chyba: ' + data.error, 'error');
        }
    } catch (e) {
        showMessage('Chyba při mazání', 'error');
    }
}

// Add email modal
const addEmailModal = document.getElementById('addEmailModal');
const addEmailBtn = document.getElementById('addEmailBtn');
if (addEmailBtn && addEmailModal) {
    addEmailBtn.onclick = () => {
        document.getElementById('emailStartDate').value = new Date().toISOString().substring(0, 10);
        addEmailModal.style.display = 'block';
    };
    
    addEmailModal.querySelector('.close').onclick = () => addEmailModal.style.display = 'none';
    window.onclick = (e) => {
        if (e.target === addEmailModal) addEmailModal.style.display = 'none';
    };
    
    document.getElementById('addEmailForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const data = {
            email: document.getElementById('emailAddress').value,
            start_date: document.getElementById('emailStartDate').value,
            period_days: parseInt(document.getElementById('emailPeriod').value) || 30
        };
        
        try {
            const res = await fetch(`${API_BASE}/api/emails`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await res.json();
            if (result.success) {
                addEmailModal.style.display = 'none';
                loadEmails();
                showMessage('Email přidán a report odeslán', 'success');
                document.getElementById('addEmailForm').reset();
            } else {
                showMessage('Chyba: ' + result.error, 'error');
            }
        } catch (e) {
            showMessage('Chyba při přidávání emailu', 'error');
        }
    });
}

// Stats
async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/api/status`);
        const data = await res.json();
        if (data.success) {
            const stats = data.stats;
            const content = document.getElementById('statsContent');
            content.innerHTML = `
                <div class="stat-card">
                    <h3>${stats.total_contents}</h3>
                    <p>Celkem obsahů</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.relevant_contents}</h3>
                    <p>Relevantních</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.total_analyses}</h3>
                    <p>Analýz</p>
                </div>
                <div class="stat-card">
                    <h3>${stats.sent_reports}</h3>
                    <p>Odeslaných reportů</p>
                </div>
            `;
        }
    } catch (e) {
        console.error('Chyba při načítání statistik:', e);
    }
}

// Run monitoring
document.getElementById('runMonitoring').addEventListener('click', async () => {
    const btn = document.getElementById('runMonitoring');
    btn.disabled = true;
    btn.textContent = '⏳ Probíhá...';
    
    try {
        const res = await fetch(`${API_BASE}/api/monitor/run`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            showMessage(`Monitoring dokončen: ${data.relevant_contents} relevantních obsahů`, 'success');
            loadStatus();
            loadStats();
        } else {
            showMessage('Chyba: ' + data.error, 'error');
        }
    } catch (e) {
        showMessage('Chyba při spuštění monitoringu', 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = '▶️ Spustit Monitoring';
    }
});

// Helper function
function showMessage(message, type) {
    const msg = document.createElement('div');
    msg.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#4CAF50' : '#f44336'};
        color: white;
        border-radius: 4px;
        z-index: 10000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    `;
    msg.textContent = message;
    document.body.appendChild(msg);
    setTimeout(() => msg.remove(), 3000);
}

// YouTube functions
async function loadYouTube() {
    await loadYouTubeChannels();
    await loadYouTubeStats();
    await loadYouTubeVideos();
}

async function loadYouTubeChannels() {
    try {
        const res = await fetch(`${API_BASE}/api/youtube/channels`);
        const data = await res.json();
        if (data.success) {
            const select = document.getElementById('youtubeChannelSelect');
            select.innerHTML = '<option value="">Všechny kanály</option>';
            data.channels.forEach(channel => {
                const option = document.createElement('option');
                option.value = channel.channel_url;
                option.textContent = channel.channel_name || channel.channel_url;
                select.appendChild(option);
            });
        }
    } catch (e) {
        console.error('Chyba při načítání kanálů:', e);
    }
}

async function loadYouTubeStats() {
    try {
        const res = await fetch(`${API_BASE}/api/youtube/stats`);
        const data = await res.json();
        if (data.success) {
            const stats = data.stats;
            const statsDiv = document.getElementById('youtubeStats');
            statsDiv.innerHTML = `
                <div class="stats-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    <div class="stat-card" style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: bold; color: #007AFF;">${stats.total_videos}</div>
                        <div style="color: #666; margin-top: 5px;">Celkem videí</div>
                    </div>
                    <div class="stat-card" style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: bold; color: #34C759;">${stats.videos_with_transcripts}</div>
                        <div style="color: #666; margin-top: 5px;">S transkriptem</div>
                    </div>
                    <div class="stat-card" style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: bold; color: #FF9500;">${stats.videos_without_transcripts}</div>
                        <div style="color: #666; margin-top: 5px;">Bez transkriptu</div>
                    </div>
                    <div class="stat-card" style="background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <div style="font-size: 24px; font-weight: bold; color: #5856D6;">${stats.active_channels}</div>
                        <div style="color: #666; margin-top: 5px;">Aktivní kanály</div>
                    </div>
                </div>
            `;
        }
    } catch (e) {
        console.error('Chyba při načítání statistik:', e);
    }
}

async function loadYouTubeVideos() {
    try {
        const channelUrl = document.getElementById('youtubeChannelSelect').value;
        const filter = document.getElementById('youtubeFilterSelect').value;
        
        let url = `${API_BASE}/api/youtube/videos?limit=1000`;
        if (channelUrl) url += `&channel_url=${encodeURIComponent(channelUrl)}`;
        if (filter === 'with_transcript') url += `&with_transcript=true`;
        if (filter === 'without_transcript') url += `&with_transcript=false`;
        
        const res = await fetch(url);
        const data = await res.json();
        
        if (data.success) {
            const videosList = document.getElementById('youtubeVideosList');
            videosList.innerHTML = '';
            
            if (data.videos.length === 0) {
                videosList.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">Žádná videa nenalezena</p>';
                return;
            }
            
            data.videos.forEach(video => {
                const hasTranscript = video.transcript_text && video.transcript_text.trim() !== '';
                const videoCard = document.createElement('div');
                videoCard.className = 'video-card';
                videoCard.style.cssText = `
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    margin-bottom: 15px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    cursor: pointer;
                    transition: transform 0.2s, box-shadow 0.2s;
                `;
                videoCard.onmouseenter = () => {
                    videoCard.style.transform = 'translateY(-2px)';
                    videoCard.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                };
                videoCard.onmouseleave = () => {
                    videoCard.style.transform = 'translateY(0)';
                    videoCard.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                };
                
                videoCard.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <h3 style="margin: 0 0 10px 0; font-size: 18px; color: #1D1D1F;">${escapeHtml(video.video_title)}</h3>
                            <div style="color: #666; font-size: 14px; margin-bottom: 10px;">
                                ${video.published_at ? `📅 ${formatDate(video.published_at)}` : ''}
                                ${video.transcript_language ? ` | 🌐 ${video.transcript_language}` : ''}
                            </div>
                            <a href="${video.video_url}" target="_blank" style="color: #007AFF; text-decoration: none; font-size: 14px;">
                                🔗 Otevřít video
                            </a>
                        </div>
                        <div style="margin-left: 20px;">
                            ${hasTranscript ? 
                                `<button class="btn btn-primary" onclick="showTranscript('${video.video_id}')" style="white-space: nowrap;">
                                    📝 Zobrazit transkript
                                </button>` :
                                `<span style="color: #FF9500; font-size: 14px;">⚠️ Bez transkriptu</span>`
                            }
                        </div>
                    </div>
                `;
                videosList.appendChild(videoCard);
            });
        }
    } catch (e) {
        console.error('Chyba při načítání videí:', e);
        showMessage('Chyba při načítání videí', 'error');
    }
}

// Make showTranscript globally available
window.showTranscript = async function(videoId) {
    try {
        const res = await fetch(`${API_BASE}/api/youtube/videos/${videoId}/transcript`);
        const data = await res.json();
        
        if (data.success && data.video) {
            const modal = document.getElementById('transcriptModal');
            document.getElementById('transcriptTitle').textContent = data.video.video_title;
            document.getElementById('transcriptLanguage').textContent = `Jazyk: ${data.video.transcript_language || 'N/A'}`;
            document.getElementById('transcriptDate').textContent = data.video.transcript_downloaded_at ? 
                ` | Staženo: ${formatDate(data.video.transcript_downloaded_at)}` : '';
            document.getElementById('transcriptVideoUrl').href = data.video.video_url;
            document.getElementById('transcriptVideoUrl').textContent = '🔗 Otevřít video na YouTube';
            
            const transcriptContent = document.getElementById('transcriptContent');
            if (data.video.transcript_text) {
                transcriptContent.innerHTML = `<pre style="white-space: pre-wrap; word-wrap: break-word; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif; line-height: 1.6; max-height: 60vh; overflow-y: auto; padding: 20px; background: #F5F5F7; border-radius: 8px;">${escapeHtml(data.video.transcript_text)}</pre>`;
            } else {
                transcriptContent.innerHTML = '<p style="text-align: center; color: #666; padding: 40px;">Transkript není dostupný</p>';
            }
            
            modal.style.display = 'block';
        } else {
            showMessage('Transkript nenalezen', 'error');
        }
    } catch (e) {
        console.error('Chyba při načítání transkriptu:', e);
        showMessage('Chyba při načítání transkriptu', 'error');
    }
}

// Helper functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return '';
    try {
        let date;
        // YouTube published_at může být ve formátu YYYYMMDD
        if (dateString.length === 8 && /^\d{8}$/.test(dateString)) {
            const year = dateString.substring(0, 4);
            const month = dateString.substring(4, 6);
            const day = dateString.substring(6, 8);
            date = new Date(`${year}-${month}-${day}`);
        } else {
            date = new Date(dateString);
        }
        return date.toLocaleDateString('cs-CZ', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric'
        });
    } catch (e) {
        return dateString;
    }
}

// YouTube event listeners
document.getElementById('refreshYoutubeBtn')?.addEventListener('click', loadYouTube);
document.getElementById('youtubeChannelSelect')?.addEventListener('change', loadYouTubeVideos);
document.getElementById('youtubeFilterSelect')?.addEventListener('change', loadYouTubeVideos);

// Modal close
document.querySelectorAll('.modal .close').forEach(closeBtn => {
    closeBtn.addEventListener('click', () => {
        closeBtn.closest('.modal').style.display = 'none';
    });
});

// Copy transcript button
document.getElementById('copyTranscriptBtn')?.addEventListener('click', () => {
    const transcriptText = document.getElementById('transcriptContent').querySelector('pre')?.textContent;
    if (transcriptText) {
        navigator.clipboard.writeText(transcriptText).then(() => {
            showMessage('Transkript zkopírován do schránky', 'success');
        });
    }
});

// Close modal on outside click
window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

