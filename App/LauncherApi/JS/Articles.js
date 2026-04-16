function loadNews() {
    fetch('https://launchercontent.mojang.com/news.json')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('NewsContainer');
            data.entries.forEach(entry => {
                const card = document.createElement('div');
                card.classList.add('NewsCard');
                const imageUrl = entry.playPageImage?.url ? `https://launchercontent.mojang.com${entry.playPageImage.url}` : '';
                const imageHTML = imageUrl ? entry.readMoreLink ? `
                    <img src="${imageUrl}" alt="${entry.title}" onclick="window.open('${entry.readMoreLink}', '_blank')">` : `
                        <img src="${imageUrl}" alt="${entry.title}">` : '';
                card.innerHTML = `
${imageHTML}
                            <h2>${entry.title}</h2>
                            <h3>${entry.date}</h3>
                            <h4>${entry.text}</h4>
`;
                container.appendChild(card);
            });
        });
}
