let existingProfileChart = null;
let existingLatestResult = null;

function renderExistingResultCharts(result) {
    existingLatestResult = result;
    existingProfileChart?.destroy();

    existingProfileChart = createProfileBarChart("existingProfileChart", result.raw_features || {});
}

function resizeExistingCharts() {
    existingProfileChart?.resize();
}

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("existingPredictBtn");
    const input = document.getElementById("existingMemberNo");
    const chartAccordion = document.getElementById("existingChartAccordion");

    btn?.addEventListener("click", async () => {
        const memberNo = input?.value.trim() || "";
        if (!memberNo) {
            alert("회원 번호를 입력해 주시기 바랍니다.");
            input?.focus();
            return;
        }

        btn.disabled = true;
        btn.textContent = "예측 중입니다...";

        try {
            const response = await fetch("/api/predict/existing", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ member_no: memberNo })
            });
            const data = await response.json();
            if (!data.ok) {
                throw new Error(data.message || "예측 중 오류가 발생했습니다.");
            }
            setResult("existingResultPanel", "existing", data.result);
            renderExistingResultCharts(data.result);
        } catch (error) {
            alert(error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = "예측하기";
        }
    });

    input?.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            btn?.click();
        }
    });

    chartAccordion?.addEventListener("toggle", () => {
        if (chartAccordion.open && existingLatestResult) {
            setTimeout(resizeExistingCharts, 80);
        }
    });

    window.addEventListener("resize", resizeExistingCharts);
});
