async function handleTranslate() {
    const text = document.getElementById('inputText').value;
    const region = document.getElementById('regionSelect').value;
    const resultBox = document.getElementById('resultBox');

    resultBox.innerText = "Processing...";

    try {
        // REPLACE with your actual Vercel URL after deployment
        const response = await fetch('https://your-project-name.vercel.app/api/translate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, region })
        });
        const data = await response.json();
        resultBox.innerText = data.translated;
    } catch (err) {
        resultBox.innerText = "Error connecting to backend.";
    }
}