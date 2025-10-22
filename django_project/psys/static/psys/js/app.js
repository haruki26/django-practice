document.addEventListener("DOMContentLoaded", () => {
  const focusTargets = document.querySelectorAll("[data-auto-focus]");
  if (focusTargets.length > 0) {
    focusTargets[0].focus();
  }

  const dismissButtons = document.querySelectorAll("[data-dismiss]");
  dismissButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const target = document.getElementById(button.dataset.dismiss ?? "");
      if (target) {
        target.remove();
      }
    });
  });
});
