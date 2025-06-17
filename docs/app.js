// Konfigurace Google Sheets API
const SPREADSHEET_ID = '1XAFv60X9g_NaTOrJL_9gb67pFNw04cfLKJ01Zr98FC4'; // ID vašeho Google Sheetu
const API_KEY = 'AIzaSyDk08_Bu-BFTJTRwYcZOw658FRRmIfjemo'; // Vložte sem váš Google API klíč
const SHEET_NAME = 'List 1'; // Název listu v Google Sheets (přesně podle záložky)
const BACKEND_URL = "https://api.zsmik.cz";

// Přidání logování pro diagnostiku
console.log('Backend URL:', BACKEND_URL);

// DOM elementy
const loginContainer = document.getElementById('login-container');
const appContainer = document.getElementById('app-container');
const loginForm = document.getElementById('login-form');
// const revisionsTable = document.getElementById('revisions-table');
// const revisionsBody = document.getElementById('revisions-body');
const addRevisionBtn = document.getElementById('add-revision');
const logoutBtn = document.getElementById('logout');
const modal = document.getElementById('modal');
const revisionForm = document.getElementById('revision-form');
const cancelRevisionBtn = document.getElementById('cancel-revision');
const detailModal = document.getElementById('detail-modal');
const detailForm = document.getElementById('detail-form');
const cancelDetailBtn = document.getElementById('cancel-detail');

// Přidání logování pro DOM elementy
console.log('DOM elementy:', {
    loginContainer: !!loginContainer,
    appContainer: !!appContainer,
    loginForm: !!loginForm,
    // revisionsTable: !!revisionsTable,
    // revisionsBody: !!revisionsBody
});

let currentRowCount = 0;
let currentDetailIndex = null;
let lastLoadedRevisions = [];
let nextDateManuallyChanged = false;
let revisionNextDateManuallyChanged = false;
let currentRevisionType = 'kindergarten';

// Načtení revizí z backendu
async function loadRevisions() {
    try {
        console.log('Načítám revize z:', `${BACKEND_URL}/get_revisions`);
        const response = await fetch(`${BACKEND_URL}/get_revisions`);
        console.log('Odpověď serveru:', response.status, response.statusText);
        const data = await response.json();
        console.log('Načtená data:', data);
        displayRevisions(data.revisions);
    } catch (error) {
        console.error('Chyba při načítání revizí:', error);
        alert('Chyba při načítání revizí: ' + error.message);
    }
}

// Načtení revizí pro školku
async function loadRevisionsKindergarten() {
    try {
        const response = await fetch(`${BACKEND_URL}/get_revisions`);
        const data = await response.json();
        displayRevisions(data.revisions, 'kindergarten');
    } catch (error) {
        console.error('Chyba při načítání revizí školky:', error);
    }
}

// Načtení revizí pro školu
async function loadRevisionsSchool() {
    try {
        const response = await fetch(`${BACKEND_URL}/get_revisions_school`);
        const data = await response.json();
        displayRevisions(data.revisions, 'school');
    } catch (error) {
        console.error('Chyba při načítání revizí školy:', error);
    }
}

// Zobrazení revizí v tabulce
function formatCzechDate(dateStr) {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (isNaN(d)) return dateStr;
    return d.toLocaleDateString('cs-CZ');
}

function getStatusAndClass(daysToNext) {
    let status = '';
    let statusClass = '';
    if (daysToNext > 60) {
        status = 'OK';
        statusClass = 'status-ok';
    } else if (daysToNext > 30) {
        status = 'Blíží se';
        statusClass = 'status-beige';
    } else if (daysToNext > 0) {
        status = 'Brzy';
        statusClass = 'status-warning';
    } else {
        status = 'Po termínu';
        statusClass = 'status-danger';
    }
    return { status, statusClass };
}

