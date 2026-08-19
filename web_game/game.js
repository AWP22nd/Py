// Game constants
const BOARD_WIDTH = 10;
const BOARD_HEIGHT = 20;
const PIECE_SIZE = 30;
const COLORS = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#f9ca24', '#f0932b', '#eb4c89'];

// Game state
let gameState = {
    board: Array(BOARD_HEIGHT).fill(null).map(() => Array(BOARD_WIDTH).fill(0)),
    currentPiece: null,
    nextPiece: null,
    score: 0,
    level: 1,
    lines: 0,
    gameOver: false,
    canDrop: true,
    scoreSpeed: 1,
    sparkles: []
};

// Initialize the game
function initGame() {
    // Reset game state
    gameState.board = Array(BOARD_HEIGHT).fill(null).map(() => Array(BOARD_WIDTH).fill(0));
    gameState.score = 0;
    gameState.level = 1;
    gameState.lines = 0;
    gameState.gameOver = false;
    gameState.canDrop = true;
    gameState.scoreSpeed = 1;
    gameState.sparkles = [];

    // Generate pieces
    gameState.currentPiece = generateRandomPiece();
    gameState.nextPiece = generateRandomPiece();

    // Update display
    updateScore();
    updateLevel();
    updateLines();

    // Render board
    renderBoard();
    renderPiece();
    renderNextPiece();

    // Hide game over screen
    const gameOverScreen = document.getElementById('game-over');
    gameOverScreen.classList.remove('active');
}

// Generate random piece
function generateRandomPiece() {
    const pieces = [
        // L-shaped piece
        [[1, 0], [1, 0], [1, 0], [1, 0]].map((row, y) => row.map((cell, x) => ({ filled: cell, x: x, y: y }))),
        // J-shaped piece
        [[0, 1], [0, 1], [0, 1], [0, 1]].map((row, y) => row.map((cell, x) => ({ filled: cell, x: x, y: y }))),
        // I-shaped piece
        [[1, 0], [1, 0], [1, 0], [1, 0]].map((row, y) => row.map((cell, x) => ({ filled: cell, x: x, y: y }))),
        // T-shaped piece
        [[1, 0], [1, 0], [1, 0], [1, 0]].map((row, y) => row.map((cell, x) => ({ filled: cell, x: x, y: y }))),
        // Square piece
        [[1, 0], [1, 0], [1, 0], [1, 0]].map((row, y) => row.map((cell, x) => ({ filled: cell, x: x, y: y })))
    ];

    const randomPiece = pieces[Math.floor(Math.random() * pieces.length)];
    return {
        shape: randomPiece,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        x: Math.floor((BOARD_WIDTH - 4) / 2),
        y: 0,
        rotation: 0
    };
}

// Render game board
function renderBoard() {
    const boardElement = document.getElementById('game-board');
    boardElement.innerHTML = '';

    for (let y = 0; y < BOARD_HEIGHT; y++) {
        for (let x = 0; x < BOARD_WIDTH; x++) {
            const cell = document.createElement('div');
            cell.className = 'cell';
            if (gameState.board[y][x]) {
                cell.classList.add('filled');
                cell.style.backgroundColor = gameState.board[y][x].color;
            }
            boardElement.appendChild(cell);
        }
    }
}

// Render current piece
function renderPiece() {
    const boardElement = document.getElementById('game-board');
    const cells = document.querySelectorAll('.cell');

    // Clear old piece
    for (let y = 0; y < BOARD_HEIGHT; y++) {
        for (let x = 0; x < BOARD_WIDTH; x++) {
            const cellIndex = y * BOARD_WIDTH + x;
            if (cells[cellIndex] && cells[cellIndex].classList.contains('active')) {
                cells[cellIndex].classList.remove('active');
            }
        }
    }

    // Draw new piece
    if (gameState.currentPiece) {
        for (let py = 0; py < 4; py++) {
            for (let px = 0; px < 4; px++) {
                if (gameState.currentPiece.shape[py][px] &&
                    gameState.currentPiece.x + px >= 0 &&
                    gameState.currentPiece.x + px < BOARD_WIDTH &&
                    gameState.currentPiece.y + py < BOARD_HEIGHT) {

                    const cellX = gameState.currentPiece.x + px;
                    const cellY = gameState.currentPiece.y + py;
                    const cellIndex = cellY * BOARD_WIDTH + cellX;

                    if (cells[cellIndex]) {
                        cells[cellIndex].classList.add('active');
                        cells[cellIndex].style.backgroundColor = gameState.currentPiece.color;
                    }
                }
            }
        }
    }
}

