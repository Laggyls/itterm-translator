async function handleTranslate() {
    const text = document.getElementById('inputText').value;
    const region = document.getElementById('regionSelect').value;
    const resultBox = document.getElementById('resultBox');

    resultBox.innerText = "Processing...";

    try {
        // Paste your Vercel URL here, ensuring it ends with /api/translate
        const response = await fetch('https://itterm-translator.vercel.app//api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, region })
        });
        
        const data = await response.json();
        
        if (data.error) {
            resultBox.innerText = "Error: " + data.error;
        } else {
            resultBox.innerText = data.translated;
        }
    } catch (err) {
        resultBox.innerText = "Error connecting to backend. Check console for details.";
        console.error(err);
    }
}