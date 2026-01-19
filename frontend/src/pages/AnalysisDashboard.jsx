import './AnalysisDashboard.css';

export default function AnalysisDashboard() {
    return (
        <div className="dashboard-container">
            <h1>Analysis Dashboard</h1>
            <form className="dashboard-form" method="get" target="_blank">
                <div className="form-group">
                    <label>Room</label>
                    <select name="room">
                        <option value="101">101</option>
                        <option value="102">102</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Metric</label>
                    <select name="metric">
                        <option value="temperature">Temperature</option>
                        <option value="humidity">Humidity</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>From</label>
                    <input type="datetime-local" name="start"/>
                </div>

                <div className="form-group">
                    <label>To</label>
                    <input type="datetime-local" name="end"/>
                </div>

                <div className="button-group">
                    <button type="submit" formAction="http://localhost:8000/analysis/plot/">Show Plot
                    </button>
                    <button type="submit" formAction="http://localhost:8000/analysis/plot/save/">Save Plot
                    </button>
                    <button type="submit" formAction="http://localhost:8000/analysis/report/">Show Report
                    </button>
                    <button type="submit" formAction="http://localhost:8000/analysis/report/save/">Save Report
                    </button>
                </div>
            </form>
        </div>
    );
}