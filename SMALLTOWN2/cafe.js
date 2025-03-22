document.getElementById("uploadButton").addEventListener("click", async function() {
    const papers = document.getElementById("papers").files[0];
    const syllabus = document.getElementById("syllabus").files[0];

    if (!papers || !syllabus) {
        alert("Please upload both past papers and the syllabus.");
        return;
    }

    const formData = new FormData();
    formData.append("papers", papers);
    formData.append("syllabus", syllabus);

    document.getElementById("loading").style.display = "block";
    
    try {
        const response = await fetch("http://127.0.0.1:8000/upload/", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();
        
        if (data && data.ranked_topics) {
            displayResults(data.ranked_topics);
        } else {
            alert("No ranked topics found in the response.");
        }
    } catch (error) {
        console.error("Error uploading files:", error);
        alert("Failed to upload files. Try again.");
    }

    document.getElementById("loading").style.display = "none";
});

function displayResults(topics) {
    const resultsDiv = document.getElementById("results");
    const topicsList = document.getElementById("topicsList");

    resultsDiv.style.display = "block";
    topicsList.innerHTML = "";  

    topics.forEach(topic => {
        const li = document.createElement("li");
        li.textContent = topic;
        topicsList.appendChild(li);
    });
}
