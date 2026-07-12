document.addEventListener("DOMContentLoaded", () => {
  const tips = document.querySelectorAll(".tips li");
  tips.forEach((tip, index) => {
    tip.style.transitionDelay = `${index * 0.2}s`;
    tip.classList.add("fade-in");
  });
});
// Floating game button
document.addEventListener('DOMContentLoaded', () => {
  const gameIcon = document.createElement('img');
  gameIcon.src = '/static/images/game-icon.png'; // Replace with your icon image path
  gameIcon.alt = 'Play Jungle Game';
  gameIcon.id = 'floating-game-icon';
  gameIcon.title = 'Play Jungle Game!';

  gameIcon.addEventListener('click', () => {
    window.location.href = '/jungle-game';
  });

  document.body.appendChild(gameIcon);
});
