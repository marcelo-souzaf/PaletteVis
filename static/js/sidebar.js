var path = window.location.pathname;
var categories = path.split("/").slice(1);

addEventListener("DOMContentLoaded", (event) => {
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
