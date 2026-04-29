let directProfileChart = null;
let directLatestResult = null;

function renderDirectResultCharts(result) {
    directLatestResult = result;
    directProfileChart?.destroy();

    directProfileChart = createProfileBarChart("directProfileChart", result.raw_features || {});
}

function resizeDirectCharts() {
    directProfileChart?.resize();
}

document.addEventListener("DOMContentLoaded", () => {
    fillSelectOptions();

    const btn = document.getElementById("directPredictBtn");
    const form = document.getElementById("directPredictForm");
    const chartAccordion = document.getElementById("directChartAccordion");

    btn?.addEventListener("click", async () => {
        if (!form) return;

        const payload = {};
        new FormData(form).forEach((value, key) => {
            payload[key] = Number(value);
        });

        btn.disabled = true;
        btn.textContent = "예측 중입니다...";

        try {
            const response = await fetch("/api/predict/direct", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (!data.ok) {
                throw new Error(data.message || "예측 중 오류가 발생했습니다.");
            }
            setResult("directResultPanel", "direct", data.result);
            renderDirectResultCharts(data.result);
        } catch (error) {
            alert(error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = "예측하기";
        }
    });

    chartAccordion?.addEventListener("toggle", () => {
        if (chartAccordion.open && directLatestResult) {
            setTimeout(resizeDirectCharts, 80);
        }
    });

    window.addEventListener("resize", resizeDirectCharts);
});
