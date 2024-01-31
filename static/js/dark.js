// Inspiration: https://www.cssscript.com/dark-mode-switcher-bootstrap-5/

function isDarkTheme() {
    let setting = localStorage.getItem("dark-theme");
    if (setting !== null) {
        return setting;
    }
    const darkThemeMq = window.matchMedia("(prefers-color-scheme: dark)");
    if (darkThemeMq.matches) {
        return "1";
    }
    return "0";
}

// Docstring
/**
 * Set the theme of the website to dark or light mode
 * @param {number} isDark - Whether to set the theme to dark mode
 */
function setTheme(isDark) {
    document.documentElement.setAttribute(
        "data-bs-theme", isDark ? "dark" : "light"
    );
    localStorage.setItem("dark-theme", String(isDark));
}

function setupDarkTheme() {
    setTheme(parseInt(isDarkTheme()));
}

// Supposed to be called using an HTML onload attribute
function setupLightSwitch() {
    function onSwitchTheme() {
        setTheme(isDark=Number(this.checked));
        icons = this.parentElement.querySelectorAll("svg");
        // Unary operator to convert bool to int
        value = +this.checked;
        icons[value].classList.remove("d-none");
        icons[1 - value].classList.add("d-none");
    }

    let lightSwitch = document.getElementById("light-switch");
    lightSwitch.addEventListener("change", onSwitchTheme);
    lightSwitch.checked = parseInt(isDarkTheme());
    onSwitchTheme.call(lightSwitch);
}

setupDarkTheme();
