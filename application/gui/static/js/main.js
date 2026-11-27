function openGithub(event) {
    event.preventDefault();
    window.open('https://github.com', '_blank');
}

function toggleUserDropdown(event) {
    event.preventDefault();
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown.classList.contains('hidden')) {
        dropdown.classList.remove('hidden');
    } else {
        dropdown.classList.add('hidden');
    }
}

function toggleSettingsOverlay(event) {
    event.preventDefault();
    const overlay = document.getElementById('settings-overlay');
    if (overlay.classList.contains('hidden')) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const loadingScreen = document.getElementById('loading-screen');
    if (loadingScreen) {
        loadingScreen.style.display = 'none';
    }
});