// Render next piece
function renderNextPiece() {
    const nextPieceElement = document.getElementById('next-piece');
    nextPieceElement.innerHTML = '';

    const nextGrid = document.createElement('div');
    nextGrid.className = 'next-piece-grid';

    for (let py = 0; py < 4; py++) {
        for (let px = 0; px < 4; px++) {
            const cell = document.createElement('div');
            cell.className = 'cell';

            if (gameState.nextPiece && gameState.nextPiece.shape[py][px]) {
                cell.classList.add('filled');
                cell.style.backgroundColor = gameState.nextPiece.color;
            }

            nextGrid.appendChild(cell);
        }
    }

    nextPieceElement.appendChild(nextGrid);
}

// Update score display
function updateScore() {
    document.getElementById('score').textContent = gameState.score;
}

// Update level display
function updateLevel() {
    document.getElementById('level').textContent = gameState.level;
}

// Update lines display
function updateLines() {
    document.getElementById('lines').textContent = gameState.lines;
}

// Move piece
function movePiece(dx, dy) {
    if (gameState.gameOver) return;

    const newX = gameState.currentPiece.x + dx;
    const newY = gameState.currentPiece.y + dy;

    if (isValidPosition(newX, newY)) {
        gameState.currentPiece.x = newX;
        gameState.currentPiece.y = newY;
        renderPiece();
    }
}

// Rotate piece
function rotatePiece() {
    if (gameState.gameOver) return;

    const rotated = gameState.currentPiece.shape.map((row, i) =>
        row.map((cell, j) => gameState.currentPiece.shape[BOARD_HEIGHT - 1 - j][i])
    );

    // Check if rotation is valid
    const oldShape = gameState.currentPiece.shape;
    gameState.currentPiece.shape = rotated;

    if (!isValidPosition()) {
        gameState.currentPiece.shape = oldShape;
    } else {
        gameState.currentPiece.rotation++;
    }

    renderPiece();
}

// Drop piece
function dropPiece() {
    if (!gameState.canDrop || gameState.gameOver) return;

    gameState.canDrop = false;

    // Auto-drop
    const dropY = findDropPosition();
    gameState.currentPiece.y = dropY;

    // Lock piece
    lockPiece();

    // Check game over
    if (checkGameOver()) {
        gameOver();
    }

    renderPiece();
    setTimeout(() => gameState.canDrop = true, 100);
}

// Find drop position
function findDropPosition() {
    let y = gameState.currentPiece.y;

    while (isValidPosition(gameState.currentPiece.x, y + 1)) {
        y++;
    }

    return y;
}

// Lock piece to board
function lockPiece() {
    for (let py = 0; py < 4; py++) {
        for (let px = 0; px < 4; px++) {
            if (gameState.currentPiece.shape[py][px]) {
                const cellX = gameState.currentPiece.x + px;
                const cellY = gameState.currentPiece.y + py;

                if (cellY < BOARD_HEIGHT) {
                    gameState.board[cellY][cellX] = {
                        color: gameState.currentPiece.color
                    };
                }
            }
        }
    }

    // Generate next piece
    gameState.currentPiece = gameState.nextPiece;
    gameState.nextPiece = generateRandomPiece();

    // Check for lines
    clearLines();

    renderBoard();
    renderPiece();
    renderNextPiece();
}

