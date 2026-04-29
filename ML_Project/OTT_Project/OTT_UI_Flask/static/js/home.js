let homeChartsLoaded = false;
let homeChartInstances = [];

function createCarousel({ trackId, dotsId, prevId, nextId, totalSlides, onChange }) {
    const track = document.getElementById(trackId);
    const dots = [...document.querySelectorAll(`#${dotsId} button`)];
    const prevButton = document.getElementById(prevId);
    const nextButton = document.getElementById(nextId);

    if (!track) {
        return {
            update: () => {},
            current: () => 0,
        };
    }

    let currentIndex = 0;

    const update = (index) => {
        currentIndex = (index + totalSlides) % totalSlides;
        track.style.transform = `translateX(-${currentIndex * 100}%)`;
        dots.forEach((dot, idx) => dot.classList.toggle("active", idx === currentIndex));
        if (typeof onChange === "function") onChange(currentIndex);
    };

    prevButton?.addEventListener("click", () => update(currentIndex - 1));
    nextButton?.addEventListener("click", () => update(currentIndex + 1));
    dots.forEach((dot, index) => dot.addEventListener("click", () => update(index)));

    let startX = 0;
    const section = track.closest(".hero-carousel");
    section?.addEventListener("touchstart", (event) => {
        startX = event.changedTouches[0].clientX;
    }, { passive: true });

    section?.addEventListener("touchend", (event) => {
        const endX = event.changedTouches[0].clientX;
        const diff = endX - startX;
        if (Math.abs(diff) < 40) return;
        update(currentIndex + (diff < 0 ? 1 : -1));
    }, { passive: true });

    update(0);

    return {
        update,
        current: () => currentIndex,
    };
}

function resizeHomeCharts() {
    homeChartInstances.forEach((chart) => chart?.resize());
}

async function loadHomeCharts() {
    if (homeChartsLoaded) return;

    try {
        const charts = await fetchCharts();
        homeChartInstances = [
            createDoughnutChart("homeRiskChart", charts.risk.labels, charts.risk.values, {
                legendPosition: "bottom",
                centerLabel: "사용자 비율",
                centerValue: "분포",
                glowColor: "rgba(46, 217, 163, 0.34)",
                cutout: "72%",
                dynamicCenter: false,
                hideAllId: "homeRiskHideAll",
                showAllId: "homeRiskShowAll"
            }),
            createDoughnutChart("homeFeeChart", charts.fee.labels, charts.fee.values, {
                legendPosition: "bottom",
                centerLabel: "결제액",
                centerValue: "분포",
                glowColor: "rgba(118, 185, 255, 0.28)",
                cutout: "72%",
                hideAllId: "homeFeeHideAll",
                showAllId: "homeFeeShowAll"
            }),
            createDoughnutChart("homeFreqChart", charts.frequency.labels, charts.frequency.values, {
                legendPosition: "bottom",
                centerLabel: "이용 빈도",
                centerValue: "패턴",
                glowColor: "rgba(154, 137, 255, 0.28)",
                cutout: "72%",
                hideAllId: "homeFreqHideAll",
                showAllId: "homeFreqShowAll"
            })
        ].filter(Boolean);

        homeChartsLoaded = true;
        setTimeout(resizeHomeCharts, 120);
    } catch (error) {
        console.error(error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    createCarousel({
        trackId: "featureCarouselTrack",
        dotsId: "featureCarouselDots",
        prevId: "featureCarouselPrev",
        nextId: "featureCarouselNext",
        totalSlides: 2,
    });

    document.querySelectorAll('.chart-accordion').forEach((accordion) => {
        accordion.addEventListener('toggle', () => {
            if (accordion.open) {
                loadHomeCharts();
                setTimeout(resizeHomeCharts, 120);
            }
        });
    });

    window.addEventListener("resize", () => {
        resizeHomeCharts();
    });
});