function displayRevisions(revisions, type) {
    const body = type === 'school' ? document.getElementById('revisions-school-body') : document.getElementById('revisions-kindergarten-body');
    body.innerHTML = '';
    currentRowCount = 0;
    lastLoadedRevisions = revisions;
    revisions.forEach((revision, index) => {
        if (!revision || revision.every(cell => !cell)) return;
        const filled = Array(10).fill('').map((_, i) => revision[i] || '');
        const [title, lastDate, nextDate, intervalMonths, daysToNextRaw, statusRaw, company, person, email, phone] = filled;
        const daysToNext = parseInt(daysToNextRaw, 10);
        const { status, statusClass } = getStatusAndClass(daysToNext);
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${title}</td>
            <td>${formatCzechDate(lastDate)}</td>
            <td>${formatCzechDate(nextDate)}</td>
            <td>${intervalMonths}</td>
            <td>${daysToNext}</td>
            <td><span class="${statusClass}">${status}</span></td>
        `;
        row.addEventListener('click', () => {
            openDetailModal(index, type);
        });
        body.appendChild(row);
        currentRowCount++;
    });
}

function openDetailModal(index, type) {
    currentRevisionType = type;
    currentDetailIndex = index;
    const rev = lastLoadedRevisions[index];
    if (!rev) return;
    const [title, lastDate, nextDate, intervalMonths, daysToNext, status, company, person, email, phone] = rev;
    document.getElementById('detail-title').value = title || '';
    document.getElementById('detail-last-date').value = lastDate || '';
    document.getElementById('detail-next-date').value = nextDate || '';
    document.getElementById('detail-interval').value = intervalMonths || '';
    document.getElementById('detail-days-to-next').value = daysToNext || '';
    document.getElementById('detail-status').value = status || '';
    document.getElementById('detail-company').value = company || '';
    document.getElementById('detail-person').value = person || '';
    document.getElementById('detail-email').value = email || '';
    document.getElementById('detail-phone').value = phone || '';
    detailModal.classList.remove('hidden');
}

function recalculateDetailFields(trigger) {
    const lastDate = document.getElementById('detail-last-date').value;
    const intervalMonths = parseInt(document.getElementById('detail-interval').value, 10);
    let nextDate = document.getElementById('detail-next-date').value;

    if ((trigger === 'last' || trigger === 'interval') && !nextDateManuallyChanged) {
        if (lastDate && intervalMonths) {
            const last = new Date(lastDate);
            const next = new Date(last);
            next.setMonth(next.getMonth() + intervalMonths);
            nextDate = next.toISOString().split('T')[0];
            document.getElementById('detail-next-date').value = nextDate;
        }
    }
    if (trigger === 'next') {
        nextDateManuallyChanged = true;
    }
    if (trigger === 'last' || trigger === 'interval') {
        nextDateManuallyChanged = false;
    }
    if (nextDate) {
        const today = new Date();
        const next = new Date(nextDate);
        const diffTime = next - today;
        const daysToNext = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        document.getElementById('detail-days-to-next').value = daysToNext;
        const { status } = getStatusAndClass(daysToNext);
        document.getElementById('detail-status').value = status;
    }
}

document.getElementById('detail-last-date').addEventListener('change', () => recalculateDetailFields('last'));
document.getElementById('detail-interval').addEventListener('input', () => recalculateDetailFields('interval'));
document.getElementById('detail-next-date').addEventListener('change', () => recalculateDetailFields('next'));

function recalculateRevisionFields(trigger) {
    const lastDate = document.getElementById('revision-last-date').value;
    const intervalMonths = parseInt(document.getElementById('revision-interval').value, 10);
    let nextDate = document.getElementById('revision-next-date').value;

    if ((trigger === 'last' || trigger === 'interval') && !revisionNextDateManuallyChanged) {
        if (lastDate && intervalMonths) {
            const last = new Date(lastDate);
            const next = new Date(last);
            next.setMonth(next.getMonth() + intervalMonths);
            nextDate = next.toISOString().split('T')[0];
            document.getElementById('revision-next-date').value = nextDate;
        }
    }
    if (trigger === 'next') {
        revisionNextDateManuallyChanged = true;
    }
    if (trigger === 'last' || trigger === 'interval') {
        revisionNextDateManuallyChanged = false;
    }
    if (nextDate) {
        const today = new Date();
        const next = new Date(nextDate);
        const diffTime = next - today;
        const daysToNext = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        document.getElementById('revision-days-to-next').value = daysToNext;
        const { status } = getStatusAndClass(daysToNext);
        document.getElementById('revision-status').value = status;
    }
}

document.getElementById('revision-last-date').addEventListener('change', () => recalculateRevisionFields('last'));
document.getElementById('revision-interval').addEventListener('input', () => recalculateRevisionFields('interval'));
document.getElementById('revision-next-date').addEventListener('change', () => recalculateRevisionFields('next'));

async function addRevision(event) {
    event.preventDefault();
    const title = document.getElementById('revision-title').value;
    const lastDate = document.getElementById('revision-last-date').value;
    const nextDate = document.getElementById('revision-next-date').value;
    const intervalMonths = document.getElementById('revision-interval').value;
    // const daysToNext = document.getElementById('revision-days-to-next').value; // NEPOSÍLAT
    const status = document.getElementById('revision-status').value;
    const company = document.getElementById('revision-company').value;
    const person = document.getElementById('revision-person').value;
    const email = document.getElementById('revision-email').value;
    const phone = document.getElementById('revision-phone').value;

    try {
        const response = await fetch(`${BACKEND_URL}/add_revision`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                lastDate,
                nextDate,
                intervalMonths,
                // daysToNext,
                status,
                company,
                person,
                email,
                phone
            })
        });
        const data = await response.json();
        if (data.success) {
            modal.classList.add('hidden');
            revisionForm.reset();
            loadRevisions();
        } else {
            alert('Chyba při ukládání revize!');
        }
    } catch (error) {
        console.error('Chyba při ukládání revize:', error);
    }
}

// Mazání z detailu
const deleteDetailBtn = document.getElementById('delete-detail');
deleteDetailBtn.addEventListener('click', async () => {
    if (currentDetailIndex === null) return;
    if (!confirm('Opravdu chcete smazat tuto revizi?')) return;
    try {
        const response = await fetch(`${BACKEND_URL}/delete_revision`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ row_index: currentDetailIndex })
        });
        const data = await response.json();
        if (data.success) {
            detailModal.classList.add('hidden');
            detailForm.reset();
            loadRevisions();
        } else {
            alert('Chyba při mazání revize!');
        }
    } catch (error) {
        console.error('Chyba při mazání revize:', error);
    }
});

// Přihlášení uživatele
async function loginUser(username, password) {
    try {
        console.log('Pokus o přihlášení uživatele:', username);
        console.log('URL pro přihlášení:', `${BACKEND_URL}/login`);
        
        const response = await fetch(`${BACKEND_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        console.log('Odpověď serveru:', response.status, response.statusText);
        const data = await response.json();
        console.log('Data odpovědi:', data);
        
        if (data.success) {
            console.log('Přihlášení úspěšné');
            localStorage.setItem('role', data.role || 'user');
            localStorage.setItem('user_type', data.user_type || '');
            localStorage.setItem('isLoggedIn', 'true');
            loginContainer.classList.add('hidden');
            appContainer.classList.remove('hidden');
            toggleTabsByRole();
            showDefaultTabByRole();
            loadRevisions();
        } else {
            console.error('Chyba přihlášení:', data.error);
            alert(data.error || 'Chyba při přihlašování');
        }
    } catch (error) {
        console.error('Chyba při přihlašování:', error);
        alert('Chyba při přihlašování: ' + error.message);
    }
}

// Event listener pro přihlašovací formulář
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    console.log('Odesílám přihlašovací formulář:', { username });
    await loginUser(username, password);
});