// Check for cleared lines
function clearLines() {
    const linesToClear = [];

    for (let y = 0; y < BOARD_HEIGHT; y++) {
        let lineFull = true;
        for (let x = 0; x < BOARD_WIDTH; x++) {
            if (!gameState.board[y][x]) {
                lineFull = false;
                break;
            }
        }

        if (lineFull) {
            linesToClear.push(y);
        }
    }

    if (linesToClear.length > 0) {
        gameState.lines += linesToClear.length;

        // Calculate score based on number of lines and level
        const lineScores = [0, 100, 300, 500, 800];
        const lineScore = lineScores[linesToClear.length] || 100;
        gameState.score += lineScore * gameState.level;

        // Update level based on lines
        gameState.level = Math.floor(gameState.lines / 10) + 1;

        // Create sparkles for cleared lines
        createSparkles(linesToClear);

        // Clear lines
        linesToClear.forEach(y => {
            for (let x = 0; x < BOARD_WIDTH; x++) {
                gameState.board[y][x] = 0;
            }
        });

        // Shift down remaining pieces
        for (let x = 0; x < BOARD_WIDTH; x++) {
            for (let y = BOARD_HEIGHT - 1; y >= 0; y--) {
                if (gameState.board[y][x]) {
                    for (let y2 = y; y2 > 0; y2--) {
                        gameState.board[y2][x] = gameState.board[y2 - 1][x];
                    }
                    gameState.board[0][x] = 0;
                }
            }
        }
    }
}

// Create sparkles effect
function createSparkles(lines) {
    for (const y of lines) {
        for (let x = 0; x < BOARD_WIDTH; x++) {
            for (let i = 0; i < 3; i++) {
                gameState.sparkles.push({
                    x: x * PIECE_SIZE + PIECE_SIZE / 2,
                    y: y * PIECE_SIZE + PIECE_SIZE / 2,
                    angle: Math.random() * 360,
                    life: 1.0,
                    size: Math.random() * 5 + 2,
                    color: COLORS[Math.floor(Math.random() * COLORS.length)]
                });
            }
        }
    }
}

// Check game over
function checkGameOver() {
    const topRows = gameState.currentPiece.y < 3;
    if (topRows) {
        for (let px = 0; px < 4; px++) {
            const cellX = gameState.currentPiece.x + px;
            if (cellX >= 0 && cellX < BOARD_WIDTH) {
                for (let py = 0; py < 4; py++) {
                    const cellY = gameState.currentPiece.y + py;
                    if (cellY >= 0 && cellY < BOARD_HEIGHT) {
                        if (gameState.currentPiece.shape[py][px] && gameState.board[cellY][cellX]) {
                            return true;
                        }
                    }
                }
            }
        }
    }
    return false;
}

// Game over
function gameOver() {
    gameState.gameOver = true;

    const gameOverScreen = document.getElementById('game-over');
    const finalScore = document.getElementById('final-score');
    finalScore.textContent = gameState.score;
    gameOverScreen.classList.add('active');
}

// Check if position is valid
function isValidPosition(newX, newY) {
    const testX = typeof newX === 'number' ? newX : gameState.currentPiece.x;
    const testY = typeof newY === 'number' ? newY : gameState.currentPiece.y;

    for (let py = 0; py < 4; py++) {
        for (let px = 0; px < 4; px++) {
            if (gameState.currentPiece.shape[py][px]) {
                const cellX = testX + px;
                const cellY = testY + py;

                // Check if cell is within bounds
                if (cellX < 0 || cellX >= BOARD_WIDTH || cellY >= BOARD_HEIGHT) {
                    return false;
                }

                // Check if cell overlaps with filled cell
                if (cellY >= 0 && cellY < BOARD_HEIGHT && gameState.board[cellY][cellX]) {
                    return false;
                }
            }
        }
    }

    return true;
}

// Keyboard controls
function setupKeyboardControls() {
    document.addEventListener('keydown', (event) => {
        if (gameState.gameOver && event.key === ' ') {
            event.preventDefault();
            resetGame();
        }

        switch (event.key) {
            case 'ArrowLeft':
                event.preventDefault();
                movePiece(-1, 0);
                break;
            case 'ArrowRight':
                event.preventDefault();
                movePiece(1, 0);
                break;
            case 'ArrowDown':
                event.preventDefault();
                movePiece(0, 1);
                break;
            case 'ArrowUp':
                event.preventDefault();
                rotatePiece();
                break;
            case ' ':
                event.preventDefault();
                dropPiece();
                break;
        }
    });
}

// Reset game
function resetGame() {
    initGame();
    setupKeyboardControls();
}

// Initialize game
function gameLoop() {
    if (!gameState.gameOver) {
        setTimeout(gameLoop, 1000);
    }
}

// Start the game
initGame();
setupKeyboardControls();
gameLoop();