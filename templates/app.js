(function () {
    const deleteScrollKey = "video-manager-delete-scroll-y";

    window.addEventListener("pageshow", function () {
        let savedScrollY = null;
        try {
            savedScrollY = window.sessionStorage.getItem(deleteScrollKey);
            window.sessionStorage.removeItem(deleteScrollKey);
        } catch (error) {}
        if (savedScrollY === null) return;

        const scrollY = Number(savedScrollY);
        if (!Number.isFinite(scrollY) || scrollY < 0) return;
        window.requestAnimationFrame(function () {
            const root = document.documentElement;
            const previousScrollBehavior = root.style.scrollBehavior;
            root.style.scrollBehavior = "auto";
            window.scrollTo(0, scrollY);
            window.requestAnimationFrame(function () {
                root.style.scrollBehavior = previousScrollBehavior;
            });
        });
    }, { once: true });

    function updateThemeButtons() {
        const dark = document.documentElement.dataset.theme === "dark";
        document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
            const label = button.querySelector("[data-theme-label]");
            if (label) label.textContent = dark ? "亮色模式" : "深色模式";
            button.setAttribute("aria-pressed", String(dark));
        });
    }
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
        button.addEventListener("click", function () {
            const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
            document.documentElement.dataset.theme = next;
            try { localStorage.setItem("video-manager-theme", next); } catch (error) {}
            updateThemeButtons();
        });
    });
    updateThemeButtons();

    document.querySelectorAll("[data-file-input]").forEach(function (input) {
        input.addEventListener("change", function () {
            const label = input.closest(".file-picker").querySelector("[data-file-label]");
            const count = input.files ? input.files.length : 0;
            label.textContent = count === 0 ? "選擇媒體檔案" : count === 1 ? input.files[0].name : "已選擇 " + count + " 個檔案";
        });
    });

    document.querySelectorAll("form[data-busy-label]").forEach(function (form) {
        form.addEventListener("submit", function () {
            const button = form.querySelector("button[type='submit']");
            const label = button && button.querySelector("[data-submit-label]");
            if (!button) return;
            button.disabled = true;
            button.classList.add("is-busy");
            if (label) label.textContent = form.dataset.busyLabel;
        });
    });

    document.querySelectorAll("[data-autosubmit]").forEach(function (control) {
        control.addEventListener("change", function () {
            const form = control.closest("form");
            form.setAttribute("aria-busy", "true");
            form.classList.add("is-submitting");
            form.requestSubmit();
        });
    });

    document.querySelectorAll(".delete-form").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!window.confirm("確定要從本機媒體庫永久刪除這個檔案嗎？")) {
                event.preventDefault();
                return;
            }
            try {
                window.sessionStorage.setItem(deleteScrollKey, String(window.scrollY));
            } catch (error) {}
            const button = form.querySelector("button[type='submit']");
            if (button) {
                button.disabled = true;
                button.classList.add("is-busy");
                const label = button.querySelector("[data-submit-label]");
                if (label) label.textContent = "刪除中…";
            }
        });
    });

    document.querySelectorAll("[data-library]").forEach(function (library) {
        const input = library.querySelector("[data-library-search]");
        if (!input) return;
        const cards = Array.from(library.querySelectorAll("[data-media-card]"));
        const empty = library.querySelector("[data-no-results]");
        const count = library.querySelector("[data-result-count]");
        function filterCards() {
            const query = input.value.trim().toLocaleLowerCase("zh-Hant");
            let visible = 0;
            cards.forEach(function (card) {
                const matches = !query || (card.dataset.name || "").toLocaleLowerCase("zh-Hant").includes(query);
                card.hidden = !matches;
                if (matches) visible += 1;
            });
            library.querySelectorAll("[data-media-section]").forEach(function (section) {
                section.hidden = !Array.from(section.querySelectorAll("[data-media-card]")).some(function (card) { return !card.hidden; });
            });
            if (empty) empty.hidden = visible !== 0;
            if (count) count.textContent = visible + " 個項目";
        }
        input.addEventListener("input", filterCards);
        library.querySelectorAll("[data-clear-filters]").forEach(function (button) {
            button.addEventListener("click", function () { input.value = ""; filterCards(); input.focus(); });
        });
    });
})();
