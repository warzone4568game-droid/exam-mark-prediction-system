// Form.js - Handle prediction form submission and image upload

let selectedImage = null;

// Initialize form
document.addEventListener('DOMContentLoaded', function() {
    setupImageUpload();
    setupFormSubmission();
    setupInternalCalculation();
});

// Setup internal marks calculation
function setupInternalCalculation() {
    const int1 = document.getElementById('int1');
    const int2 = document.getElementById('int2');
    const int3 = document.getElementById('int3');
    const attendance = document.getElementById('attendance');

    if (!int1 || !int2 || !int3 || !attendance) return;

    const updateTotals = () => {
        const v1 = Math.min(100, Math.max(0, parseFloat(int1.value) || 0));
        const v2 = Math.min(100, Math.max(0, parseFloat(int2.value) || 0));
        const v3 = Math.min(100, Math.max(0, parseFloat(int3.value) || 0));
        const attP = Math.min(100, Math.max(0, parseFloat(attendance.value) || 0));

        const conv1 = (v1 / 100) * 5;
        const conv2 = (v2 / 100) * 10;
        const conv3 = (v3 / 100) * 10;
        
        let attM = 0;
        if (attP >= 95) {
            attM = 5;
        } else if (attP >= 91) {
            attM = 4;
        } else if (attP >= 86) {
            attM = 3;
        } else if (attP >= 81) {
            attM = 2;
        } else if (attP >= 75) {
            attM = 1;
        } else {
            attM = 0;
        }

        document.getElementById('int1_conv').textContent = conv1.toFixed(2);
        document.getElementById('int2_conv').textContent = conv2.toFixed(2);
        document.getElementById('int3_conv').textContent = conv3.toFixed(2);
        document.getElementById('att_mark_display').textContent = attM;
        document.getElementById('att_mark_conv').textContent = attM;

        const total = conv1 + conv2 + conv3 + attM;
        document.getElementById('totalInternalDisplay').textContent = total.toFixed(2);
        document.getElementById('internalMarks').value = total.toFixed(2);
    };

    [int1, int2, int3, attendance].forEach(el => {
        el.addEventListener('input', updateTotals);
    });
}


// Setup image upload area
function setupImageUpload() {
    const uploadArea = document.getElementById('imageUploadArea');
    const fileInput = document.getElementById('resultImage');

    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = 'rgba(52, 152, 219, 0.1)';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.backgroundColor = '#f8f9fa';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.backgroundColor = '#f8f9fa';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleImageSelect(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleImageSelect(e.target.files[0]);
        }
    });
}

// Handle image selection
async function handleImageSelect(file) {
    // Validate file
    const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/bmp'];
    if (!allowedTypes.includes(file.type)) {
        showAlert('Invalid file type. Please upload an image (PNG, JPG, GIF, BMP)', 'error');
        return;
    }

    if (file.size > 16 * 1024 * 1024) {
        showAlert('File size exceeds 16MB limit', 'error');
        return;
    }

    selectedImage = file;

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('imagePreview').style.display = 'block';
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('imageUploadArea').style.display = 'none';

        // Process image with OCR
        processImage(file);
    };
    reader.readAsDataURL(file);
}

// Process image with OCR
async function processImage(file) {
    try {
        const formData = new FormData();
        formData.append('image', file);

        const response = await fetch(`${API_BASE_URL}/upload-image`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Image processing failed');
        }

        const data = await response.json();

        // Display OCR results
        displayOCRResults(data);

        // Auto-fill marks if detected
        if (data.parsed_marks && data.parsed_marks.obtained_marks) {
            document.getElementById('previousMarks').value = formatNumber(data.parsed_marks.obtained_marks);
        }

        showAlert('Image processed successfully!', 'success');
    } catch (error) {
        console.error('OCR Error:', error);
        showAlert('Failed to process image: ' + error.message, 'error');
    }
}

// Display OCR results
function displayOCRResults(data) {
    const ocrResults = document.getElementById('ocrResults');
    const ocrContent = document.getElementById('ocrContent');

    let content = '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">';
    
    if (data.parsed_marks) {
        const marks = data.parsed_marks;
        content += `
            <p><strong>Detected CGPA/Marks:</strong> ${marks.obtained_marks || 'Not detected'}</p>
            <p><strong>Out of:</strong> ${marks.total_marks || 'Not detected'}</p>
            <p><strong>Grade:</strong> ${marks.grade || 'Not detected'}</p>
        `;
    }

    if (data.extracted_text) {
        content += `<p><strong>Raw Text:</strong></p><small style="word-break: break-all; color: #666;">${data.extracted_text.substring(0, 200)}...</small>`;
    }

    content += '</div>';
    ocrContent.innerHTML = content;
    ocrResults.style.display = 'block';
}

