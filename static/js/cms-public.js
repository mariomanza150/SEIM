(function () {
    function initCarousel(el) {
        if (!el || el.dataset.cmsCarouselInit) {
            return;
        }
        el.dataset.cmsCarouselInit = "1";

        var reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        if (reducedMotion) {
            el.removeAttribute("data-bs-ride");
            el.setAttribute("data-bs-interval", "false");
        }

        var carousel = bootstrap.Carousel.getOrCreateInstance(el, {
            ride: reducedMotion ? false : el.getAttribute("data-bs-ride"),
            interval: reducedMotion ? false : el.getAttribute("data-bs-interval"),
        });

        var section = el.closest("section");
        var pauseBtn = section ? section.querySelector("[data-cms-carousel-pause]") : null;
        if (!pauseBtn) {
            return;
        }

        var paused = reducedMotion;

        function updateLabel() {
            pauseBtn.setAttribute("aria-pressed", paused ? "true" : "false");
            pauseBtn.textContent = paused ? "Reanudar" : "Pausar";
        }

        updateLabel();
        pauseBtn.addEventListener("click", function () {
            if (paused) {
                carousel.cycle();
                paused = false;
            } else {
                carousel.pause();
                paused = true;
            }
            updateLabel();
        });
    }

    function initYoutubeFacades() {
        document.querySelectorAll("[data-cms-youtube-facade]").forEach(function (wrapper) {
            var trigger = wrapper.querySelector(".cms-youtube-facade__trigger");
            if (!trigger || trigger.dataset.cmsYoutubeInit) {
                return;
            }
            trigger.dataset.cmsYoutubeInit = "1";
            trigger.addEventListener("click", function () {
                var embedUrl = trigger.getAttribute("data-embed-url");
                if (!embedUrl) {
                    return;
                }
                var iframe = document.createElement("iframe");
                iframe.src = embedUrl + (embedUrl.indexOf("?") >= 0 ? "&" : "?") + "autoplay=1";
                iframe.title = trigger.getAttribute("aria-label") || "Video CGRI";
                iframe.allow =
                    "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
                iframe.allowFullscreen = true;
                iframe.className = "w-100 h-100";
                wrapper.innerHTML = "";
                wrapper.appendChild(iframe);
            });
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".cms-carousel").forEach(initCarousel);
        initYoutubeFacades();
    });
})();
