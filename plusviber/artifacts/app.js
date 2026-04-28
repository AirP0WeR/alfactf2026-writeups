const API = '/api';
let token = localStorage.getItem('token');
let currentUser = null;
let _vibeInterval = null;

// ---- Vibe loader ----

function spawnParticle() {
    const field = document.getElementById('vibe-field');
    if (!field) return;
    const isPlus = Math.random() < 0.4;
    const el = document.createElement('span');
    el.className = 'vibe-particle' + (isPlus ? ' vibe-sym' : '');
    el.textContent = isPlus ? '+' : 'ВАЙБ';
    el.style.left = (5 + Math.random() * 90) + '%';
    el.style.top = (20 + Math.random() * 60) + '%';
    el.style.setProperty('--drift', (Math.random() * 40 - 20) + 'px');
    field.appendChild(el);
    el.addEventListener('animationend', () => el.remove());
}

function startVibeLoader() {
    const field = document.getElementById('vibe-field');
    if (field) field.innerHTML = '';
    for (let i = 0; i < 6; i++) setTimeout(spawnParticle, i * 150);
    _vibeInterval = setInterval(spawnParticle, 300);
}

function stopVibeLoader() {
    if (_vibeInterval) { clearInterval(_vibeInterval); _vibeInterval = null; }
}

// ---- API helper ----

async function api(method, path, body) {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('is-hidden');
    startVibeLoader();

    const opts = { method, headers: {} };
    if (token) opts.headers['Authorization'] = `Bearer ${token}`;
    if (body && !(body instanceof FormData)) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(body);
    } else if (body instanceof FormData) {
        opts.body = body;
    }

    try {
        const res = await fetch(API + path, opts);
        const data = await res.json();
        if (!res.ok) throw { status: res.status, detail: data.detail || 'Error' };
        return data;
    } finally {
        stopVibeLoader();
        overlay.classList.add('is-hidden');
    }
}

// ---- Auth ----

async function doLogin() {
    hideAuthError();
    const username = document.getElementById('auth-username').value.trim();
    const password = document.getElementById('auth-password').value;
    try {
        const data = await api('POST', '/login', { username, password });
        token = data.token;
        localStorage.setItem('token', token);
        await initApp();
    } catch (e) {
        showAuthError(e.detail || 'Ошибка входа');
    }
}

async function doRegister() {
    hideAuthError();
    const username = document.getElementById('auth-username').value.trim();
    const password = document.getElementById('auth-password').value;
    if (username.length < 9) { showAuthError('Имя пользователя — минимум 9 символов'); return; }
    if (password.length < 9) { showAuthError('Пароль — минимум 9 символов'); return; }
    try {
        const data = await api('POST', '/register', { username, password });
        token = data.token;
        localStorage.setItem('token', token);
        await initApp();
    } catch (e) {
        showAuthError(e.detail || 'Ошибка регистрации');
    }
}

function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    document.getElementById('page-app').style.display = 'none';
    document.getElementById('page-auth').style.display = '';
    document.getElementById('nav-user').style.display = 'none';
}

function showAuthError(msg) {
    const el = document.getElementById('auth-error');
    el.textContent = msg;
    el.classList.remove('is-hidden');
}

function hideAuthError() {
    document.getElementById('auth-error').classList.add('is-hidden');
}

// ---- Init ----

async function initApp() {
    try {
        currentUser = await api('GET', '/me');
    } catch {
        logout();
        return;
    }
    document.getElementById('page-auth').style.display = 'none';
    document.getElementById('page-app').style.display = '';
    document.getElementById('nav-user').style.display = 'flex';
    document.getElementById('nav-username').textContent = currentUser.username;
    showFeed();
}

// ---- Sections ----

function hideAllSections() {
    document.querySelectorAll('.content-section').forEach(s => s.classList.add('is-hidden'));
    document.querySelectorAll('.menu-list a').forEach(a => a.classList.remove('is-active'));
}

function showSection(id, menuId) {
    hideAllSections();
    document.getElementById(id).classList.remove('is-hidden');
    if (menuId) document.getElementById(menuId).classList.add('is-active');
}

// ---- Feed ----

async function showFeed() {
    showSection('section-feed', 'menu-feed');
    try {
        const posts = await api('GET', '/feed');
        const list = document.getElementById('feed-list');
        const empty = document.getElementById('feed-empty');
        if (posts.length === 0) {
            list.innerHTML = '';
            empty.classList.remove('is-hidden');
        } else {
            empty.classList.add('is-hidden');
            list.innerHTML = posts.map(p => renderPost(p, false)).join('');
        }
    } catch (e) { console.error(e); }
}

// ---- My posts ----

