const API_URL = "https://2cf0951c240b.ngrok-free.app"; // Your Colab ngrok URL

document.getElementById("prompt-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    const prompt = document.getElementById("prompt").value;
    const button = document.getElementById("generate-btn");
    const container = document.getElementById("image-container");

    // Loading state
    button.disabled = true;
    button.textContent = "Generating...";
    container.innerHTML = "";

    try {
        const response = await fetch(`${API_URL}/generate-image`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: prompt })
        });
        const data = await response.json();

        if (data.image_base64) {
            container.innerHTML = `
                <img src="data:image/png;base64,${data.image_base64}" width="512"/>
                <br><a href="data:image/png;base64,${data.image_base64}" download="generated.png">Download Image</a>
            `;
        } else {
            alert("Failed to generate image");
        }
    } catch (err) {
        console.error(err);
        alert("Error calling API");
    } finally {
        button.disabled = false;
        button.textContent = "Generate";
    }
});
