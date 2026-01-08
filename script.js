const updates = [
     {
    date: "2026-1-7",
    title: "Vote to choose the characters for the next story!",
    description: `We have so many ideas in mind 😁
- Asta and Yami (Black Clover)
- Killua and Gon (Hunter x Hunter)
- Prof Cerise with Ash and Goh (Pokemon Journeys)
- Tetsuru with Hinata and Kageyama (Haikyuu)`,
    image: "imagenes/polltw.jpg",
    twitter: "https://x.com/FootParadiseArt/status/2009017540417343733"
  },
    {
    date: "2026-1-4",
    title: "First comm of the year 🎉",
    description: `Pawbert Lynxley from Zootopia about to fall, what a great view!`,
    image: "imagenes/zootopia.jfif",
    twitter: "https://x.com/FootParadiseArt/status/2007943360083100120"
  },
     {
    date: "2026-1-3",
    title: "How is everyone doing?",
    description: `Remember, you can still read our latest comic 😊
What could Goku and Gohan have been up to? A new story is coming this month!`,
    image: "imagenes/comic.jfif",
    twitter: "https://x.com/FootParadiseArt/status/2007567500716978372"
  },
    {
    date: "2026-1-3",
    title: "New Comic: Gohan´s Wish",
    description: `Our new story is out now, Gohan’s Wish! 
Gohan reunites with Goku, and the two share a great moment, playing with their feet 😉`,
    image: "imagenes/gohan_wish.jfif",
    twitter: "https://x.com/FootParadiseArt/status/2004301696328216922"
  },
   {
    date: "2025-12-30",
    title: "Happy New Year",
    description: `Tanjiro and Inosuke say goodbye to the year with Tengen Uzui!
Our last illustration of the year, thank you all for the amazing support! More coming next year! 🥂`,
    image: "imagenes/newyear.jfif",
    twitter: "https://x.com/FootParadiseArt/status/2006119167112470598"
  },
  {
    date: "2025-12-29",
    title: "December’s reward",
    description: `Last days to check out December’s reward, did you like this month’s characters? 🙌
- Hinata and Nishinoya
- Android 17
- Bakugo and Deku
- New comic starring Goku and Gohan.`,
    image: "imagenes/dec_rewards.jpeg",
    twitter: "https://twitter.com/footparadise/status/2005427232270086412"
  },
  {
    date: "2025-12-28",
    title: "New content available",
    description: "Bakugo and Deku are part of this month’s pack! You know where to see it ",
    image: "imagenes/bakugo.jpeg",
    twitter: "https://twitter.com/footparadise/status/2005032550725800188"
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
