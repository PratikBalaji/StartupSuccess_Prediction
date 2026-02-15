import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PredictionForm = ({ onPredict }) => {
    const [metadata, setMetadata] = useState({ industries: [], regions: [] });
    const [formData, setFormData] = useState({
        funding_rounds: 2,
        funding_amount: 50,
        valuation: 100,
        revenue: 10,
        employees: 50,
        market_share: 5,
        profitable: 0,
        year_founded: 2020,
        industry: '',
        region: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Fetch metadata for dropdowns
        axios.get('/api/metadata')
            .then(response => {
                setMetadata(response.data);
                // Set defaults if available
                if (response.data.industries.length > 0) {
                    setFormData(prev => ({ ...prev, industry: response.data.industries[0] }));
                }
                if (response.data.regions.length > 0) {
                    setFormData(prev => ({ ...prev, region: response.data.regions[0] }));
                }
            })
            .catch(err => {
                console.error('Error fetching metadata:', err);
                setError('Failed to load form data. Is the backend running?');
            });
    }, []);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const response = await axios.post('/predict', formData);
            onPredict(response.data);
        } catch (err) {
            console.error('Prediction error:', err);
            setError(err.response?.data?.error || 'Prediction failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="form-container">
            <h2>🚀 Startup Success Predictor</h2>
            {error && <div className="alert alert-danger">{error}</div>}

            <form onSubmit={handleSubmit} className="form-grid">
                <div className="form-group">
                    <label>Industry</label>
                    <select
                        name="industry"
                        value={formData.industry}
                        onChange={handleChange}
                        required
                        className="form-control"
                    >
                        {metadata.industries.map(ind => (
                            <option key={ind} value={ind}>{ind}</option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label>Region</label>
                    <select
                        name="region"
                        value={formData.region}
                        onChange={handleChange}
                        required
                        className="form-control"
                    >
                        {metadata.regions.map(reg => (
                            <option key={reg} value={reg}>{reg}</option>
                        ))}
                    </select>
                </div>

                <div className="form-group">
                    <label>Funding Rounds</label>
                    <input
                        type="number"
                        name="funding_rounds"
                        value={formData.funding_rounds}
                        onChange={handleChange}
                        min="1" max="10"
                        required
                        className="form-control"
                    />
                </div>

                <div className="form-group">
                    <label>Funding Amount (M USD)</label>
                    <input
                        type="number"
                        name="funding_amount"
                        value={formData.funding_amount}
                        onChange={handleChange}
                        min="0" step="0.01"
                        required
                        className="form-control"
                    />
                </div>

                <div className="form-group">
                    <label>Valuation (M USD)</label>
                    <input
                        type="number"
                        name="valuation"
                        value={formData.valuation}
                        onChange={handleChange}
                        min="0" step="0.01"
                        required
                        className="form-control"
                    />
                </div>

                <div className="form-group">
                    <label>Revenue (M USD)</label>
                    <input
                        type="number"
                        name="revenue"
                        value={formData.revenue}
                        onChange={handleChange}
                        min="0" step="0.01"
                        required
                        className="form-control"
                    />
                </div>

                <div className="form-group">
                    <label>Employees</label>
                    <input
                        type="number"
                        name="employees"
                        value={formData.employees}
                        onChange={handleChange}
                        min="1"
                        required
                        className="form-control"
                    />
                </div>

                <div className="form-group">
                    <label>Market Share (%)</label>
                    <input
                        type="number"
                        name="market_share"
                        value={formData.market_share}
                        onChange={handleChange}
                        min="0" max="100" step="0.01"
                        required
                        className="form-control"
                    />
                </div>

                <div className="form-group">
                    <label>Profitable</label>
                    <select
                        name="profitable"
                        value={formData.profitable}
                        onChange={handleChange}
                        required
                        className="form-control"
                    >
                        <option value="0">No</option>
                        <option value="1">Yes</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Year Founded</label>
                    <input
                        type="number"
                        name="year_founded"
                        value={formData.year_founded}
                        onChange={handleChange}
                        min="1990" max="2025"
                        required
                        className="form-control"
                    />
                </div>

                <button type="submit" className="submit-btn" disabled={loading}>
                    {loading ? 'Predicting...' : 'Predict Success'}
                </button>
            </form>
        </div>
    );
};

export default PredictionForm;
