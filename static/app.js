// Manhwa Generator Pro - Complete JavaScript

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const state = {
    currentProject: null,
    currentJobId: null,
    projects: [],
    characters: [],
    panels: [],
    pollInterval: null
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initModals();
    initEventListeners();
    initCharacterCounter();
    loadProjects();
    loadCharacters();
});

// ============================================================================
// INITIALIZATION
// ============================================================================

function initCharacterCounter() {
    const textarea = document.getElementById('chapter-text');
    const counter = document.getElementById('char-count');

    if (textarea && counter) {
        textarea.addEventListener('input', () => {
            counter.textContent = textarea.value.length.toLocaleString();
        });
    }
}

function initEventListeners() {
    // Projects
    document.getElementById('btn-new-project')?.addEventListener('click', () => {
        openModal('modal-new-project');
    });

    document.getElementById('btn-create-project')?.addEventListener('click', createProject);

    // Characters
    document.getElementById('btn-new-character')?.addEventListener('click', () => {
        openModal('modal-new-character');
    });

    document.getElementById('btn-create-character')?.addEventListener('click', createCharacter);

    // Panel Editor
    document.getElementById('btn-analyze-chapter')?.addEventListener('click', analyzeChapter);
    document.getElementById('btn-save-panel')?.addEventListener('click', savePanel);

    // Generate
    document.getElementById('btn-generate')?.addEventListener('click', startGeneration);
    document.getElementById('btn-download')?.addEventListener('click', downloadResults);
    document.getElementById('btn-new-generation')?.addEventListener('click', resetGeneration);

    // Help
    document.getElementById('btn-show-help')?.addEventListener('click', () => {
        openModal('modal-help');
    });
}

// ============================================================================
// TABS
// ============================================================================

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Remove active from all
            tabBtns.forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Add active to clicked
            btn.classList.add('active');
            const tabId = btn.dataset.tab;
            document.getElementById(`tab-${tabId}`).classList.add('active');
        });
    });
}

// ============================================================================
// MODALS
// ============================================================================

function initModals() {
    const modals = document.querySelectorAll('.modal');

    modals.forEach(modal => {
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });

        // Close button
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => closeModal(modal.id));
        }
    });
}

function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// ============================================================================
// EVENT LISTENERS
// ============================================================================

function initEventListeners() {
    // Projects
    document.getElementById('btn-new-project')?.addEventListener('click', () => {
        openModal('modal-new-project');
    });

    document.getElementById('btn-create-project')?.addEventListener('click', createProject);

    // Characters
    document.getElementById('btn-new-character')?.addEventListener('click', () => {
        openModal('modal-new-character');
    });

    document.getElementById('btn-create-character')?.addEventListener('click', createCharacter);

    // Panel Editor
    document.getElementById('btn-analyze-chapter')?.addEventListener('click', analyzeChapter);
    document.getElementById('btn-save-panel')?.addEventListener('click', savePanel);

    // Generate
    document.getElementById('btn-generate')?.addEventListener('click', startGeneration);
    document.getElementById('btn-download')?.addEventListener('click', downloadResults);
}

// ============================================================================
// PROJECTS
// ============================================================================

async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();

        if (data.success) {
            state.projects = data.projects;
            renderProjects();
            updateProjectSelectors();
        }
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

