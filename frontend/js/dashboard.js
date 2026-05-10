// Dashboard.js - Handle dashboard functionality

let comparisonChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadStatistics();
    loadRecentPredictions();
    loadModelInfo();
    loadComparisonChart();
});

// Load statistics
async function loadStatistics() {
    try {
        const data = await apiCall('/statistics');

        document.getElementById('totalStudents').textContent = data.total_students;
        document.getElementById('totalPredictions').textContent = data.total_predictions;
        document.getElementById('avgPredicted').textContent = formatNumber(data.average_predicted_marks);
        document.getElementById('avgPrevious').textContent = formatNumber(data.average_previous_marks);
        document.getElementById('avgAttendance').textContent = formatNumber(data.average_attendance);
        document.getElementById('avgStudyHours').textContent = formatNumber(data.average_study_hours);

    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Load recent predictions
async function loadRecentPredictions() {
    try {
        const data = await apiCall('/student-records');
        const tbody = document.getElementById('predictionsTableBody');

        if (data.records.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">No predictions yet</td></tr>';
            return;
        }

        tbody.innerHTML = data.records.map(record => `
            <tr>
                <td>${record.student_name}</td>
                <td>${record.student_id}</td>
                <td>${formatNumber(record.attendance)}%</td>
                <td>${formatNumber(record.internal_marks)}</td>
                <td>${formatNumber(record.study_hours)}</td>
                <td>${formatNumber(record.previous_semester_marks)}</td>
                <td><strong>${formatNumber(record.predicted_marks)}</strong></td>
                <td>${formatDate(record.prediction_date)}</td>
            </tr>
        `).join('');

    } catch (error) {
        console.error('Error loading predictions:', error);
    }
}

// Load model information
async function loadModelInfo() {
    try {
        const data = await apiCall('/model-info');

        document.getElementById('metricR2').textContent = formatNumber(data.metrics.r2_score);
        document.getElementById('metricRMSE').textContent = formatNumber(data.metrics.rmse);
        document.getElementById('metricMSE').textContent = formatNumber(data.metrics.mse);
        document.getElementById('metricMAE').textContent = formatNumber(data.metrics.mae);

        // Display feature importance
        displayFeatureImportance(data);

    } catch (error) {
        console.error('Error loading model info:', error);
    }
}

// Display feature importance
async function displayFeatureImportance(modelData) {
    try {
        const container = document.getElementById('featureImportanceContainer');
        
        if (!modelData.coefficients || modelData.coefficients.length === 0) {
            container.innerHTML = '<p>No feature importance data available</p>';
            return;
        }

        // Normalize coefficients to percentages
        const absCoefficients = modelData.coefficients.map(c => Math.abs(c));
        const total = absCoefficients.reduce((a, b) => a + b, 1);
        const percentages = absCoefficients.map(c => (Math.abs(c) / total) * 100);

        container.innerHTML = modelData.features.map((feature, index) => `
            <div class="feature-item">
                <span class="feature-name">${feature}</span>
                <div class="feature-bar-container">
                    <div class="feature-bar" style="width: ${percentages[index]}%"></div>
                </div>
                <span class="feature-percentage">${formatNumber(percentages[index])}%</span>
            </div>
        `).join('');

    } catch (error) {
        console.error('Error displaying feature importance:', error);
    }
}

// Load comparison chart
async function loadComparisonChart() {
    try {
        const data = await apiCall('/comparison-data');

        if (data.student_names.length === 0) {
            document.querySelector('.chart-wrapper').innerHTML = '<p style="text-align: center;">No data to display</p>';
            return;
        }

        // Prepare chart data
        const previousMarks = data.predictions.map(p => p.previous);
        const predictedMarks = data.predictions.map(p => p.predicted);

        // Create chart
        const ctx = document.getElementById('comparisonChart').getContext('2d');
        
        if (comparisonChart) {
            comparisonChart.destroy();
        }

        comparisonChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.student_names,
                datasets: [
                    {
                        label: 'Previous Semester CGPA',
                        data: previousMarks,
                        backgroundColor: 'rgba(52, 152, 219, 0.7)',
                        borderColor: 'rgba(52, 152, 219, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Predicted CGPA',
                        data: predictedMarks,
                        backgroundColor: 'rgba(46, 204, 113, 0.7)',
                        borderColor: 'rgba(46, 204, 113, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            callback: function(value) {
                                return value;
                            }
                        }
                    }
                }
            }
        });

    } catch (error) {
        console.error('Error loading comparison chart:', error);
    }
}

// Export data as CSV
function exportData() {
    try {
        fetch(`${API_BASE_URL}/student-records`)
            .then(response => response.json())
            .then(data => {
                if (data.records.length === 0) {
                    showAlert('No data to export', 'info');
                    return;
                }

                // Prepare CSV
                const headers = ['Student Name', 'Student ID', 'Attendance %', 'Internal CGPA', 'Study Hours', 'Previous CGPA', 'Predicted CGPA', 'Date'];
                const rows = data.records.map(record => [
                    record.student_name,
                    record.student_id,
                    record.attendance.toFixed(2),
                    record.internal_marks.toFixed(2),
                    record.study_hours.toFixed(2),
                    record.previous_semester_marks.toFixed(2),
                    record.predicted_marks.toFixed(2),
                    formatDate(record.prediction_date)
                ]);

                // Create CSV content
                const csvContent = [
                    headers.join(','),
                    ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
                ].join('\n');

                // Download CSV
                const blob = new Blob([csvContent], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `exam-predictions-${new Date().toISOString().split('T')[0]}.csv`;
                a.click();
                window.URL.revokeObjectURL(url);

                showAlert('Data exported successfully!', 'success');
            });
    } catch (error) {
        console.error('Export Error:', error);
        showAlert('Failed to export data', 'error');
    }
}

// Retrain model
async function retrainModel(btn) {
    if (!confirm('This will retrain the model with current database records. Continue?')) {
        return;
    }

    try {
        const submitBtn = btn || event.target;
        submitBtn.disabled = true;
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Retraining...';

        const response = await apiCall('/retrain-model', {
            method: 'POST'
        });

        showAlert(response.message, 'success');

        // Reload model info
        setTimeout(() => {
            loadModelInfo();
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }, 1000);

    } catch (error) {
        console.error('Retrain Error:', error);
        showAlert('Failed to retrain model: ' + error.message, 'error');
        if (btn) btn.disabled = false;
        if (btn) btn.textContent = 'Retrain Model';
    }
}

// Refresh dashboard
function refreshDashboard() {
    location.reload();
}
