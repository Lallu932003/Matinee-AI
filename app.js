// --- Global Logic & Cursor ---
const cursor = document.getElementById('cursor');
if (cursor) {
    document.addEventListener('mousemove', (e) => {
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
    });

    document.addEventListener('mousedown', () => cursor.style.transform = 'scale(0.8)');
    document.addEventListener('mouseup', () => cursor.style.transform = 'scale(1)');
}

function addCursorHover() {
    if (!cursor) return;
    document.querySelectorAll('button, a, select, input, textarea, .nav-tab, .sub-tab, .action-btn').forEach(el => {
        el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
        el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
    });
}

// --- Scroll Reveal ---
function handleScroll() {
    const reveals = document.querySelectorAll('.reveal');
    reveals.forEach(el => {
        const windowHeight = window.innerHeight;
        const revealTop = el.getBoundingClientRect().top;
        if (revealTop < windowHeight - 150) {
            el.classList.add('active');
        }
    });
}
window.addEventListener('scroll', handleScroll);

// --- Navigation ---
function scrollToId(id) {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}

function showSubView(subId) {
    const listSub = document.getElementById('management-list-subview');
    const createSub = document.getElementById('management-create-subview');
    
    if (listSub && createSub) {
        listSub.classList.add('hidden');
        createSub.classList.add('hidden');
        document.getElementById(`management-${subId}-subview`).classList.remove('hidden');

        document.querySelectorAll('.sub-tab').forEach(t => t.classList.remove('active'));
        const activeTab = document.getElementById(`sub-tab-${subId}`);
        if (activeTab) activeTab.classList.add('active');
    }
}

// --- Persona Management Logic ---
async function generateGroup() {
    const nameInput = document.getElementById('group-name');
    const ageInput = document.getElementById('group-age');
    const genderInput = document.getElementById('group-gender');
    const countInput = document.getElementById('group-count');
    const detailsInput = document.getElementById('group-details');

    if (!nameInput) return;

    const name = nameInput.value.trim();
    const ageRange = ageInput.value;
    const gender = genderInput.value;
    const count = parseInt(countInput.value);
    const details = detailsInput.value.trim();

    if (!name) { alert("Please provide a group name."); return; }

    const btn = document.getElementById('gen-group-btn');
    btn.disabled = true;
    btn.innerText = `GENERATING ${count} PERSONAS...`;

    try {
        const response = await fetch('http://127.0.0.1:8000/personas/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                group_name: name,
                age_range: ageRange,
                gender: gender,
                count: count,
                additional_details: details
            })
        });

        if (!response.ok) throw new Error("Generation failed.");
        const data = await response.json();

        const newGroup = {
            id: Date.now().toString(),
            name: name,
            isPredefined: false,
            personas: data.personas
        };

        personaGroups.push(newGroup);
        saveState();
        renderGroupList();
        
        showSubView('list');
        alert(`Successfully generated ${count} personas for ${name}`);
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        btn.disabled = false;
        btn.innerText = "INITIALIZE GENERATION";
    }
}

