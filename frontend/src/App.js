import { useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(false); // ✅ loading state

  const handleSearch = async () => {
    setLoading(true); // start loading
    try {
      const response = await axios.post("http://127.0.0.1:8000/search", {
        text: query,
        min_amount: 5000,
      });
      setResults(response.data.results);

      // Aggregate data for chart
      const severityCount = { "High Risk": 0, "Medium Risk": 0, "Suspicious": 0, "Low Risk": 0 };
      response.data.results.forEach((r) => {
        severityCount[r.severity] += 1;
      });
      const chartArr = Object.keys(severityCount).map((k) => ({
        severity: k,
        count: severityCount[k],
      }));
      setChartData(chartArr);
    } catch (err) {
      console.error(err);
      alert("Error querying API");
    } finally {
      setLoading(false); // stop loading
    }
  };

  const getRowColor = (severity) => {
    switch (severity) {
      case "High Risk":
        return "#f8d7da"; // red
      case "Medium Risk":
        return "#fff3cd"; // yellow
      case "Suspicious":
        return "#d1ecf1"; // light blue
      default:
        return "#d4edda"; // green
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h2>Fraud Detection Dashboard</h2>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search transaction..."
        style={{ width: 300, marginRight: 10 }}
      />
      <button onClick={handleSearch} disabled={loading}>
        {loading ? "Fetching data..." : "Search"}
      </button>

      {loading && <p style={{ marginTop: 20 }}>⏳ Calculating results, please wait...</p>}

      {!loading && results.length > 0 && (
        <>
          <h3 style={{ marginTop: 20 }}>Transaction Results</h3>
          <table border="1" cellPadding="5" style={{ marginTop: 10, borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Account</th>
                <th>Description</th>
                <th>Amount</th>
                <th>Distance</th>
                <th>Rule Flag</th>
                <th>Explanation</th>
                <th>Anomaly Flag</th>
                <th>Anomaly Score</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {results.map((row) => (
                <tr key={row.id} style={{ backgroundColor: getRowColor(row.severity) }}>
                  <td>{row.id}</td>
                  <td>{row.account_number}</td>
                  <td>{row.description}</td>
                  <td>{row.amount}</td>
                  <td>{row.dist?.toFixed(4)}</td>
                  <td>{row.rule_flag}</td>
                  <td>{row.explanation}</td>
                  <td>{row.anomaly_flag}</td>
                  <td>{row.anomaly_score?.toFixed(4)}</td>
                  <td>{row.severity}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <h3 style={{ marginTop: 40 }}>Fraud Severity Summary</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <XAxis dataKey="severity" />
              <YAxis />
              <RechartsTooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}

export default App;