function toggleTabsByRole() {
    const role = localStorage.getItem('role');
    const userType = localStorage.getItem('user_type');
    const userTabBtn = document.querySelector('.tab-button[data-tab="users"]');
    const revKindBtn = document.querySelector('.tab-button[data-tab="revisions-kindergarten"]');
    const revSchoolBtn = document.querySelector('.tab-button[data-tab="revisions-school"]');
    // Admin vidí vše
    if (role === 'admin') {
        if (userTabBtn) userTabBtn.style.display = '';
        if (revKindBtn) revKindBtn.style.display = '';
        if (revSchoolBtn) revSchoolBtn.style.display = '';
    } else {
        if (userTabBtn) userTabBtn.style.display = 'none';
        if (revKindBtn) revKindBtn.style.display = (userType === 'školka') ? '' : 'none';
        if (revSchoolBtn) revSchoolBtn.style.display = (userType === 'škola') ? '' : 'none';
    }
}

// Po přihlášení/načtení stránky automaticky zobraz správnou záložku
function showDefaultTabByRole() {
    const role = localStorage.getItem('role');
    const userType = localStorage.getItem('user_type');
    if (role === 'admin') {
        // Aktivuj školku jako výchozí
        activateTab('revisions-kindergarten');
    } else if (userType === 'školka') {
        activateTab('revisions-kindergarten');
    } else if (userType === 'škola') {
        activateTab('revisions-school');
    }
}

function activateTab(tabName) {
    document.querySelectorAll('.tab-button').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    const btn = document.querySelector(`.tab-button[data-tab="${tabName}"]`);
    const tab = document.getElementById(`${tabName}-tab`);
    if (btn) btn.classList.add('active');
    if (tab) tab.classList.add('active');
}

// Odhlášení
function logout() {
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('role');
    localStorage.removeItem('user_type');
    loginContainer.classList.remove('hidden');
    appContainer.classList.add('hidden');
    modal.classList.add('hidden'); // Modal skrytý po odhlášení
}

