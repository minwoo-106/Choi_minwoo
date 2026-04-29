const CODE_MAPS = {
    GENDER: { 1: "남자", 2: "여자" },
    AGE_GROUP: { 1: "10대", 2: "20대", 3: "30대", 4: "40대", 5: "50대", 6: "60대", 7: "70세 이상" },
    INCOME_GROUP: { 1: "100만원 미만", 2: "100~199만원", 3: "200~299만원", 4: "300~399만원", 5: "400~499만원", 6: "500~599만원", 7: "600만원 이상", 9: "무응답" },
    FAMILY_TYPE: { 1: "1인가구", 2: "1세대가구", 3: "2세대가구", 4: "3세대가구", 5: "기타" },
    MONTHLY_FEE_CODE: { 1: "3,000원 미만", 2: "3,000원 이상 ~ 5,000원 미만", 3: "5,000원 이상 ~ 7,000원 미만", 4: "7,000원 이상 ~ 10,000원 미만", 5: "10,000원 이상 ~ 13,000원 미만", 6: "13,000원 이상 ~ 15,000원 미만", 7: "15,000원 이상", 8: "지인 계정 사용" },
    HAS_AD_PLAN: { 1: "예", 2: "아니오" },
    AD_INTENT: { 1: "전혀 이용하지 않을 것 같다", 2: "별로 이용하지 않을 것 같다", 3: "보통이다", 4: "이용할 것 같다", 5: "반드시 이용할 생각이다" },
    USE_FREQUENCY: { 1: "매일", 2: "주 4~6일", 3: "주 2~3일", 4: "주 1일", 5: "월 1~3일", 6: "2~3달에 1~2일 이하" },
    WEEKDAY_TIME_CODE: { 1: "06:00~08:59", 2: "09:00~11:59", 3: "12:00~13:59", 4: "14:00~16:59", 5: "17:00~19:59", 6: "20:00~22:59", 7: "23:00~01:59", 8: "주중에 이용하지 않음" },
    WEEKEND_TIME_CODE: { 1: "06:00~08:59", 2: "09:00~11:59", 3: "12:00~13:59", 4: "14:00~16:59", 5: "17:00~19:59", 6: "20:00~22:59", 7: "23:00~01:59", 8: "주말에 이용하지 않음" },
    SEARCH_VIEW: { 1: "전혀 그렇지 않다", 2: "그렇지 않은 편이다", 3: "보통이다", 4: "그런 편이다", 5: "매우 그렇다" },
    RECOMMEND_VIEW: { 1: "전혀 그렇지 않다", 2: "그렇지 않은 편이다", 3: "보통이다", 4: "그런 편이다", 5: "매우 그렇다" },
    BINGE_WATCH: { 1: "전혀 그렇지 않다", 2: "그렇지 않은 편이다", 3: "보통이다", 4: "그런 편이다", 5: "매우 그렇다" }
};

const DEFAULTS = {
    GENDER: 1,
    AGE_GROUP: 2,
    INCOME_GROUP: 4,
    FAMILY_TYPE: 1,
    MONTHLY_FEE_CODE: 4,
    HAS_AD_PLAN: 2,
    AD_INTENT: 3,
    USE_FREQUENCY: 3,
    WEEKDAY_TIME_CODE: 6,
    WEEKEND_TIME_CODE: 6,
    SEARCH_VIEW: 3,
    RECOMMEND_VIEW: 4,
    BINGE_WATCH: 3
};

const CHART_COLORS = ["#49E6D1", "#FFBE55", "#FF70A8", "#52B8FF", "#AE6BFF", "#61D9FF", "#7C86FF", "#D88CFF"];

if (window.Chart) {
    Chart.defaults.color = "#ECF3FF";
    Chart.defaults.borderColor = "rgba(129, 185, 255, 0.18)";
    Chart.defaults.font.family = 'Pretendard, system-ui, -apple-system, BlinkMacSystemFont, sans-serif';
}

function fillSelectOptions() {
    document.querySelectorAll("[data-fill-options]").forEach((select) => {
        const key = select.dataset.fillOptions;
        const options = CODE_MAPS[key] || {};
        const html = Object.entries(options)
            .map(([value, label]) => `<option value="${value}">${label}</option>`)
            .join("");
        select.innerHTML = html;
        if (DEFAULTS[key] !== undefined) {
            select.value = String(DEFAULTS[key]);
        }
    });
}

