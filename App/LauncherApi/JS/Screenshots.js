API_BASE = 'http://localhost:21934';

function getImageUrl(fullPath) {
    const match = fullPath.match(/Minecraft Bedrock[\\/]Users[\\/](.+)/);
    if (!match) return null;
    const relative = match[1]
    .replace(/\\/g, '/')
    .split('/')
    .map(seg => encodeURIComponent(seg))
    .join('/');
    return `${API_BASE}/launcher/api/screenshots/getimage/${relative}`;
}

function getFileName(fullPath) {
    return fullPath.split(/[\\/]/).pop();
}

async function loadScreenshots() {
var container = document.getElementById('ScreenshotsContainer');
try {
var response = await fetch(`${API_BASE}/launcher/api/screenshots/getlist`);
var paths = await response.json();

if (!paths || paths.length === 0) {
    container.innerHTML = '<div class="empty-state">No screenshots found.</div>';
    return;
}

paths.forEach(fullPath => {
    var imgUrl = getImageUrl(fullPath);
    if (!imgUrl) return;

    var card = document.createElement('div');
    card.classList.add('ScreenshotCard');

    card.innerHTML = `<img src="${imgUrl}" alt="${getFileName(fullPath)}" loading="lazy">`;
    container.appendChild(card);
});

} catch (err) {
container.innerHTML = `<div class="empty-state">Could not load screenshots.<br><small style="opacity:0.5;">${err.message}</small></div>`;
}
}