// Event listeners
logoutBtn.addEventListener('click', logout);
addRevisionBtn.addEventListener('click', () => {
    if (localStorage.getItem('isLoggedIn') === 'true') {
        modal.classList.remove('hidden');
    }
});
cancelRevisionBtn.addEventListener('click', () => {
    modal.classList.add('hidden');
    revisionForm.reset();
});
revisionForm.addEventListener('submit', addRevision);

cancelDetailBtn.addEventListener('click', () => {
    detailModal.classList.add('hidden');
    detailForm.reset();
});

detailForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (currentDetailIndex === null) return;
    const title = document.getElementById('detail-title').value;
    const lastDate = document.getElementById('detail-last-date').value;
    const nextDate = document.getElementById('detail-next-date').value;
    const intervalMonths = document.getElementById('detail-interval').value;
    // const daysToNext = document.getElementById('detail-days-to-next').value; // NEPOSÍLAT
    const status = document.getElementById('detail-status').value;
    const company = document.getElementById('detail-company').value;
    const person = document.getElementById('detail-person').value;
    const email = document.getElementById('detail-email').value;
    const phone = document.getElementById('detail-phone').value;
    const data = {
        row_index: currentDetailIndex,
        title, lastDate, nextDate, intervalMonths, /* daysToNext, */ status, company, person, email, phone
    };
    try {
        let response;
        if (currentRevisionType === 'school') {
            response = await fetch(`${BACKEND_URL}/edit_revision_school`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
            });
        } else {
            response = await fetch(`${BACKEND_URL}/edit_revision`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data)
            });
        }
        const respData = await response.json();
        if (respData.success) {
            detailModal.classList.add('hidden');
            detailForm.reset();
            if (currentRevisionType === 'school') {
                loadRevisionsSchool();
            } else {
                loadRevisionsKindergarten();
            }
        } else {
            alert('Chyba při ukládání změn!');
        }
    } catch (error) {
        console.error('Chyba při ukládání změn:', error);
    }
    currentDetailIndex = null;
});

// Kontrola přihlášení při načtení stránky
window.addEventListener('load', () => {
    modal.classList.add('hidden'); // Modal vždy skrytý při načtení
    loginContainer.classList.remove('hidden');
    appContainer.classList.add('hidden');
    if (localStorage.getItem('isLoggedIn') === 'true') {
        loginContainer.classList.add('hidden');
        appContainer.classList.remove('hidden');
        loadRevisions(); // Načíst data i po reloadu
    }
    toggleTabsByRole();
    showDefaultTabByRole();
});

// Správa uživatelů
async function loadUsers() {
    try {
        const response = await fetch(`${BACKEND_URL}/get_users`);
        const data = await response.json();
        displayUsers(data.users);
    } catch (error) {
        console.error('Chyba při načítání uživatelů:', error);
    }
}

function displayUsers(users) {
    const usersBody = document.getElementById('users-body');
    usersBody.innerHTML = '';
    
    users.forEach(user => {
        let username, role, userType;
        if (typeof user === 'string') {
            username = user;
            role = 'user';
            userType = '';
        } else {
            username = user.username;
            role = user.role || 'user';
            userType = user.user_type || '';
        }
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${username}</td>
            <td>${role}</td>
            <td>${userType}</td>
            <td>
                <button class="edit-user" data-username="${username}" data-role="${role}" data-type="${userType}">Upravit</button>
                <button class="delete-user" data-username="${username}">Smazat</button>
            </td>
        `;
        usersBody.appendChild(row);
    });
    
    // Event listenery pro mazání
    document.querySelectorAll('.delete-user').forEach(button => {
        button.addEventListener('click', async (e) => {
            const username = e.target.dataset.username;
            if (confirm(`Opravdu chcete smazat uživatele ${username}?`)) {
                try {
                    const response = await fetch(`${BACKEND_URL}/delete_user`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ username })
                    });
                    const data = await response.json();
                    if (data.success) {
                        loadUsers();
                    } else {
                        alert('Chyba při mazání uživatele!');
                    }
                } catch (error) {
                    console.error('Chyba při mazání uživatele:', error);
                }
            }
        });
    });
    // Event listenery pro editaci
    document.querySelectorAll('.edit-user').forEach(button => {
        button.addEventListener('click', (e) => {
            const username = e.target.dataset.username;
            const role = e.target.dataset.role || 'user';
            const userType = e.target.dataset.type || 'školka';
            document.getElementById('edit-username').value = username;
            document.getElementById('edit-password').value = '';
            document.getElementById('edit-role').value = role;
            document.getElementById('edit-type').value = userType;
            document.getElementById('edit-user-modal').classList.remove('hidden');
        });
    });
}

// Obsluha modálního okna pro změnu hesla
const editUserModal = document.getElementById('edit-user-modal');
const editUserForm = document.getElementById('edit-user-form');
const cancelEditUserBtn = document.getElementById('cancel-edit-user');

cancelEditUserBtn.addEventListener('click', () => {
    editUserModal.classList.add('hidden');
    editUserForm.reset();
});

editUserForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const username = document.getElementById('edit-username').value;
    const password = document.getElementById('edit-password').value;
    const role = document.getElementById('edit-role').value;
    const userType = document.getElementById('edit-type').value;
    try {
        const response = await fetch(`${BACKEND_URL}/edit_user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, role, user_type: userType })
        });
        const data = await response.json();
        if (data.success) {
            editUserModal.classList.add('hidden');
            editUserForm.reset();
            loadUsers();
        } else {
            alert('Chyba při změně hesla/role!');
        }
    } catch (error) {
        console.error('Chyba při změně hesla/role:', error);
    }
});

