const updates = [
  {
    date: "2025-01-16",
    title: "Bakugo & Deku – Monthly Pack",
    description: "Bakugo and Deku are part of this month’s pack! You know where to see it 😊",
    image: "imagenes/bakugo.jpeg",
    twitter: "https://twitter.com/footparadise/status/2005032550725800188"
  },
  {
    date: "2025-01-15",
    title: "New content available",
    description: "Daily Footparadise post is live!",
    twitter: "https://twitter.com/footparadise"
  }
];

const today = new Date().toISOString().slice(0, 10);
const feed = document.getElementById("feed");

updates.forEach(item => {
  const card = document.createElement("div");
  card.className = "card" + (item.date === today ? " today" : "");

  const imageHTML = item.image
    ? `<img src="${item.image}" class="thumb" data-image="${item.image}" />`
    : `<div class="thumb placeholder"></div>`;

  card.innerHTML = `
    <div class="row">
      ${imageHTML}
      <div class="content">
        <small>${item.date === today ? "TODAY · " : ""}${item.date}</small>
        <h2>${item.title}</h2>
        <p>${item.description || ""}</p>
        <a class="button" href="${item.twitter}" target="_blank">Open on Twitter</a>
      </div>
    </div>
  `;

  feed.appendChild(card);
});

// Modal logic
const modal = document.getElementById("imageModal");
const modalImage = document.getElementById("modalImage");

document.addEventListener("click", (e) => {
  const img = e.target.closest(".thumb[data-image]");
  if (img) {
    modalImage.src = img.dataset.image;
    modal.classList.remove("hidden");
  }

  if (e.target.classList.contains("modal-backdrop")) {
    modal.classList.add("hidden");
  }
});
