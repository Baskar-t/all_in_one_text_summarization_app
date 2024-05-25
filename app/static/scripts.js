document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    const videoFile = document.getElementById('video-upload').files[0];
    formData.append('video', videoFile);
    
    try {
        const response = await fetch('/upload_video', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error:', error);
    }
});

function displayResults(data) {
    document.getElementById('result').style.display = 'block';

    document.getElementById('transcription').innerHTML = `<h3>Transcription:</h3><p>${data.transcription}</p>`;
    document.getElementById('summary').innerHTML = `<h3>Summary:</h3><p>${data.summary}</p>`;
    document.getElementById('keyphrases').innerHTML = `<h3>Keyphrases:</h3><ul>${data.keyphrases.map(k => `<li>${k}</li>`).join('')}</ul>`;
    document.getElementById('sentiment').innerHTML = `<h3>Sentiment:</h3><p>Polarity: ${data.sentiment.polarity}, Subjectivity: ${data.sentiment.subjectivity}</p>`;
    document.getElementById('entities').innerHTML = `<h3>Named Entities:</h3><ul>${data.entities.map(e => `<li>${e[0]} (${e[1]})</li>`).join('')}</ul>`;
}
