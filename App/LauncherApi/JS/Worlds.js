async function loadWorlds() {
    try {
        const res = await fetch("/launcher/api/worlds/getlist");
        const worlds = await res.json();
        const container = document.getElementById("WorldContainter");
        container.innerHTML = "";

        worlds.forEach(worldName => {
            const card = document.createElement("div");
            card.className = "WorldCard";

            card.innerHTML = `
                <img src="/launcher/api/worlds/getimage/${encodeURIComponent(worldName)}" alt="${worldName}">
                <h2>${worldName}</h2>
                <h3>Size: Loading</h3>
            `;

            fetch(`/launcher/api/worlds/getsize/${encodeURIComponent(worldName)}`)
                .then(r => r.json())
                .then(data => {
                    card.querySelector("h3").textContent = `Size: ${data.size}`;
                });

            container.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load worlds");
    }
}

window.onload = loadWorlds;
