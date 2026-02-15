const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors()); // Allow all origins for dev simplicity
app.use(bodyParser.json());

// Load metadata
let metadata = { industries: [], regions: [] };
try {
    const metadataPath = path.join(__dirname, 'data', 'metadata.json');
    if (fs.existsSync(metadataPath)) {
        const data = fs.readFileSync(metadataPath, 'utf8');
        metadata = JSON.parse(data);
    } else {
        console.warn('Warning: metadata.json not found. Run scripts/extract_metadata.py');
    }
} catch (err) {
    console.error('Error loading metadata:', err);
}

// REST API Routes

// GET /api/metadata - Serve valid options
app.get('/api/metadata', (req, res) => {
    res.json(metadata);
});

// POST /predict - Handle prediction
app.post('/predict', (req, res) => {
    const scriptPath = path.join(__dirname, 'scripts', 'predict_cli.py');
    const pythonProcess = spawn('python', [scriptPath]);

    let result = '';
    let error = '';

    // Send data to Python script via stdin
    pythonProcess.stdin.write(JSON.stringify(req.body));
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
        result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        error += data.toString();
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Python script exited with code ${code}`);
            console.error(`Error: ${error}`);
            return res.status(500).json({ error: 'Prediction failed', details: error });
        }

        try {
            const jsonResponse = JSON.parse(result);
            if (jsonResponse.error) {
                return res.status(400).json(jsonResponse);
            }
            res.json(jsonResponse);
        } catch (e) {
            console.error('Failed to parse Python output:', e);
            console.error('Raw output:', result);
            res.status(500).json({ error: 'Invalid response from model' });
        }
    });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
