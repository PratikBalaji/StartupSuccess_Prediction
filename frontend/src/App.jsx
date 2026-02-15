import React, { useState } from 'react';
import PredictionForm from './components/PredictionForm';
import ResultsDashboard from './components/ResultsDashboard';
import './App.css';

function App() {
    const [resultData, setResultData] = useState(null);

    return (
        <div className="app-container">
            <div className="content-wrapper">
                <PredictionForm onPredict={setResultData} />
                {resultData && <ResultsDashboard data={resultData} />}
            </div>
        </div>
    );
}

export default App;