// Přepínání záložek
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        tabButtons.forEach(b => b.classList.remove('active'));
        tabContents.forEach(c => c.classList.remove('active'));
        button.classList.add('active');
        const tabId = button.dataset.tab + '-tab';
        const tabContent = document.getElementById(tabId);
        if (tabContent) tabContent.classList.add('active');
        // Načti data pro aktivní záložku
        if (tabId === 'revisions-kindergarten-tab') {
            loadRevisionsKindergarten();
        } else if (tabId === 'revisions-school-tab') {
            loadRevisionsSchool();
        } else if (tabId === 'users-tab') {
            loadUsers();
        }
    });
});

// Po načtení stránky nastavím aktivní záložku na revize
window.addEventListener('DOMContentLoaded', () => {
    document.querySelector('[data-tab="revisions"]').classList.add('active');
    document.getElementById('revisions-tab').classList.add('active');
    document.getElementById('users-tab').classList.remove('active');
    toggleTabsByRole();
    showDefaultTabByRole();
});

// Přidání nového uživatele
const userModal = document.getElementById('user-modal');
const userForm = document.getElementById('user-form');
const addUserBtn = document.getElementById('add-user');
const cancelUserBtn = document.getElementById('cancel-user');

addUserBtn.addEventListener('click', () => {
    userModal.classList.remove('hidden');
});

cancelUserBtn.addEventListener('click', () => {
    userModal.classList.add('hidden');
    userForm.reset();
});

userForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const username = document.getElementById('new-username').value;
    const password = document.getElementById('new-password').value;
    const role = document.getElementById('new-role').value;
    const userType = document.getElementById('new-type').value;
    try {
        const response = await fetch(`${BACKEND_URL}/add_user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, role, user_type: userType })
        });
        const data = await response.json();
        if (data.success) {
            userModal.classList.add('hidden');
            userForm.reset();
            loadUsers();
        } else {
            alert('Chyba při přidávání uživatele!');
        }
    } catch (error) {
        console.error('Chyba při přidávání uživatele:', error);
    }
});

// Přidání nové revize pro školku
const addRevisionKindBtn = document.getElementById('add-revision-kindergarten');
addRevisionKindBtn.addEventListener('click', () => {
    openRevisionModal('kindergarten');
});

// Přidání nové revize pro školu
const addRevisionSchoolBtn = document.getElementById('add-revision-school');
addRevisionSchoolBtn.addEventListener('click', () => {
    openRevisionModal('school');
});

// Funkce pro otevření modálního okna pro přidání/editaci revize
function openRevisionModal(type, index = null) {
    currentRevisionType = type;
    currentDetailIndex = index;
    if (index !== null) {
        // Editace - předvyplň hodnoty
        const rev = lastLoadedRevisions[index];
        if (!rev) return;
        const [title, lastDate, nextDate, intervalMonths, daysToNext, status, company, person, email, phone] = rev;
        document.getElementById('revision-title').value = title || '';
        document.getElementById('revision-last-date').value = lastDate || '';
        document.getElementById('revision-next-date').value = nextDate || '';
        document.getElementById('revision-interval').value = intervalMonths || '';
        document.getElementById('revision-days-to-next').value = daysToNext || '';
        document.getElementById('revision-status').value = status || '';
        document.getElementById('revision-company').value = company || '';
        document.getElementById('revision-person').value = person || '';
        document.getElementById('revision-email').value = email || '';
        document.getElementById('revision-phone').value = phone || '';
    } else {
        // Přidání - vyprázdni formulář
        document.getElementById('revision-form').reset();
    }
    modal.classList.remove('hidden');
} 
