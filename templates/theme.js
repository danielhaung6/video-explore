(function () {
    const storageKey = "video-manager-theme";
    let theme = "light";

    try {
        const savedTheme = localStorage.getItem(storageKey);
        if (savedTheme === "light" || savedTheme === "dark") {
            theme = savedTheme;
        }
    } catch (error) {
        // The theme still works for this page when storage is unavailable.
    }

    document.documentElement.dataset.theme = theme;

})();
