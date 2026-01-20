import {useState, useEffect} from "react";
import './AnalysisDashboard.css';

export default function AnalysisDashboard() {
    const [reports, setReports] = useState([]);
    const [selectedReport, setSelectedReport] = useState("");
    const [filters, setFilters] = useState({
        reportType: "DAILY",
        room: "SALON-01",
        metric: "temperature",
        start: "",
        end: "",
    });
    const [error, setError] = useState("");
    const [archiveError, setArchiveError] = useState("");

    useEffect(() => {
        const query = Object.fromEntries(
            Object.entries(filters).filter(([_, v]) => v)
        );
        const params = new URLSearchParams(query).toString();
        fetch(`http://localhost:8000/analysis/archive/list/?${params}`)
            .then((res) => res.json())
            .then((data) => {
                setReports(data);
                if (data.length > 0) setSelectedReport(data[0].id);
                else setSelectedReport("");
            })
            .catch(() => setArchiveError("Failed to fetch archived reports"));
    }, [filters]);

    const handleFilterChange = (e) => {
        const {name, value} = e.target;
        setFilters((prev) => ({...prev, [name]: value}));
        setSelectedReport("");
    };

    const handleSubmit = (e) => {

        const form = e.target;
        const start = form.start.value;
        const end = form.end.value;


        if (new Date(start) > new Date(end)) {
            setError("Start date/time cannot be after end date/time.");
            return;
        }

        setError("");
    };

    const handleReportSubmit = (e) => {
        if (!selectedReport) {
            e.preventDefault();
            setArchiveError("Please select a report to download.");
            return;
        }

        const form = e.target;
        const start = form.start.value;
        const end = form.end.value;

        if (new Date(start) > new Date(end)) {
            setArchiveError("Start date/time cannot be after end date/time.");
            return;
        }
        setArchiveError("");
    };

    return (
        <div>
            <div className="dashboard-container">
                <h1>Analysis Dashboard</h1>

                {error && <div className="error-message">{error}</div>}

                <form className="dashboard-form" method="get" target="_blank" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label>Room</label>
                        <select name="room">
                            <option value="SALON-01">SALON-01</option>
                            <option value="SALON-02">SALON-02</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Metric</label>
                        <select name="metric">
                            <option value="temperature">Temperature (°C)</option>
                            <option value="humidity">Humidity (%)</option>
                            <option value="sunlight">Sunlight (lux)</option>
                            <option value="brightness">Brightness (lumen)</option>
                            <option value="cloudiness">Cloudiness (%)</option>
                            <option value="rainfall">Rainfall (mm/h)</option>
                            <option value="wind">Wind (m/s)</option>
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
            <div className="dashboard-container">
                <h1>Save Archive Report</h1>

                {archiveError && <div className="error-message">{archiveError}</div>}

                <form className="dashboard-form" method="get" target="_blank" onSubmit={handleReportSubmit}
                      action={selectedReport ? `http://localhost:8000/analysis/archive/${selectedReport}/` : "#"}>

                    <div className="form-group">
                        <label>Report Type</label>
                        <select name="reportType" value={filters.reportType} onChange={handleFilterChange}>
                            <option value="DAILY">Daily</option>
                            <option value="WEEKLY">Weekly</option>
                            <option value="MONTHLY">Monthly</option>
                            <option value="SEASONAL">Seasonal</option>
                            <option value="SEMIANNUAL">Semiannual</option>
                            <option value="ANNUAL">Annual</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Room</label>
                        <select name="room" value={filters.room} onChange={handleFilterChange}>
                            <option value="SALON-01">SALON-01</option>
                            <option value="SALON-02">SALON-02</option>
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Metric</label>
                        <select name="metric" value={filters.metric} onChange={handleFilterChange}>
                            <option value="temperature">Temperature (°C)</option>
                            <option value="humidity">Humidity (%)</option>
                            <option value="sunlight">Sunlight (lux)</option>
                            <option value="brightness">Brightness (lumen)</option>
                            <option value="cloudiness">Cloudiness (%)</option>
                            <option value="rainfall">Rainfall (mm/h)</option>
                            <option value="wind">Wind (m/s)</option>
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

                    <div className="form-group">
                        <label>Report ID</label>
                        <select value={selectedReport} onChange={(e) => setSelectedReport(e.target.value)}>
                            {reports.length > 0 ? (
                                reports.map((r) => (
                                    <option key={r.id} value={r.id}>
                                        {r.reportType} | {r.roomId} | {r.metric} | {r.periodStart.split("T")[0]} | {r.periodEnd.split("T")[0]}
                                    </option>
                                ))
                            ) : (
                                <option disabled>No reports found</option>
                            )}
                        </select>
                    </div>


                    <div className="button-group">
                        <button type="submit" disabled={!selectedReport}>Save Report</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