function renderProjects() {
    const container = document.getElementById('projects-list');

    if (state.projects.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📂</div>
                <p>No projects yet. Create your first manhwa!</p>
                <button class="btn btn-primary" onclick="document.getElementById('btn-new-project').click()">
                    Create Project
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = state.projects.map(project => `
        <div class="project-card" onclick="selectProject('${project.project_id}')">
            <div class="project-name">${escapeHtml(project.title)}</div>
            <div class="project-meta">
                ${project.panel_count} panels • Updated ${formatDate(project.updated_at)}
            </div>
            <div class="project-actions" onclick="event.stopPropagation()">
                <button class="btn btn-secondary" onclick="editProject('${project.project_id}')">Edit</button>
                <button class="btn btn-secondary" onclick="deleteProject('${project.project_id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

async function createProject() {
    const name = document.getElementById('new-project-name').value.trim();

    if (!name) {
        alert('Please enter a project name');
        return;
    }

    try {
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: name })
        });

        const data = await response.json();

        if (data.success) {
            closeModal('modal-new-project');
            document.getElementById('new-project-name').value = '';
            await loadProjects();
            showNotification('✅ Project created successfully!');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error creating project:', error);
        alert('Failed to create project');
    }
}

function selectProject(projectId) {
    state.currentProject = projectId;
    showNotification(`✓ Selected project`);
    updateProjectSelectors();
}

async function deleteProject(projectId) {
    if (!confirm('Are you sure you want to delete this project?')) {
        return;
    }

    try {
        const response = await fetch(`/api/projects/${projectId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            await loadProjects();
            showNotification('✅ Project deleted');
        }
    } catch (error) {
        console.error('Error deleting project:', error);
    }
}

function updateProjectSelectors() {
    const selectors = [
        document.getElementById('editor-project-select'),
        document.getElementById('generate-project-select')
    ];

    selectors.forEach(select => {
        if (!select) return;

        select.innerHTML = '<option value="">Select a project...</option>' +
            state.projects.map(p =>
                `<option value="${p.project_id}" ${p.project_id === state.currentProject ? 'selected' : ''}>
                    ${escapeHtml(p.title)}
                </option>`
            ).join('');
    });
}

// ============================================================================
// CHARACTERS
// ============================================================================

async function loadCharacters() {
    try {
        const response = await fetch('/api/characters');
        const data = await response.json();

        if (data.success) {
            state.characters = data.characters;
            renderCharacters();
        }
    } catch (error) {
        console.error('Error loading characters:', error);
    }
}

function renderCharacters() {
    const container = document.getElementById('characters-list');

    if (state.characters.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">👥</div>
                <p>No characters yet. Add your first character!</p>
                <button class="btn btn-primary" onclick="document.getElementById('btn-new-character').click()">
                    Add Character
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = state.characters.map(char => `
        <div class="character-card">
            <div class="character-name">${escapeHtml(char.name)}</div>
            <div class="character-meta">
                ${char.gender} ${char.has_reference ? '• Has reference image' : ''}
            </div>
            <div class="character-actions">
                <button class="btn btn-secondary" onclick="editCharacter('${char.character_id}')">Edit</button>
            </div>
        </div>
    `).join('');
}

async function createCharacter() {
    const charData = {
        name: document.getElementById('char-name').value.trim(),
        gender: document.getElementById('char-gender').value,
        age: document.getElementById('char-age').value.trim(),
        hair_color: document.getElementById('char-hair').value.trim(),
        eye_color: document.getElementById('char-eyes').value.trim(),
        default_outfit: document.getElementById('char-outfit').value.trim()
    };

    if (!charData.name) {
        alert('Please enter a character name');
        return;
    }

    try {
        const response = await fetch('/api/characters', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(charData)
        });

        const data = await response.json();

        if (data.success) {
            // Upload reference image if provided
            const fileInput = document.getElementById('char-reference');
            if (fileInput.files.length > 0) {
                await uploadCharacterReference(data.character.character_id, fileInput.files[0]);
            }

            closeModal('modal-new-character');
            clearCharacterForm();
            await loadCharacters();
            showNotification('✅ Character added successfully!');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error creating character:', error);
        alert('Failed to create character');
    }
}

async function uploadCharacterReference(characterId, file) {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('set_as_face', 'true');

    try {
        await fetch(`/api/characters/${characterId}/reference`, {
            method: 'POST',
            body: formData
        });
    } catch (error) {
        console.error('Error uploading reference:', error);
    }
}

function clearCharacterForm() {
    document.getElementById('char-name').value = '';
    document.getElementById('char-gender').value = '';
    document.getElementById('char-age').value = '';
    document.getElementById('char-hair').value = '';
    document.getElementById('char-eyes').value = '';
    document.getElementById('char-outfit').value = '';
    document.getElementById('char-reference').value = '';
}

// ============================================================================
// PANEL EDITOR
// ============================================================================

async function analyzeChapter() {
    const projectId = document.getElementById('editor-project-select').value;

    if (!projectId) {
        alert('Please select a project first');
        return;
    }

    const project = state.projects.find(p => p.project_id === projectId);
    if (!project || !project.chapter_text) {
        alert('Project has no chapter text. Please add text in the Generate tab first.');
        return;
    }

    try {
        showNotification('🔍 Analyzing chapter...');

        const response = await fetch('/api/panels/preview', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                project_id: projectId,
                chapter_text: project.chapter_text
            })
        });

        const data = await response.json();

        if (data.success) {
            state.panels = data.panels;
            renderPanels();
            showNotification(`✅ Found ${data.panels.length} panels`);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error analyzing chapter:', error);
        alert('Failed to analyze chapter');
    }
}