async function showMyPosts() {
    showSection('section-my', 'menu-my');
    document.getElementById('new-post-form').style.display = 'none';
    document.getElementById('edit-post-form').style.display = 'none';
    try {
        const posts = await api('GET', `/users/${currentUser.id}/posts`);
        const listEl = document.getElementById('my-posts-list');
        listEl.innerHTML = posts.length
            ? posts.map(p => renderPost(p, true)).join('')
            : '<p class="has-text-grey">У вас пока нет постов</p>';
    } catch (e) { console.error(e); }
}

// ---- My notes ----

async function showMyNotes() {
    showSection('section-notes', 'menu-notes');
    document.getElementById('new-note-form').style.display = 'none';
    document.getElementById('edit-note-form').style.display = 'none';
    try {
        const notes = await api('GET', `/users/${currentUser.uuid}/notes`);
        const listEl = document.getElementById('my-notes-list');
        listEl.innerHTML = notes.length
            ? notes.map(n => renderNote(n)).join('')
            : '<p class="has-text-grey">У вас пока нет заметок</p>';
    } catch (e) { console.error(e); }
}

// ---- Subscriptions ----

async function showSubscriptions() {
    showSection('section-subs', 'menu-subs');
    try {
        const subs = await api('GET', '/subscriptions');
        const list = document.getElementById('subs-list');
        if (subs.length === 0) {
            list.innerHTML = '<p class="has-text-grey">Вы пока ни на кого не подписаны</p>';
        } else {
            list.innerHTML = subs.map(s => `
                <div class="box is-flex is-align-items-center is-justify-content-space-between">
                    <div>
                        <a onclick="showUserProfile(${s.user.id})" class="has-text-link has-text-weight-semibold" style="cursor:pointer">
                            ${esc(s.user.username)}
                        </a>
                        <span class="has-text-grey is-size-7 ml-2">с ${new Date(s.subscribed_at).toLocaleDateString('ru')}</span>
                    </div>
                    <button class="button is-small is-danger is-outlined is-rounded" onclick="doUnsubscribe(${s.user.id})">Отписаться</button>
                </div>
            `).join('');
        }
    } catch (e) { console.error(e); }
}

// ---- User profile ----

async function showUserProfile(userId) {
    showSection('section-profile');
    const header = document.getElementById('profile-header');
    const postsEl = document.getElementById('profile-posts');
    try {
        const posts = await api('GET', `/users/${userId}/posts`);
        const authorName = posts.length > 0 ? posts[0].author : `#${userId}`;
        header.innerHTML = `
            <div class="is-flex is-align-items-center is-justify-content-space-between mb-4">
                <h3 class="title is-4 mb-0">${esc(authorName)}</h3>
            </div>
        `;
        postsEl.innerHTML = posts.length
            ? posts.map(p => renderPost(p, false)).join('')
            : '<p class="has-text-grey">Нет постов</p>';
    } catch (e) { console.error(e); }
}

// ---- New post ----

function showNewPostForm() {
    document.getElementById('new-post-form').style.display = '';
    document.getElementById('new-post-form').scrollIntoView({ behavior: 'smooth' });
}

async function createPost() {
    const title = document.getElementById('post-title').value.trim();
    const content = document.getElementById('post-content').value.trim();
    const fileInput = document.getElementById('post-media');
    if (!title || !content) return;
    try {
        const post = await api('POST', '/posts', { title, content });
        if (fileInput.files.length > 0) {
            const fd = new FormData();
            fd.append('file', fileInput.files[0]);
            await api('POST', `/posts/${post.uuid}/media`, fd);
        }
        document.getElementById('post-title').value = '';
        document.getElementById('post-content').value = '';
        fileInput.value = '';
        document.getElementById('new-post-form').style.display = 'none';
        showMyPosts();
    } catch (e) { console.error(e); }
}

// ---- Edit post ----

let _postCache = {};
let editingPostUuid = null;

function startEditFromCache(uuid) {
    const post = _postCache[uuid];
    if (!post) return;
    const form = document.getElementById('edit-post-form');
    form.style.display = '';
    document.getElementById('edit-post-title').value = post.title;
    document.getElementById('edit-post-content').value = post.content;
    document.getElementById('edit-post-media').value = '';
    editingPostUuid = uuid;
    form.scrollIntoView({ behavior: 'smooth' });
}

async function saveEditPost() {
    if (!editingPostUuid) return;
    const title = document.getElementById('edit-post-title').value.trim();
    const content = document.getElementById('edit-post-content').value.trim();
    const fileInput = document.getElementById('edit-post-media');
    if (!title || !content) return;
    try {
        await api('PUT', `/posts/${editingPostUuid}`, { title, content });
        if (fileInput.files.length > 0) {
            const fd = new FormData();
            fd.append('file', fileInput.files[0]);
            await api('POST', `/posts/${editingPostUuid}/media`, fd);
        }
        editingPostUuid = null;
        document.getElementById('edit-post-form').style.display = 'none';
        showMyPosts();
    } catch (e) { console.error(e); }
}

function cancelEditPost() {
    editingPostUuid = null;
    document.getElementById('edit-post-form').style.display = 'none';
}

