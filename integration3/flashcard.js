document.addEventListener('DOMContentLoaded', () => {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('pdfInput');
    const flashcard = document.getElementById('flashcard');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const carouselContainer = document.getElementById('carouselContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');

    let flashcards = [];
    let currentCardIndex = 0;

    uploadBox.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleFileUpload(file);
        }
    });

    async function handleFileUpload(file) {
        try {
            // Show loading indicator
            loadingIndicator.style.display = 'block';
            carouselContainer.classList.remove('visible');

            const formData = new FormData();
            formData.append("papers", file);

            // Make sure to update with the correct URL if needed (API is hosted locally)
            const response = await fetch("http://127.0.0.1:8000/upload/", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Upload failed: ${errorText}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            if (!data.flashcards || data.flashcards.length === 0) {
                throw new Error("No flashcards generated");
            }

            // Process all flashcards from all files
            flashcards = [];
            data.flashcards.forEach(fileData => {
                fileData.flashcards.forEach(card => {
                    flashcards.push({
                        question: card.question,
                        answer: card.answer
                    });
                });
            });

            if (flashcards.length === 0) {
                throw new Error("No valid flashcards were generated");
            }

            // Show success and update UI
            alert(`Successfully generated ${flashcards.length} flashcards!`);
            carouselContainer.classList.add("visible");
            currentCardIndex = 0;
            updateCard();
        } catch (error) {
            console.error("Upload error:", error);
            alert(`Error: ${error.message}`);
        } finally {
            // Hide loading indicator
            loadingIndicator.style.display = 'none';
        }
    }

    function updateCard() {
        const currentCard = flashcards[currentCardIndex];
        if (currentCard) {
            document.getElementById('questionText').textContent = currentCard.question;
            document.getElementById('answerText').textContent = currentCard.answer;
            flashcard.classList.remove('flipped');

            // Update counter
            document.getElementById('cardCounter').textContent = 
                `Card ${currentCardIndex + 1} of ${flashcards.length}`;
        }
    }

    prevBtn.addEventListener('click', () => {
        currentCardIndex = (currentCardIndex - 1 + flashcards.length) % flashcards.length;
        updateCard();
    });

    nextBtn.addEventListener('click', () => {
        currentCardIndex = (currentCardIndex + 1) % flashcards.length;
        updateCard();
    });
});
