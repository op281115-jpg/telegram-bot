const express = require('express');
const cors = require('cors');
const app = express();

app.use(express.json());
app.use(cors());

// Login API
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    if (username) {
        res.json({ success: true, message: 'Login successful', balance: 10000 });
    } else {
        res.status(400).json({ success: false, message: 'Invalid username' });
    }
});

// Game Bet & Win/Loss Logic (House Profit Control)
app.post('/api/bet', (req, res) => {
    const { betAmount } = req.body;
    
    const isWin = Math.random() < 0.45; 
    const winAmount = isWin ? betAmount * 2 : 0;

    res.json({
        success: true,
        isWin: isWin,
        winAmount: winAmount,
        message: isWin ? 'You Won!' : 'You Lost!'
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