function renderPanels() {
    const container = document.getElementById('panels-preview');

    if (state.panels.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📄</div>
                <p>Click "Analyze Chapter" to preview panels</p>
            </div>
        `;
        return;
    }

    container.innerHTML = state.panels.map(panel => `
        <div class="panel-item">
            <div class="panel-header">
                <span class="panel-number">Panel ${panel.panel_id}</span>
                <button class="btn btn-secondary" onclick="editPanel(${panel.panel_id})">✏️ Edit</button>
            </div>
            <div class="panel-scene">"${escapeHtml(panel.scene_text.substring(0, 100))}..."</div>
            <div class="panel-prompt">
                <strong>Prompt:</strong> ${escapeHtml(panel.edited_prompt || panel.generated_prompt)}
            </div>
            <div style="display: flex; gap: 12px; font-size: 13px; color: var(--text-secondary);">
                <span>📷 ${panel.camera_angle || 'medium shot'}</span>
                <span>💡 ${panel.lighting || 'natural'}</span>
                <span>😊 ${panel.mood || 'neutral'}</span>
            </div>
        </div>
    `).join('');
}

function editPanel(panelId) {
    const panel = state.panels.find(p => p.panel_id === panelId);
    if (!panel) return;

    document.getElementById('panel-number').textContent = panelId;
    document.getElementById('edit-scene-text').value = panel.scene_text;
    document.getElementById('edit-original-prompt').value = panel.generated_prompt;
    document.getElementById('edit-custom-prompt').value = panel.edited_prompt || '';
    document.getElementById('edit-camera').value = panel.camera_angle || 'medium shot';
    document.getElementById('edit-lighting').value = panel.lighting || 'natural';
    document.getElementById('edit-mood').value = panel.mood || 'neutral';

    openModal('modal-edit-panel');

    // Store for saving
    document.getElementById('btn-save-panel').dataset.panelId = panelId;
}

async function savePanel() {
    const panelId = parseInt(document.getElementById('btn-save-panel').dataset.panelId);
    const projectId = document.getElementById('editor-project-select').value;

    const updates = {
        edited_prompt: document.getElementById('edit-custom-prompt').value.trim() || null,
        camera_angle: document.getElementById('edit-camera').value,
        lighting: document.getElementById('edit-lighting').value,
        mood: document.getElementById('edit-mood').value
    };

    try {
        const response = await fetch(`/api/panels/${projectId}/${panelId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });

        const data = await response.json();

        if (data.success) {
            // Update local state
            const panel = state.panels.find(p => p.panel_id === panelId);
            if (panel) {
                Object.assign(panel, data.panel);
            }

            closeModal('modal-edit-panel');
            renderPanels();
            showNotification('✅ Panel updated!');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error saving panel:', error);
        alert('Failed to save panel');
    }
}

// ============================================================================
// GENERATION
// ============================================================================

async function startGeneration() {
    const chapterText = document.getElementById('chapter-text').value.trim();

    if (!chapterText) {
        alert('Please enter chapter text');
        return;
    }

    const settings = {
        model: document.getElementById('model-select').value,
        style: document.getElementById('style-select').value,
        quality: document.getElementById('quality-select').value,
        max_panels: parseInt(document.getElementById('max-panels').value)
    };

    try {
        // Show progress
        document.getElementById('progress-section').style.display = 'block';
        document.getElementById('results-section').style.display = 'none';

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                chapter_text: chapterText,
                ...settings
            })
        });

        const data = await response.json();

        if (data.success) {
            state.currentJobId = data.job_id;
            startPolling(data.job_id);
        } else {
            alert('Error: ' + data.error);
            document.getElementById('progress-section').style.display = 'none';
        }
    } catch (error) {
        console.error('Error starting generation:', error);
        alert('Failed to start generation');
        document.getElementById('progress-section').style.display = 'none';
    }
}

function startPolling(jobId) {
    if (state.pollInterval) {
        clearInterval(state.pollInterval);
    }

    state.pollInterval = setInterval(() => checkProgress(jobId), 2000);
}

async function checkProgress(jobId) {
    try {
        const response = await fetch(`/api/progress/${jobId}`);
        const data = await response.json();

        if (data.status === 'completed') {
            clearInterval(state.pollInterval);
            showResults(jobId);
        } else if (data.status === 'failed') {
            clearInterval(state.pollInterval);
            alert('Generation failed: ' + data.error);
            document.getElementById('progress-section').style.display = 'none';
        } else {
            // Update progress
            const percent = Math.round(data.progress);
            document.getElementById('progress-fill').style.width = percent + '%';
            document.getElementById('progress-text').textContent = percent + '%';
            document.getElementById('progress-status').textContent = data.message || 'Generating...';
        }
    } catch (error) {
        console.error('Error checking progress:', error);
    }
}

function showResults(jobId) {
    document.getElementById('progress-section').style.display = 'none';
    document.getElementById('results-section').style.display = 'block';

    // You can add result rendering here
    showNotification('✅ Generation complete!');
}

async function downloadResults() {
    if (state.currentJobId) {
        window.location.href = `/api/download/${state.currentJobId}`;
    }
}

// ============================================================================
// UTILITIES
// ============================================================================

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
}

function showNotification(message, type = 'info') {
    // Create toast container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    // Add to container
    container.appendChild(toast);

    // Remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function resetGeneration() {
    document.getElementById('results-section').style.display = 'none';
    document.getElementById('chapter-text').value = '';
    document.getElementById('char-count').textContent = '0';
    showNotification('Ready for new generation', 'success');
}

// Add slideOut animation to CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

