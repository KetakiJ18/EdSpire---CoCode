let timeLeft = 0;
let initialTime = 0;
let timerInterval = null;
let isRunning = false;

const setupScreen = document.getElementById('setup');
const timerScreen = document.getElementById('timer');
const timeDisplay = document.querySelector('.time-display');
const background = document.querySelector('.background');
const pauseBtn = document.getElementById('pauseBtn');

function startTimer(minutes) {
    initialTime = minutes * 60;
    timeLeft = initialTime;
    startTimerLogic();
}

function startCustomTimer() {
    const minutes = parseInt(document.getElementById('customMinutes').value);
    if (minutes && minutes > 0 && minutes <= 120) {
        startTimer(minutes);
    } else {
        alert('Please enter a valid time between 1 and 120 minutes');
    }
}

function startTimerLogic() {
    setupScreen.classList.add('hidden');
    timerScreen.classList.remove('hidden');
    isRunning = true;
    updateDisplay();
    timerInterval = setInterval(updateTimer, 1000);
}

function updateTimer() {
    if (timeLeft > 0) {
        timeLeft--;
        updateDisplay();
        updateBackground();
    } else {
        clearInterval(timerInterval);
        alert('Study session completed!');
        quitTimer();
    }
}

function updateDisplay() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    timeDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateBackground() {
    const progress = timeLeft / initialTime;
    background.style.filter = `grayscale(${progress * 100}%)`;
}

function toggleTimer() {
    isRunning = !isRunning;
    if (isRunning) {
        timerInterval = setInterval(updateTimer, 1000);
        pauseBtn.innerHTML = '<span class="pause-icon">⏸</span>';
    } else {
        clearInterval(timerInterval);
        pauseBtn.innerHTML = '<span class="play-icon">▶</span>';
    }
}

function quitTimer() {
    clearInterval(timerInterval);
    timeLeft = 0;
    isRunning = false;
    background.style.filter = 'grayscale(100%)';
    setupScreen.classList.remove('hidden');
    timerScreen.classList.add('hidden');
}