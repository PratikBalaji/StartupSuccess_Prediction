import React from 'react';
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend,
    CategoryScale,
    LinearScale,
    BarElement,
    Title
} from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(
    ArcElement,
    Tooltip,
    Legend,
    CategoryScale,
    LinearScale,
    BarElement,
    Title
);

const ResultsDashboard = ({ data }) => {
    if (!data) return null;

    const { prediction, probabilities, benchmarks, feature_importance, user_input } = data;

    // Probability Data
    const probData = {
        labels: Object.keys(probabilities),
        datasets: [
            {
                data: Object.values(probabilities),
                backgroundColor: [
                    '#11998e', // High Success
                    '#f093fb', // Medium Success
                    '#4facfe'  // Low Success
                ],
                borderWidth: 1,
            },
        ],
    };

    // Benchmark Data
    const metrics = Object.keys(benchmarks);
    const userValues = metrics.map(m => user_input[m]);
    const avgValues = metrics.map(m => benchmarks[m]);

    const benchmarkData = {
        labels: metrics,
        datasets: [
            {
                label: 'Your Startup',
                data: userValues,
                backgroundColor: '#667eea',
            },
            {
                label: 'Industry Average',
                data: avgValues,
                backgroundColor: '#e0e0e0',
            },
        ],
    };

    const benchmarkOptions = {
        indexAxis: 'y',
        responsive: true,
        scales: {
            x: {
                type: 'logarithmic',
                display: false // Hide grid for cleaner look
            }
        },
        plugins: {
            title: {
                display: true,
                text: 'Market Benchmark (Log Scale)'
            }
        }
    };

    // Feature Importance Data
    const entries = Object.entries(feature_importance);
    entries.sort((a, b) => b[1] - a[1]);
    const topEntries = entries.slice(0, 5);

    const importanceData = {
        labels: topEntries.map(e => e[0]),
        datasets: [
            {
                label: 'Impact (%)',
                data: topEntries.map(e => e[1]),
                backgroundColor: '#ff9f43',
            },
        ],
    };

    const importanceOptions = {
        responsive: true,
        plugins: {
            title: { display: true, text: 'Top 5 Key Success Drivers' },
            legend: { display: false }
        }
    };

    let resultClass = 'result-card';
    if (prediction === 'High Success') resultClass += ' high';
    else if (prediction === 'Medium Success') resultClass += ' medium';
    else resultClass += ' low';

    return (
        <div className="results-container">
            <div className={resultClass}>
                <h2>Prediction: {prediction}</h2>
            </div>

            <div className="charts-grid">
                <div className="chart-box">
                    <h3>Success Probability</h3>
                    <div className="chart-wrapper">
                        <Doughnut data={probData} />
                    </div>
                </div>

                <div className="chart-box">
                    <div className="chart-wrapper">
                        <Bar data={benchmarkData} options={benchmarkOptions} />
                    </div>
                </div>

                <div className="chart-box">
                    <div className="chart-wrapper">
                        <Bar data={importanceData} options={importanceOptions} />
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ResultsDashboard;
