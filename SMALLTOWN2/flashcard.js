document.addEventListener('DOMContentLoaded', () => {
    const uploadBox = document.getElementById('uploadBox');
    const pdfInput = document.getElementById('pdfInput');
    const flashcard = document.getElementById('flashcard');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const carouselContainer = document.getElementById('carouselContainer');

    // Sample questions (to be replaced with backend data)
    const flashcards = [
        { question: "What is the capital of France?", answer: "Paris" },
        { question: "What is the largest planet in our solar system?", answer: "Jupiter" },
        { question: "Who painted the Mona Lisa?", answer: "Leonardo da Vinci" }
    ];

    let currentCardIndex = 0;

    // Upload functionality
    uploadBox.addEventListener('click', () => {
        pdfInput.click();
    });

    uploadBox.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadBox.style.transform = 'scale(1.02)';
    });

    uploadBox.addEventListener('dragleave', () => {
        uploadBox.style.transform = 'scale(1)';
    });

    uploadBox.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadBox.style.transform = 'scale(1)';
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            handlePDFUpload(file);
        } else {
            alert('Please upload a PDF file');
        }
    });

    pdfInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handlePDFUpload(file);
        }
    });

    function handlePDFUpload(file) {
        // Here you would typically send the file to your backend
        console.log('PDF uploaded:', file.name);
        // Show success message
        alert('PDF uploaded successfully! Generating flashcards...');
        // Show the carousel container
        carouselContainer.classList.add('visible');
        // Initialize the first card
        updateCard();
    }

    // Flashcard functionality
    flashcard.addEventListener('click', () => {
        flashcard.classList.toggle('flipped');
    });

    function updateCard() {
        const currentCard = flashcards[currentCardIndex];
        document.getElementById('questionText').textContent = currentCard.question;
        document.getElementById('answerText').textContent = currentCard.answer;
        flashcard.classList.remove('flipped');
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
