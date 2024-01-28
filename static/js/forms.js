addEventListener("DOMContentLoaded", function() {
    defaultsForm = document.getElementById("defaults-form");
    if (defaultsForm) {
        // Function exists simply to handle an AJAX request, which does not redirect to a new page
        defaultsForm.addEventListener("submit", function(event) {
            event.preventDefault();

            fetch("/set-default", {
                method: "POST",
                body: new FormData(this),
            });
        });
        return;
    }

    document.getElementById("main-title").innerHTML = categories.join(".");

    // Select all forms and listen to their changes, then get
    // the image data as bytes from the server and update the display
    forms = document.querySelectorAll(".palette-form");
    forms.forEach(form => {
        form.addEventListener("change", function() {
            let formData = new FormData(this);
            formData.append("categories", categories);
            formData.append("id", this.id);

            fetch("/get-palette", {
                method: "POST",
                body: formData
            })
            .then(response => response.text())
            .then(data => {
                let img_frame = this.querySelector(".palette-display");
                // -1 for reversed order
                img_frame.style.transform = `scale(${this.order.value}, 1)`;
                img_frame.innerHTML = data;
            });
        });

        // Trigger the event to show the palette initially
        form.dispatchEvent(new Event("change"));
    });
});
