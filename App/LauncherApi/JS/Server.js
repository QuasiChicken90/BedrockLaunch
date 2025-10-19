async function loadServers() {
  const container = document.querySelector(".ServerList");
  container.innerHTML = "<h1 style='color:white;'>Loading servers...</h1>";

  try {
    const res = await fetch("/launcher/api/servers/getlist");
    const servers = await res.json();

    container.innerHTML = ""; 

    servers.forEach(server => {
      const div = document.createElement("div");
      div.classList.add("ServerContainer");
      div.innerHTML = `
        <h3>${server.name}</h3>
        <h4>${server.ip}:${server.port}</h4>
        <h5>${server.online ? 
              `${server.players_online} online right now` : 
              "Offline"}</h5>
      `;
      container.appendChild(div);
    });

  } catch (err) {
    container.innerHTML = `<p style="color:red;">Failed to load servers: ${err}</p>`;
  }
}
