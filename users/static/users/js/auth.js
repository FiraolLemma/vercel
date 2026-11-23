document.querySelectorAll(".auth-password-toggle").forEach((toggle) => {
    toggle.addEventListener("click", () => {
        const input = document.getElementById(toggle.getAttribute("aria-controls"));
        if (!input) {
            throw new Error("PIN visibility control target was not found.");
        }

        const isVisible = input.type === "text";
        input.type = isVisible ? "password" : "text";
        toggle.setAttribute("aria-label", isVisible ? toggle.dataset.showLabel : toggle.dataset.hideLabel);

        const icon = toggle.querySelector("i");
        if (!icon) {
            throw new Error("PIN visibility control icon was not found.");
        }
        icon.classList.toggle("fa-eye", isVisible);
        icon.classList.toggle("fa-eye-slash", !isVisible);
    });
});