function riskColor(label) {
    if (label === "안정") return "#2ED9A3";
    if (label === "주의") return "#F6B454";
    return "#F56D8B";
}

function formatProbabilityBars(container, probabilities) {
    const order = ["안정", "주의", "위험"];
    container.innerHTML = order.map((label) => {
        const value = Number(probabilities?.[label] ?? 0);
        return `
            <div class="prob-item">
                <div class="prob-row">
                    <span>${label}</span>
                    <span>${value.toFixed(2)}%</span>
                </div>
                <div class="prob-track">
                    <div class="prob-fill" style="width:${value}%; background:${riskColor(label)}"></div>
                </div>
            </div>
        `;
    }).join("");
}

function formatSummary(container, summary) {
    const items = Array.isArray(summary)
        ? summary
        : Object.entries(summary || {}).map(([label, value]) => ({ label, value }));

    container.innerHTML = items
        .map((item) => `
            <div class="summary-item">
                <span>${item.label}</span>
                <strong>${item.value}</strong>
            </div>
        `)
        .join("");
}

function formatReasons(container, reasons) {
    container.innerHTML = (reasons || [])
        .map((reason) => `<li>${reason}</li>`)
        .join("");
}

function smoothScrollTo(el) {
    if (!el) return;
    requestAnimationFrame(() => {
        el.scrollIntoView({ behavior: "smooth", block: "start" });
    });
}

