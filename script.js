const updates = [
  {
    date: "2025-01-15",
    title: "New content available",
    description: "Daily Footparadise post is live!",
    twitter: "https://twitter.com/footparadise"
  },
  {
    date: "2025-01-14",
    title: "Daily Drawing",
    twitter: "https://twitter.com/footparadise"
  }
];

const today = new Date().toISOString().slice(0,10);
const feed = document.getElementById("feed");

updates.forEach(item => {
  const card = document.createElement("div");
  card.className = "card" + (item.date === today ? " today" : "");

  card.innerHTML = `
    <div class="image-placeholder"></div>
    <small>${item.date === today ? "TODAY · " : ""}${item.date}</small>
    <h2>${item.title}</h2>
    <p>${item.description || ""}</p>
    <a class="button" href="${item.twitter}" target="_blank">Open on Twitter</a>
  `;

  feed.appendChild(card);
});
