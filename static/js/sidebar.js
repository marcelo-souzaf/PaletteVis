var path = window.location.pathname;
var categories = path.split("/").slice(1);

// Inspiration: https://www.cssscript.com/dark-mode-switcher-bootstrap-5/
function setupDarkMode() {
    let lightSwitch = document.getElementById("light-switch");
    if (!lightSwitch) {
        return;
    }

    function onSwitchMode() {
        document.documentElement.setAttribute(
            "data-bs-theme", this.checked ? "dark" : "light"
        );
        icons = this.parentElement.querySelectorAll("svg");
        // Unary operator to convert to int
        value = +this.checked;
        icons[value].classList.remove("d-none");
        icons[1 - value].classList.add("d-none");

        localStorage.setItem("dark-mode", String(value));
    }

    function isSystemDarkMode() {
        const darkThemeMq = window.matchMedia("(prefers-color-scheme: dark)");
        if (darkThemeMq.matches) {
            return "1";
        }
        return "0";
    }

    let setting = localStorage.getItem("dark-mode");
    if (setting === null) {
        setting = isSystemDarkMode();
    }
    lightSwitch.checked = parseInt(setting);

    lightSwitch.addEventListener("change", onSwitchMode);
    onSwitchMode.call(lightSwitch);
}

addEventListener("DOMContentLoaded", (event) => {
    setupDarkMode();

    // Expand the category in the sidebar if there is a selected subcategory
    // Only applies if there is a nested category
    if (categories.length >= 2) {
        let link = document.querySelector(`li a[href='${path}']`);
        if (link) {
            let ancestor = link.parentElement.closest(".mb-1");
            ancestor.querySelector("button").setAttribute("aria-expanded", "true");
            ancestor.querySelector("div").classList.add("show");
        }
    }
});