// Clear image
function clearImage() {
    selectedImage = null;
    document.getElementById('resultImage').value = '';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('ocrResults').style.display = 'none';
    document.getElementById('imageUploadArea').style.display = 'block';
}

// Setup form submission
function setupFormSubmission() {
    const form = document.getElementById('predictionForm');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validate form
        const studentName = document.getElementById('studentName').value;
        const studentId = document.getElementById('studentId').value;
        const attendance = parseFloat(document.getElementById('attendance').value);
        const internalMarks = parseFloat(document.getElementById('internalMarks').value);
        const studyHours = parseFloat(document.getElementById('studyHours').value);
        const previousMarks = parseFloat(document.getElementById('previousMarks').value);

        // Validation
        if (!studentName || !studentId) {
            showAlert('Please enter student name and ID', 'error');
            return;
        }

        if (attendance < 0 || attendance > 100 || previousMarks < 0 || previousMarks > 10) {
            showAlert('Attendance must be 0-100%, Previous CGPA must be between 0 and 10', 'error');
            return;
        }

        if (studyHours < 0 || studyHours > 24) {
            showAlert('Study hours must be between 0 and 24', 'error');
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Processing...';
        submitBtn.disabled = true;

        try {
            // Make prediction
            const predictionData = {
                student_name: studentName,
                student_id: studentId,
                attendance: attendance,
                internal_marks: internalMarks,
                study_hours: studyHours,
                previous_semester_marks: previousMarks
            };

            const response = await apiCall('/predict', {
                method: 'POST',
                body: JSON.stringify(predictionData)
            });

            // Display results
            displayResults(response, previousMarks, attendance, internalMarks, studyHours);

            showAlert('Prediction completed successfully!', 'success');

        } catch (error) {
            console.error('Prediction Error:', error);
            showAlert('Prediction failed: ' + error.message, 'error');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    });
}

// Helper to convert CGPA to Letter Grade
function getGrade(cgpa) {
    if (cgpa >= 9.5) return { letter: 'O', label: 'Outstanding', color: '#1b5e20', bg: '#c8e6c9' }; // Deep Green
    if (cgpa >= 9.0) return { letter: 'A+', label: 'Excellent', color: '#2e7d32', bg: '#e8f5e9' };
    if (cgpa >= 8.0) return { letter: 'A', label: 'Very Good', color: '#1565c0', bg: '#e3f2fd' }; // Deep Blue
    if (cgpa >= 7.0) return { letter: 'B+', label: 'Good', color: '#f57f17', bg: '#fffde7' }; // Deep Yellow/Orange
    if (cgpa >= 6.0) return { letter: 'B', label: 'Above Average', color: '#ef6c00', bg: '#fff3e0' };
    if (cgpa >= 5.0) return { letter: 'C', label: 'Average', color: '#455a64', bg: '#eceff1' };
    return { letter: 'U', label: 'Re-appear', color: '#c62828', bg: '#ffebee' }; // Deep Red
}