function createDoughnutChart(canvasId, labels, values, options = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const total = values.reduce((acc, cur) => acc + cur, 0) || 1;
    const chartColors = labels.map((_, idx) => options.colors?.[idx] || CHART_COLORS[idx % CHART_COLORS.length]);

    const getPctText = (index) => `${((Number(values[index] || 0) / total) * 100).toFixed(1)}%`;
    const getLabelText = (index) => labels[index] || "";
    const getVisibleIndices = (chart) => labels
        .map((_, index) => index)
        .filter((index) => chart.getDataVisibility(index));

    const futuristicPlugin = {
        id: `futuristicCenter_${canvasId}`,
        afterDatasetsDraw(chart) {
            const meta = chart.getDatasetMeta(0);
            const arc = meta?.data?.find((_, index) => chart.getDataVisibility(index)) || meta?.data?.[0];
            if (!arc) return;

            const { ctx } = chart;
            const x = arc.x;
            const y = arc.y;
            const innerRadius = arc.innerRadius;
            const state = chart.$centerState || { value: options.centerValue || `${Math.round(total)}`, label: options.centerLabel || "전체" };
            const valueText = state.value || "";
            const labelText = state.label || "";

            ctx.save();
            const glow = options.glowColor || "rgba(118, 185, 255, 0.26)";
            const grad = ctx.createRadialGradient(x, y, innerRadius * 0.18, x, y, innerRadius * 1.05);
            grad.addColorStop(0, "rgba(255,255,255,0.14)");
            grad.addColorStop(0.55, glow);
            grad.addColorStop(1, "rgba(7, 17, 38, 0)");
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(x, y, innerRadius * 0.96, 0, Math.PI * 2);
            ctx.fill();

            ctx.strokeStyle = "rgba(208, 226, 255, 0.16)";
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(x, y, innerRadius * 0.82, 0, Math.PI * 2);
            ctx.stroke();

            if (valueText) {
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillStyle = "#F3F7FF";
                ctx.font = `700 ${Math.max(16, innerRadius * 0.24)}px Pretendard, sans-serif`;
                ctx.fillText(valueText, x, y - innerRadius * 0.08);
            }
            if (labelText) {
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillStyle = "#B9C9E8";
                ctx.font = `600 ${Math.max(10, innerRadius * 0.11)}px Pretendard, sans-serif`;
                ctx.fillText(labelText, x, y + innerRadius * 0.24);
            }
            ctx.restore();
        }
    };

    const chart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: chartColors,
                borderColor: "rgba(5, 15, 46, 0.96)",
                borderWidth: 3,
                hoverOffset: 10,
                spacing: 2,
                radius: "92%"
            }]
        },
        plugins: [futuristicPlugin],
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: options.cutout || "70%",
            layout: { padding: 10 },
            animation: {
                animateRotate: true,
                duration: 900,
                easing: "easeOutQuart"
            },
            onHover(event, activeElements, chartInstance) {
                if (!options.dynamicCenter) return;
                const hovered = activeElements?.[0]?.index;
                if (typeof hovered === "number" && chartInstance.getDataVisibility(hovered)) {
                    chartInstance.$hoveredIndex = hovered;
                } else {
                    chartInstance.$hoveredIndex = null;
                }
                updateCenterState(chartInstance);
                chartInstance.draw();
            },
            plugins: {
                legend: {
                    position: options.legendPosition || "bottom",
                    onClick(event, legendItem, legend) {
                        const chartInstance = legend.chart;
                        const index = legendItem.index;
                        chartInstance.toggleDataVisibility(index);
                        const isVisible = chartInstance.getDataVisibility(index);
                        chartInstance.$selectedIndex = isVisible ? index : null;
                        chartInstance.$hoveredIndex = null;
                        updateCenterState(chartInstance);
                        chartInstance.update();
                    },
                    labels: {
                        color: "#ECF3FF",
                        boxWidth: 13,
                        boxHeight: 13,
                        usePointStyle: true,
                        pointStyle: "circle",
                        padding: window.innerWidth <= 760 ? 14 : 18,
                        font: {
                            size: window.innerWidth <= 760 ? 13 : 14,
                            weight: "700"
                        },
                        generateLabels(chartInstance) {
                            const dataset = chartInstance.data.datasets[0];
                            const data = dataset.data || [];
                            const sum = data.reduce((acc, cur) => acc + cur, 0) || 1;
                            return chartInstance.data.labels.map((label, index) => ({
                                text: `${label} ${((data[index] / sum) * 100).toFixed(1)}%`,
                                fillStyle: dataset.backgroundColor[index],
                                strokeStyle: dataset.backgroundColor[index],
                                color: "#FFFFFF",
                                fontColor: "#FFFFFF",
                                lineWidth: 0,
                                hidden: !chartInstance.getDataVisibility(index),
                                index
                            }));
                        }
                    }
                },
                tooltip: {
                    backgroundColor: "rgba(7, 13, 31, 0.94)",
                    borderColor: "rgba(145, 175, 255, 0.18)",
                    borderWidth: 1,
                    padding: 12,
                    titleColor: "#F3F7FF",
                    bodyColor: "#DCE8FF",
                    displayColors: true,
                    callbacks: {
                        label(context) {
                            const value = Number(context.parsed || 0);
                            const pct = ((value / total) * 100).toFixed(1);
                            const unit = options.unit || "명";
                            return unit === "%"
                                ? `${context.label}: ${value.toFixed(2)}%`
                                : `${context.label}: ${value}${unit} · ${pct}%`;
                        }
                    }
                }
            }
        }
    });

    function updateCenterState(chartInstance) {
        const visibleIndices = getVisibleIndices(chartInstance);
        let value = options.centerValue || `${Math.round(total)}`;
        let label = options.centerLabel || "전체";

        if (visibleIndices.length === 0) {
            value = "";
            label = "";
        } else if (options.dynamicCenter && typeof chartInstance.$hoveredIndex === "number" && visibleIndices.includes(chartInstance.$hoveredIndex)) {
            value = getPctText(chartInstance.$hoveredIndex);
            label = getLabelText(chartInstance.$hoveredIndex);
        } else if (options.dynamicCenter && typeof chartInstance.$selectedIndex === "number" && visibleIndices.includes(chartInstance.$selectedIndex)) {
            value = getPctText(chartInstance.$selectedIndex);
            label = getLabelText(chartInstance.$selectedIndex);
        } else if (options.singleVisibleCenter === true && visibleIndices.length === 1) {
            value = getPctText(visibleIndices[0]);
            label = getLabelText(visibleIndices[0]);
        }

        chartInstance.$centerState = { value, label };
    }

    chart.$hoveredIndex = null;
    chart.$selectedIndex = null;
    updateCenterState(chart);

    const hideAllButton = options.hideAllId ? document.getElementById(options.hideAllId) : null;
    const showAllButton = options.showAllId ? document.getElementById(options.showAllId) : null;

    hideAllButton?.addEventListener("click", () => {
        labels.forEach((_, index) => {
            if (chart.getDataVisibility(index)) {
                chart.toggleDataVisibility(index);
            }
        });
        chart.$hoveredIndex = null;
        chart.$selectedIndex = null;
        updateCenterState(chart);
        chart.update();
    });

    showAllButton?.addEventListener("click", () => {
        labels.forEach((_, index) => {
            if (!chart.getDataVisibility(index)) {
                chart.toggleDataVisibility(index);
            }
        });
        chart.$hoveredIndex = null;
        chart.$selectedIndex = null;
        updateCenterState(chart);
        chart.update();
    });

    return chart;
}

