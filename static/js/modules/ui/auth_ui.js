// Auth and role-based UI toggling for SEIM frontend

export function updateAuthUI() {
    const authElements = document.querySelectorAll('.auth-only');
    authElements.forEach(el => el.style.display = 'block');
    const unauthElements = document.querySelectorAll('.unauth-only');
    unauthElements.forEach(el => el.style.display = 'none');
}

export function updateUnauthUI() {
    const authElements = document.querySelectorAll('.auth-only');
    authElements.forEach(el => el.style.display = 'none');
    const unauthElements = document.querySelectorAll('.unauth-only');
    unauthElements.forEach(el => el.style.display = 'block');
}

export function updateUserInterface(userData) {
    const usernameElements = document.querySelectorAll('.user-username');
    usernameElements.forEach(el => {
        el.textContent = userData.username;
    });
    const roleElements = document.querySelectorAll('.user-role');
    roleElements.forEach(el => {
        el.textContent = userData.role;
    });
    const emailElements = document.querySelectorAll('.user-email');
    emailElements.forEach(el => {
        el.textContent = userData.email;
    });
    updateRoleBasedUI(userData.role);
}

export function updateRoleBasedUI(role) {
    const roleElements = document.querySelectorAll('[data-role]');
    roleElements.forEach(el => {
        el.style.display = 'none';
    });
    const currentRoleElements = document.querySelectorAll(`[data-role="${role}"]`);
    currentRoleElements.forEach(el => {
        el.style.display = 'block';
    });
    if (role === 'admin') {
        const adminElements = document.querySelectorAll('[data-role="admin"]');
        adminElements.forEach(el => {
            el.style.display = 'block';
        });
    }
} 