// Display prediction results
function displayResults(data, previousMarks, attendance, internalMarks, studyHours) {
    const resultsSection = document.getElementById('resultsSection');
    const predGrade = getGrade(data.predicted_marks);

    // Update result cards with high-visibility styling
    document.getElementById('predictedMarks').innerHTML = `
        <div style="font-size: 3.8rem; font-weight: 900; color: #ffffff; line-height: 1; text-shadow: 0 2px 4px rgba(0,0,0,0.1);">${formatNumber(data.predicted_marks)}</div>
        <div style="margin-top: 15px; display: inline-block; padding: 10px 25px; border-radius: 50px; background: #ffffff; color: ${predGrade.color}; font-weight: 800; font-size: 1.2rem; border: 3px solid ${predGrade.color}; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            Grade: ${predGrade.letter} (${predGrade.label})
        </div>
    `;
    
    document.getElementById('r2Score').textContent = formatNumber(data.accuracy_metrics.r2_score);
    document.getElementById('rmseValue').textContent = formatNumber(data.accuracy_metrics.rmse);
    document.getElementById('mseValue').textContent = formatNumber(data.accuracy_metrics.mse);

    // Update Improved Comparison Bars
    const prevPercentage = (previousMarks / 10) * 100;
    const predPercentage = (data.predicted_marks / 10) * 100;

    document.getElementById('prevValueLabel').textContent = formatNumber(previousMarks);
    document.getElementById('prevBarFill').style.width = prevPercentage + '%';

    document.getElementById('predValueLabel').textContent = formatNumber(data.predicted_marks);
    document.getElementById('predBarFill').style.width = predPercentage + '%';

    // Generate Roadmap & Focus Areas
    generateRecommendations(data.predicted_marks, previousMarks, attendance, internalMarks, studyHours);

    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Generate personalized Success Roadmap
function generateRecommendations(predictedMarks, previousMarks, attendance, internalMarks, studyHours) {
    const badge = document.getElementById('performanceBadge');
    const keyInsight = document.getElementById('keyInsight');
    const criticalAction = document.getElementById('criticalAction');
    const aiAnalysis = document.getElementById('aiAnalysis');
    const focusContainer = document.getElementById('focusAreasContainer');

    // 1. Determine Performance Category & Badge
    const predGrade = getGrade(predictedMarks);
    badge.textContent = `Predicted Grade: ${predGrade.letter}`;
    badge.style.background = predGrade.bg;
    badge.style.color = predGrade.color;
    badge.style.border = `2px solid ${predGrade.color}`;
    badge.style.fontWeight = '800';
    badge.style.padding = '8px 20px';
    badge.style.borderRadius = '50px';

    // 2. Determine Key Insight (The "Why")
    let whyText = "";
    if (predictedMarks < previousMarks) {
        whyText = `Your prediction is currently <strong>${(previousMarks - predictedMarks).toFixed(2)} lower</strong> than your previous semester. This is likely due to the gap in current study intensity or internal marks compared to your baseline.`;
    } else {
        whyText = `Your prediction shows a <strong>positive trend</strong>. This is supported by your current performance metrics which are successfully building upon your previous CGPA of ${formatNumber(previousMarks)}.`;
    }
    keyInsight.innerHTML = whyText;

    // 3. Determine Critical Action (The "Increase")
    // Calculate a "Potential Max"
    const potentialMax = Math.min(10, predictedMarks + 0.8);
    const potentialGrade = getGrade(potentialMax);
    
    let actionText = "";
    if (predictedMarks < 9.5) {
        actionText = `<strong>Target Grade ${potentialGrade.letter}:</strong> By optimizing your focus areas, you can realistically increase your subject score from <strong>${formatNumber(predictedMarks)}</strong> to <strong>${formatNumber(potentialMax)}</strong>. This would elevate your grade from ${predGrade.letter} to ${potentialGrade.letter}.`;
    } else {
        actionText = "<strong>Maintain Perfection:</strong> You are already in the top percentile. Focus on sustaining this level of performance to secure your 'O' grade.";
    }
    criticalAction.innerHTML = actionText;

    // 4. Populate Focus Areas
    const focusAreas = [];
    if (attendance < 85) {
        focusAreas.push({ title: "Attendance Optimization", impact: "High", reason: "Bridging the attendance gap to 90%+ could add ~0.3 to your subject grade point.", color: "#e74c3c" });
    }
    if (internalMarks < 26) {
        focusAreas.push({ title: "Internal Mark Recovery", impact: "Critical", reason: "Every 2 points gained in internals directly translates to a ~0.2 increase in your final CGPA prediction.", color: "#3498db" });
    }
    if (studyHours < 5) {
        focusAreas.push({ title: "Study Discipline", impact: "Medium", reason: "Increasing daily focus to 5-6 hours provides the 'consistency buffer' needed for high-grade stability.", color: "#2ecc71" });
    }

    focusContainer.innerHTML = focusAreas.length > 0 ? focusAreas.map(area => `
        <div style="display: flex; gap: 15px; padding: 12px; border-radius: 8px; background: #f8f9fa; border-left: 4px solid ${area.color};">
            <div style="font-weight: 700; min-width: 180px; color: ${area.color};">${area.title}</div>
            <div style="flex: 1; font-size: 0.9rem; color: #555;">
                <strong>Goal:</strong> ${area.reason} <br>
                <span style="display: inline-block; margin-top: 4px; font-size: 0.8rem; background: #eee; padding: 2px 6px; border-radius: 4px;">Priority: ${area.impact}</span>
            </div>
        </div>
    `).join('') : '<p style="color: #27ae60; font-weight: 600;">✅ Your current metrics are optimized for your potential! Maintain this pace.</p>';

    // 5. AI General Analysis
    const diff = predictedMarks - previousMarks;
    aiAnalysis.innerHTML = `This prediction represents the <strong>subject-level grade point</strong>. In our model, we consider ${formatNumber(previousMarks)} as your historic capability, and your current inputs suggest you are ${diff >= 0 ? 'exceeding' : 'trailing'} that baseline by ${Math.abs(diff).toFixed(2)} points.`;
}
