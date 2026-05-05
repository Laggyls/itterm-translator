const API_BASE_URL = "https://itterm-translator.vercel.app";

const elements = {
    inputText: document.getElementById("inputText"),
    sourceLanguage: document.getElementById("sourceLanguage"),
    targetVariant: document.getElementById("targetVariant"),
    toneStyle: document.getElementById("toneStyle"),
    translateButton: document.getElementById("translateButton"),
    resultBox: document.getElementById("resultBox"),
    statusText: document.getElementById("statusText"),
};

async function handleTranslate() {
    const text = elements.inputText.value.trim();
    if (!text) {
        elements.statusText.textContent = "Please enter text first.";
        return;
    }

    elements.translateButton.disabled = true;
    elements.statusText.textContent = "Translating...";
    elements.resultBox.textContent = "";

    try {
        const response = await fetch(`${API_BASE_URL}/api/translate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text,
                source_language: elements.sourceLanguage.value,
                target_variant: elements.targetVariant.value,
                tone_style: elements.toneStyle.value,
            }),
        });

        const data = await response.json();
        if (!response.ok || data.error) {
            throw new Error(data.error || "Translation failed.");
        }

        elements.resultBox.textContent = data.translated;
        elements.statusText.textContent = "Done.";
    } catch (error) {
        elements.statusText.textContent = "Translation failed.";
        elements.resultBox.textContent = error.message;
    } finally {
        elements.translateButton.disabled = false;
    }
}

elements.translateButton.addEventListener("click", handleTranslate);