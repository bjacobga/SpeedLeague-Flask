document.addEventListener("DOMContentLoaded", () => {
    // --- Run Table Filtering ---
    const gameFilter = document.getElementById("game-filter");
    const categoryFilter = document.getElementById("category-filter");
    const table = document.getElementById("runs-table");

    if (table && gameFilter && categoryFilter) {
        const rows = Array.from(table.tBodies[0].rows);

        function filterTable() {
            const gameValue = gameFilter.value;
            const categoryValue = categoryFilter.value;

            rows.forEach(row => {
                const game = row.cells[2].textContent;
                const category = row.cells[3].textContent;

                if ((gameValue === "" || game === gameValue) &&
                    (categoryValue === "" || category === categoryValue)) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            });
        }

        gameFilter.addEventListener("change", filterTable);
        categoryFilter.addEventListener("change", filterTable);
    }

    // --- Dark Mode Toggle ---
    const toggleButton = document.getElementById("dark-mode-toggle");

    if (toggleButton) {
        // Load saved preference
        if (localStorage.getItem("dark-mode") === "true") {
            document.body.classList.add("dark-mode");
        }

        toggleButton.addEventListener("click", () => {
            document.body.classList.toggle("dark-mode");
            // Save preference
            localStorage.setItem(
                "dark-mode",
                document.body.classList.contains("dark-mode")
            );
        });
    }
});