function createProfileBarChart(canvasId, rawFeatures = {}) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const score = (value, max) => Math.max(0, Math.min(100, (Number(value || 0) / max) * 100));
    const scores = [
        score(7 - Number(rawFeatures.USE_FREQUENCY || 3), 6),
        score(rawFeatures.RECOMMEND_VIEW || 3, 5),
        score(rawFeatures.SEARCH_VIEW || 3, 5),
        score(rawFeatures.BINGE_WATCH || 3, 5),
        score(rawFeatures.OTT_SERVICE_COUNT || 2, 5)
    ];

    return new Chart(canvas, {
        type: "bar",
        data: {
            labels: ["이용빈도", "추천 활용", "검색 활용", "몰아보기", "OTT 다양성"],
            datasets: [{
                data: scores,
                backgroundColor: ["#2ED9A3", "#76B9FF", "#9A89FF", "#F6B454", "#6FD2C0"],
                borderRadius: 12,
                maxBarThickness: 34
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { color: "#ECF3FF" },
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: "#DCE8FF",
                        callback: (value) => `${value}`
                    },
                    grid: { color: "rgba(145, 175, 255, 0.14)" }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label(context) {
                            return `${context.label}: ${Number(context.parsed.y).toFixed(0)}점`;
                        }
                    }
                }
            }
        }
    });
}

function createProbabilityChart(canvasId, probabilities = {}) {
    const labels = ["안정", "주의", "위험"];
    const values = labels.map((label) => Number(probabilities?.[label] ?? 0));
    return createDoughnutChart(canvasId, labels, values, {
        colors: labels.map(riskColor),
        unit: "%",
        cutout: "66%"
    });
}

function setResult(panelId, prefix, result) {
    const panel = document.getElementById(panelId);
    if (!panel) return;

    panel.classList.remove("hidden");

    const badge = document.getElementById(`${prefix}RiskBadge`);
    const confidence = document.getElementById(`${prefix}Confidence`);
    const probabilityBars = document.getElementById(`${prefix}ProbabilityBars`);
    const reasons = document.getElementById(`${prefix}Reasons`);
    const summary = document.getElementById(`${prefix}Summary`);

    if (badge) {
        badge.textContent = result.risk_label;
        badge.style.background = riskColor(result.risk_label);
    }
    if (confidence) {
        const value = Number(result.confidence ?? 0);
        confidence.textContent = `${value.toFixed(2)}%`;
    }
    if (probabilityBars) {
        formatProbabilityBars(probabilityBars, result.probabilities || {});
    }
    if (reasons) {
        formatReasons(reasons, result.reasons || []);
    }
    if (summary) {
        formatSummary(summary, result.summary || []);
    }

    panel.dataset.result = JSON.stringify(result || {});
    smoothScrollTo(panel);
}

async function fetchCharts() {
    const response = await fetch("/api/charts/overview");
    const data = await response.json();
    if (!data.ok) {
        throw new Error(data.message || "차트 데이터를 불러오지 못했습니다.");
    }
    return data.charts;
}


document.addEventListener("DOMContentLoaded", () => {
    const navToggle = document.getElementById("navToggle");
    const siteNav = document.getElementById("siteNav");

    if (navToggle && siteNav) {
        const closeMenu = () => {
            navToggle.setAttribute("aria-expanded", "false");
            siteNav.classList.remove("is-open");
            document.body.classList.remove("nav-open");
        };

        navToggle.addEventListener("click", () => {
            const isOpen = navToggle.getAttribute("aria-expanded") === "true";
            navToggle.setAttribute("aria-expanded", String(!isOpen));
            siteNav.classList.toggle("is-open", !isOpen);
            document.body.classList.toggle("nav-open", !isOpen);
        });

        siteNav.querySelectorAll("a").forEach((a) => a.addEventListener("click", closeMenu));

        document.addEventListener("click", (e) => {
            if (!document.body.classList.contains("nav-open")) return;
            const t = e.target;
            if (t.closest && (t.closest('#siteNav') || t.closest('#navToggle'))) return;
            closeMenu();
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth > 860) closeMenu();
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") closeMenu();
        });
    }
});
