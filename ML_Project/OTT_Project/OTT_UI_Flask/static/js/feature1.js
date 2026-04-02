const userSeqForm = document.getElementById("userSeqForm");
const manualPredictForm = document.getElementById("manualPredictForm");
const resultEmpty = document.getElementById("resultEmpty");
const resultContent = document.getElementById("resultContent");
const riskBadge = document.getElementById("riskBadge");
const summaryUserSeq = document.getElementById("summaryUserSeq");
const summaryConfidence = document.getElementById("summaryConfidence");
const probStableText = document.getElementById("probStableText");
const probCautionText = document.getElementById("probCautionText");
const probRiskText = document.getElementById("probRiskText");
const probStableBar = document.getElementById("probStableBar");
const probCautionBar = document.getElementById("probCautionBar");
const probRiskBar = document.getElementById("probRiskBar");
const reasonList = document.getElementById("reasonList");
const inputSummary = document.getElementById("inputSummary");
const feedbackToast = document.getElementById("feedbackToast");

function showToast(message, type = "error") {
    feedbackToast.textContent = message;
    feedbackToast.className = `toast-box show ${type}`;
    setTimeout(() => {
        feedbackToast.className = "toast-box d-none";
    }, 3200);
}

function setRiskBadge(label) {
    riskBadge.textContent = label;
    riskBadge.className = "risk-badge";
    if (label === "안정") riskBadge.classList.add("risk-safe");
    if (label === "주의") riskBadge.classList.add("risk-caution");
    if (label === "위험") riskBadge.classList.add("risk-danger");
}

function renderReasons(reasons) {
    reasonList.innerHTML = "";
    (reasons || []).forEach((reason) => {
        const li = document.createElement("li");
        li.textContent = reason;
        reasonList.appendChild(li);
    });
}

function renderInputSummary(summary) {
    inputSummary.innerHTML = "";
    Object.entries(summary || {}).forEach(([label, value]) => {
        const item = document.createElement("div");
        item.className = "summary-chip";
        item.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
        inputSummary.appendChild(item);
    });
}

function renderResult(data) {
    resultEmpty.classList.add("d-none");
    resultContent.classList.remove("d-none");

    setRiskBadge(data.risk_label);
    summaryUserSeq.textContent = data.user_seq ?? "직접 입력";
    summaryConfidence.textContent = `${data.confidence}%`;

    probStableText.textContent = `${data.probabilities.stable}%`;
    probCautionText.textContent = `${data.probabilities.caution}%`;
    probRiskText.textContent = `${data.probabilities.risk}%`;

    probStableBar.style.width = `${data.probabilities.stable}%`;
    probCautionBar.style.width = `${data.probabilities.caution}%`;
    probRiskBar.style.width = `${data.probabilities.risk}%`;

    renderReasons(data.reasons);
    renderInputSummary(data.input_summary);
}

async function postJson(url, payload) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok || !result.success) {
        throw new Error(result.message || "요청 처리 중 오류가 발생했습니다.");
    }
    return result.data;
}

userSeqForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const userSeq = document.getElementById("user_seq").value.trim();
    if (!userSeq) {
        showToast("사용자 번호를 입력해주세요.");
        return;
    }
    try {
        const data = await postJson("/api/predict/user-seq", { user_seq: userSeq });
        renderResult(data);
    } catch (error) {
        showToast(error.message);
    }
});

manualPredictForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(manualPredictForm);
    const payload = {};
    for (const [key, value] of formData.entries()) {
        payload[key] = value;
    }
    try {
        const data = await postJson("/api/predict/manual", payload);
        renderResult(data);
    } catch (error) {
        showToast(error.message);
    }
});