async function deletePost(uuid) {
    if (!confirm('Удалить пост?')) return;
    try { await api('DELETE', `/posts/${uuid}`); showMyPosts(); } catch (e) { console.error(e); }
}

async function deletePostMedia(uuid) {
    try { await api('DELETE', `/posts/${uuid}/media`); showMyPosts(); } catch (e) { console.error(e); }
}

// ---- New note ----

function showNewNoteForm() {
    document.getElementById('new-note-form').style.display = '';
    document.getElementById('new-note-form').scrollIntoView({ behavior: 'smooth' });
}

async function createNote() {
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value.trim();
    if (!title || !content) return;
    try {
        await api('POST', '/notes', { title, content });
        document.getElementById('note-title').value = '';
        document.getElementById('note-content').value = '';
        document.getElementById('new-note-form').style.display = 'none';
        showMyNotes();
    } catch (e) { console.error(e); }
}

// ---- Edit note ----

let _noteCache = {};
let editingNoteUuid = null;

function startEditNote(uuid) {
    const note = _noteCache[uuid];
    if (!note) return;
    const form = document.getElementById('edit-note-form');
    form.style.display = '';
    document.getElementById('edit-note-title').value = note.title;
    document.getElementById('edit-note-content').value = note.content;
    editingNoteUuid = uuid;
    form.scrollIntoView({ behavior: 'smooth' });
}

async function saveEditNote() {
    if (!editingNoteUuid) return;
    const title = document.getElementById('edit-note-title').value.trim();
    const content = document.getElementById('edit-note-content').value.trim();
    if (!title || !content) return;
    try {
        await api('PUT', `/notes/${editingNoteUuid}`, { title, content });
        editingNoteUuid = null;
        document.getElementById('edit-note-form').style.display = 'none';
        showMyNotes();
    } catch (e) { console.error(e); }
}

function cancelEditNote() {
    editingNoteUuid = null;
    document.getElementById('edit-note-form').style.display = 'none';
}

async function deleteNote(uuid) {
    if (!confirm('Удалить заметку?')) return;
    try { await api('DELETE', `/notes/${uuid}`); showMyNotes(); } catch (e) { console.error(e); }
}

// ---- Unsubscribe ----

async function doUnsubscribe(userId) {
    try { await api('POST', '/unsubscribe', { user_id: userId }); showSubscriptions(); } catch (e) { console.error(e); }
}

// ---- Stubs ----

function showMessages() {
    showSection('section-messages', 'menu-messages');
}

function showSearch() {
    showSection('section-search', 'menu-search');
}

// ---- Helpers ----

function renderPost(post, isOwn) {
    _postCache[post.uuid] = post;
    const imageHtml = post.image
        ? `<figure class="image mt-3" style="position:relative">
               <img src="${esc(post.image)}" alt="${esc(post.title)}" loading="lazy" style="max-width:100%;border-radius:12px">
               ${isOwn ? `<button class="delete is-small" style="position:absolute;top:8px;right:8px;background:rgba(0,0,0,0.5)" onclick="deletePostMedia('${post.uuid}')"></button>` : ''}
           </figure>`
        : '';
    const actions = isOwn ? `
        <div class="buttons are-small mt-3">
            <button class="button is-small is-outlined" onclick="startEditFromCache('${post.uuid}')">Редактировать</button>
            <button class="button is-small is-danger is-outlined" onclick="deletePost('${post.uuid}')">Удалить</button>
        </div>` : '';
    return `
        <div class="box post-card">
            <p class="is-size-5 has-text-weight-semibold">${esc(post.title)}</p>
            <p class="mt-2" style="white-space:pre-line">${esc(post.content)}</p>
            ${imageHtml}
            <p class="has-text-grey is-size-7 mt-3">
                ${post.author ? esc(post.author) + ' · ' : ''}${new Date(post.created_at).toLocaleString('ru')}
            </p>
            ${actions}
        </div>`;
}

function renderNote(note) {
    _noteCache[note.uuid] = note;
    return `
        <div class="box post-card" style="border-left:4px solid #485fc7">
            <p class="is-size-5 has-text-weight-semibold">${esc(note.title)}</p>
            <p class="mt-2" style="white-space:pre-line">${esc(note.content)}</p>
            <p class="has-text-grey is-size-7 mt-3">${new Date(note.created_at).toLocaleString('ru')}</p>
            <div class="buttons are-small mt-3">
                <button class="button is-small is-outlined" onclick="startEditNote('${note.uuid}')">Редактировать</button>
                <button class="button is-small is-danger is-outlined" onclick="deleteNote('${note.uuid}')">Удалить</button>
            </div>
        </div>`;
}

function updateFileName(input, nameId) {
    document.getElementById(nameId).textContent = input.files.length ? input.files[0].name : 'Не выбрано';
}

function esc(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ---- Boot ----

if (token) {
    initApp();
} else {
    document.getElementById('page-auth').style.display = '';
}