function renderGroupList() {
    const list = document.getElementById('management-list-subview');
    if (!list) return;
    
    list.innerHTML = '';

    personaGroups.forEach(group => {
        const card = document.createElement('div');
        card.className = 'glass-panel rounded-3xl p-6 space-y-4 animate-fade-in relative overflow-hidden group';
        card.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="font-black text-xl uppercase tracking-tighter">${group.name}</h3>
                    <p class="text-xs text-slate-500 font-bold uppercase tracking-widest">${group.personas.length} AUDIENCES</p>
                </div>
                ${!group.isPredefined ? `
                    <button onclick="deleteGroup('${group.id}')" class="text-slate-600 hover:text-red-500 transition-colors">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                ` : '<span class="text-[10px] bg-white/10 px-2 py-1 rounded font-black tracking-widest opacity-50">CORE</span>'}
            </div>
            
            <div class="grid grid-cols-2 gap-2">
                ${group.personas.slice(0, 4).map(p => `
                    <div class="bg-white/5 rounded-lg p-2">
                        <p class="text-[10px] font-black text-red-500 truncate">${p.name}</p>
                        <p class="text-[8px] text-slate-400 capitalize">${p.job}</p>
                    </div>
                `).join('')}
            </div>

            <button onclick="viewGroupDetails('${group.id}')" class="w-full py-3 bg-white/5 hover:bg-white/10 rounded-xl text-[10px] font-black uppercase tracking-[0.3em] transition-all">
                Access Vault Key
            </button>
        `;
        list.appendChild(card);
    });
    addCursorHover();
}

function viewGroupDetails(groupId) {
    const group = personaGroups.find(g => g.id === groupId);
    if (!group) return;
    
    const detailsHtml = `
        <div id="vault-overlay" class="fixed inset-0 bg-black/90 backdrop-blur-xl z-[100] p-8 overflow-y-auto animate-fade-in">
            <div class="max-w-6xl mx-auto space-y-12">
                <div class="flex justify-between items-center">
                    <div>
                        <span class="text-xs font-black tracking-widest text-red-500 uppercase">Vault Record</span>
                        <h2 class="text-5xl font-black uppercase italic">${group.name}</h2>
                    </div>
                    <button onclick="document.getElementById('vault-overlay').remove()" class="p-4 bg-white/10 rounded-full hover:bg-white/20 transition-all">
                        <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    ${group.personas.map(p => `
                        <div class="glass-panel rounded-3xl p-8 space-y-4 border-l-4 border-l-red-500">
                             <div class="flex justify-between items-center">
                                <h4 class="text-xl font-black text-red-500">${p.name}</h4>
                                <div class="flex gap-2">
                                    <button onclick="openEditModal('${group.id}', '${p.name}')" class="action-btn text-red-500 hover:text-red-400">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                                    </button>
                                    <button onclick="deletePersona('${group.id}', '${p.name}')" class="action-btn text-red-500 hover:text-red-400">
                                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                    </button>
                                </div>
                             </div>
                             <div class="space-y-3">
                                <div class="flex justify-between text-[10px] uppercase tracking-widest font-bold">
                                    <span class="text-slate-500">Age / Gender</span>
                                    <span class="text-white">${p.age}y / ${p.gender}</span>
                                </div>
                                <div class="flex justify-between text-[10px] uppercase tracking-widest font-bold">
                                    <span class="text-slate-500">Occupation</span>
                                    <span class="text-white">${p.job}</span>
                                </div>
                                <div class="flex justify-between text-[10px] uppercase tracking-widest font-bold">
                                    <span class="text-slate-500">Origin</span>
                                    <span class="text-white">${p.location}</span>
                                </div>
                                <div class="pt-4 border-t border-white/5">
                                    <p class="text-xs leading-relaxed text-slate-300 italic">"${p.description}"</p>
                                </div>
                             </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', detailsHtml);
    addCursorHover();
}

// --- Lifecycle ---
async function runEvaluations() {
    const scriptInput = document.getElementById('script-content');
    const groupSelect = document.getElementById('evaluation-group-select');
    
    if (!scriptInput || !groupSelect) return;

    const script = scriptInput.value.trim();
    const groupId = groupSelect.value;
    
    if (!script) { alert("Please enter script content."); return; }
    
    const group = personaGroups.find(g => g.id === groupId);
    if (!group) return;

    const loader = document.getElementById('loading-container');
    const dashboard = document.getElementById('dashboard-container');
    const runBtn = document.getElementById('run-btn');

    if (dashboard) dashboard.classList.add('hidden');
    if (loader) loader.classList.remove('hidden');
    if (runBtn) runBtn.disabled = true;

    try {
        const response = await fetch('http://127.0.0.1:8000/evaluate/group', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                personas: group.personas,
                content: script
            })
        });

        if (!response.ok) throw new Error("Evaluation failed.");
        const results = await response.json();
        
        renderDashboard(results);
    } catch (err) {
        alert("Error: " + err.message);
    } finally {
        if (loader) loader.classList.add('hidden');
        if (runBtn) runBtn.disabled = false;
    }
}

function renderDashboard(results) {
    const dashboard = document.getElementById('dashboard-container');
    if (!dashboard) return;
    dashboard.classList.remove('hidden');

    const tableBody = document.getElementById('metrics-table-body');
    const feedbackContainer = document.getElementById('feedback-container');
    if (tableBody) tableBody.innerHTML = '';
    if (feedbackContainer) feedbackContainer.innerHTML = '';

    const chartData = {
        labels: [],
        overall: [],
        hook: [],
        resonance: [],
        binge: [],
        relatability: []
    };

    results.forEach(res => {
        const evaluation = res.evaluation;
        chartData.labels.push(res.persona_name);
        chartData.overall.push(evaluation.overall_rating);
        chartData.hook.push(evaluation.attention_hook);
        chartData.resonance.push(evaluation.emotional_resonance);
        chartData.binge.push(evaluation.binge_ability);
        chartData.relatability.push(evaluation.relatability_score);

        // Table
        if (tableBody) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="py-4 font-bold text-red-500">${res.persona_name}</td>
                <td class="py-4 text-center font-black">${evaluation.overall_rating}</td>
                <td class="py-4 text-center font-bold text-slate-400">${evaluation.attention_hook}</td>
                <td class="py-4 text-center font-bold text-slate-400">${evaluation.emotional_resonance}</td>
                <td class="py-4 text-center font-bold text-slate-400">${evaluation.binge_ability}</td>
            `;
            tableBody.appendChild(row);
        }

        // Feedback Card
        if (feedbackContainer) {
            const card = document.createElement('div');
            card.className = "glass-panel rounded-3xl p-8 relative overflow-hidden group";
            card.innerHTML = `
                <div class="absolute top-0 left-0 w-2 h-full bg-gradient-to-b from-red-600 to-orange-500"></div>
                <div class="space-y-4">
                    <h4 class="font-black text-xl uppercase tracking-tighter">${res.persona_name}</h4>
                    <div>
                        <span class="text-[10px] font-black tracking-widest text-[#ff0055] uppercase block mb-1">Alienation Risk</span>
                        <p class="text-sm text-slate-400 leading-tight">${evaluation.controversy_risk}</p>
                    </div>
                    <div class="pt-4 border-t border-white/5">
                        <span class="text-[10px] font-black tracking-widest text-red-500 uppercase block mb-2">Neural Verdict</span>
                        <blockquote class="text-slate-200 italic font-medium leading-relaxed">"${evaluation.feedback}"</blockquote>
                    </div>
                </div>
            `;
            feedbackContainer.appendChild(card);
        }
    });

    renderChart(chartData);
    addCursorHover();
}

function renderChart(data) {
    const canvas = document.getElementById('resultsChart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (chartInstance) chartInstance.destroy();

    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(255, 0, 60, 0.2)');
    gradient.addColorStop(1, 'rgba(255, 0, 60, 0)');

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Overall Rating',
                    data: data.overall,
                    borderColor: '#ff003c',
                    borderWidth: 4,
                    tension: 0.4,
                    fill: true,
                    backgroundColor: gradient
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, max: 10, ticks: { color: '#64748b' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { ticks: { color: '#64748b' }, grid: { display: false } }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

// --- Initialization ---
let personaGroups = [];
let chartInstance = null;

const DEFAULT_GROUPS = [
    { 
        id: 'young', 
        name: 'Young Adults (Kerala)', 
        isPredefined: true,
        personas: [
            { name: "Arjun K.", age: 22, gender: "Male", job: "IT Professional", location: "Kochi, Kerala", description: "Loves fast-paced thrillers and dark humor." },
            { name: "Meera R.", age: 24, gender: "Female", job: "Content Creator", location: "Trivandrum, Kerala", description: "Enjoys romantic comedies and aesthetic cinematography." }
        ]
    }
];

// --- Confirmation Modal Logic ---
let activeConfirmCallback = null;

function openConfirmModal(message, callback) {
    const msgEl = document.getElementById('confirm-message');
    const modalEl = document.getElementById('confirm-modal');
    if (msgEl && modalEl) {
        msgEl.innerText = message;
        activeConfirmCallback = callback;
        modalEl.classList.remove('hidden');
        addCursorHover();
    }
}

function closeConfirmModal() {
    const modalEl = document.getElementById('confirm-modal');
    if (modalEl) modalEl.classList.add('hidden');
    activeConfirmCallback = null;
}

const confirmActionBtn = document.getElementById('confirm-action-btn');
if (confirmActionBtn) {
    confirmActionBtn.addEventListener('click', () => {
        if (activeConfirmCallback) {
            activeConfirmCallback();
            closeConfirmModal();
        }
    });
}

// --- Edit/Delete Persona Logic ---
function deletePersona(groupId, personaName) {
    openConfirmModal(`Permanently remove ${personaName} from this audience vault?`, () => {
        const group = personaGroups.find(g => g.id === groupId);
        if (!group) return;
        
        group.personas = group.personas.filter(p => p.name !== personaName);
        saveState();
        
        // Refresh UI
        const overlay = document.getElementById('vault-overlay');
        if (overlay) overlay.remove();
        viewGroupDetails(groupId);
        renderGroupList();
    });
}

function openEditModal(groupId, personaName) {
    const group = personaGroups.find(g => g.id === groupId);
    const persona = group.personas.find(p => p.name === personaName);
    
    const editModal = document.getElementById('edit-modal');
    if (!editModal) return;

    document.getElementById('edit-group-id').value = groupId;
    document.getElementById('edit-persona-id').value = personaName; // Use name as ID for now
    document.getElementById('edit-persona-name').value = persona.name;
    document.getElementById('edit-persona-age').value = persona.age;
    document.getElementById('edit-persona-gender').value = persona.gender;
    document.getElementById('edit-persona-bio').value = persona.description;
    
    editModal.classList.remove('hidden');
    addCursorHover();
}

function closeEditModal() {
    const editModal = document.getElementById('edit-modal');
    if (editModal) editModal.classList.add('hidden');
}

function savePersonaEdit() {
    const groupId = document.getElementById('edit-group-id').value;
    const oldName = document.getElementById('edit-persona-id').value;
    
    const group = personaGroups.find(g => g.id === groupId);
    const persona = group.personas.find(p => p.name === oldName);
    
    persona.name = document.getElementById('edit-persona-name').value;
    persona.age = document.getElementById('edit-persona-age').value;
    persona.gender = document.getElementById('edit-persona-gender').value;
    persona.description = document.getElementById('edit-persona-bio').value;
    
    saveState();
    closeEditModal();
    
    // Refresh detail view
    const overlay = document.getElementById('vault-overlay');
    if (overlay) overlay.remove();
    viewGroupDetails(groupId);
    renderGroupList();
}

function init() {
    const stored = localStorage.getItem('matinee_persona_groups');
    if (stored) {
        personaGroups = JSON.parse(stored);
    } else {
        personaGroups = [...DEFAULT_GROUPS];
        saveState();
    }
    
    // Page-specific initialization
    renderGroupList();
    renderGroupSelect();
    addCursorHover();
    handleScroll();
}

function saveState() {
    localStorage.setItem('matinee_persona_groups', JSON.stringify(personaGroups));
}

function deleteGroup(groupId) {
    const group = personaGroups.find(g => g.id === groupId);
    openConfirmModal(`Purge the entire ${group.name} group from memory?`, () => {
        personaGroups = personaGroups.filter(g => g.id !== groupId);
        saveState();
        renderGroupList();
        renderGroupSelect();
    });
}

function renderGroupSelect() {
    const select = document.getElementById('evaluation-group-select');
    if (!select) return;
    select.innerHTML = '';
    personaGroups.forEach(group => {
        const opt = document.createElement('option');
        opt.value = group.id;
        opt.innerText = group.name;
        select.appendChild(opt);
    });
}

window.onload = init;


