document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadStatus = document.getElementById('uploadStatus');
    const activityBody = document.getElementById('activityBody');
    const ratingForm = document.getElementById('ratingForm');
    const ratingStatus = document.getElementById('ratingStatus');
    
    // Add elements for dynamic validation
    const processOption = document.getElementById('processOption');
    const preset = document.getElementById('preset');
    
    let currentUploadId = null;
    
    // Load activity history on page load
    loadActivityHistory();
    
    // Add event listeners for dynamic validation
    processOption.addEventListener('change', validatePresetCombination);
    preset.addEventListener('change', validatePresetCombination);
    
    // Validate preset combination function
    function validatePresetCombination() {
        const selectedProcess = processOption.value;
        const selectedPreset = preset.value;
        
        // Check for incompatible combination
        if (selectedProcess === 'mp4' && selectedPreset === 'flashvideo') {
            showStatus('Warning: MP4 conversion with flashvideo preset is not supported. Please select a different preset.', 'error');
            // Disable the submit button
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Invalid Configuration';
        } else {
            // Clear any previous warnings and enable submit button
            if (uploadStatus.textContent.includes('Warning: MP4 conversion with flashvideo')) {
                uploadStatus.textContent = '';
                uploadStatus.className = 'status-message';
            }
            const submitBtn = uploadForm.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Process Video';
        }
    }
    
    // Form submission handler
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const videoFile = document.getElementById('videoFile').files[0];
        const processOption = document.getElementById('processOption').value;
        const preset = document.getElementById('preset').value || 'divx'; // Use divx as default if not provided
        
        if (!videoFile) {
            showStatus('Please select a video file.', 'error');
            return;
        }
        
        if (!processOption) {
            showStatus('Please select a processing option.', 'error');
            return;
        }
        
        // Double-check for incompatible combination before submission
        if (processOption === 'mp4' && preset === 'flashvideo') {
            showStatus('Error: MP4 conversion with flashvideo preset is not supported. Please select a different preset.', 'error');
            return;
        }
        
        try {
            showStatus('Uploading video...', '');
            
            // Upload the file
            const uploadResult = await uploadVideo(videoFile);
            currentUploadId = uploadResult.activity.id;
            
            showStatus('Processing video...', '');
            
            // Process the video with the selected preset
            const processResult = await processVideo(currentUploadId, processOption, preset);
            
            showStatus('Video processed successfully!', 'success');
            
            // Refresh the activity history
            loadActivityHistory();
            
            // Reset the form
            uploadForm.reset();
            
        } catch (error) {
            showStatus(`Error: Choose another combination of processing option and preset.`, 'error');

            console.error('Error:', error);
        }
    });
    

    
    // Rating form submission handler
    if (ratingForm) {
        ratingForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const userId = document.getElementById('userId').value;
            const ratingInputs = document.getElementsByName('rating');
            const comment = document.getElementById('comment').value;
            
            let selectedRating = null;
            for (let i = 0; i < ratingInputs.length; i++) {
                if (ratingInputs[i].checked) {
                    selectedRating = ratingInputs[i].value;
                    break;
                }
            }
            
            if (!userId || !selectedRating) {
                showRatingStatus('Please fill in all required fields.', 'error');
                return;
            }
            
            try {
                showRatingStatus('Submitting your rating...', '');
                
                const response = await fetch('/rate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        userId: userId,
                        rating: selectedRating,
                        comment: comment
                    })
                });
                
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Failed to submit rating');
                }
                
                const result = await response.json();
                showRatingStatus('Thank you for your feedback!', 'success');
                
                // Reset the form
                ratingForm.reset();
                
            } catch (error) {
                showRatingStatus(`Error: ${error.message}`, 'error');
                console.error('Error:', error);
            }
        });
    }
    
    // Upload video function
    async function uploadVideo(file) {
        const formData = new FormData();
        formData.append('video', file);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to upload video');
        }
        
        return await response.json();
    }
    
    // Process video function
    async function processVideo(id, processOption, preset) {
        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id, processOption, preset })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to process video');
        }
        
        return await response.json();
    }
    
    // Load activity history function
    async function loadActivityHistory() {
        try {
            const response = await fetch('/history');
            
            if (!response.ok) {
                throw new Error('Failed to fetch activity history');
            }
            
            const activities = await response.json();
            
            // Clear current activity table
            activityBody.innerHTML = '';
            
            // Add activities to the table
            activities.forEach(activity => {
                addActivityRow(activity);
            });
            
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }
    
    // Add a row to the activity table
    function addActivityRow(activity) {
        const row = document.createElement('tr');
        
        // Define status class
        let statusClass = '';
        switch (activity.status) {
            case 'Completed':
                statusClass = 'status-completed';
                break;
            case 'In Progress':
                statusClass = 'status-inprogress';
                break;
            case 'Failed':
                statusClass = 'status-failed';
                break;
            default:
                statusClass = '';
        }
        
        // Format timestamp to be more readable
        const timestamp = new Date(activity.timestamp).toLocaleString();
        
        // Format process option for display
        let processOptionDisplay = 'N/A';
        if (activity.processOption) {
            switch (activity.processOption) {
                case 'mp4':
                    processOptionDisplay = `Convert to MP4 (${activity.preset || 'medium'})`;
                    break;
                case '720p':
                    processOptionDisplay = `Resize to 720p (${activity.preset || 'medium'})`;
                    break;
                case 'avi':
                    processOptionDisplay = `Change codec to AVI (${activity.preset || 'medium'})`;
                    break;
                default:
                    processOptionDisplay = activity.processOption;
            }
        }
        
        // Create action button or loading indicator
        let actionContent;
        if (activity.status === 'Completed' && activity.downloadLink) {
            actionContent = `<a href="${activity.downloadLink}" class="download-btn">Download</a>`;
        } else if (activity.status === 'In Progress') {
            actionContent = `<span class="loading"></span>`;
        } else {
            actionContent = 'N/A';
        }
        
        row.innerHTML = `
            <td>${activity.originalFileName}</td>
            <td>${processOptionDisplay}</td>
            <td>${timestamp}</td>
            <td class="${statusClass}">${activity.status}</td>
            <td>${actionContent}</td>
        `;
        
        activityBody.appendChild(row);
    }
    
    // Show status message
    function showStatus(message, type) {
        uploadStatus.textContent = message;
        uploadStatus.className = 'status-message';
        if (type) {
            uploadStatus.classList.add(type);
        }
    }
    
    // Show rating status message
    function showRatingStatus(message, type) {
        if (ratingStatus) {
            ratingStatus.textContent = message;
            ratingStatus.className = 'status-message';
            if (type) {
                ratingStatus.classList.add(type);
            }
        }
    }
    
    // Poll for activity updates if there's an active upload
    setInterval(async () => {
        if (currentUploadId) {
            try {
                const response = await fetch('/history');
                if (response.ok) {
                    const activities = await response.json();
                    const currentActivity = activities.find(a => a.id === currentUploadId);
                    
                    if (currentActivity && (currentActivity.status === 'Completed' || currentActivity.status === 'Failed')) {
                        // Update the status message
                        if (currentActivity.status === 'Completed') {
                            showStatus('Video processed successfully!', 'success');
                        } else {
                            showStatus('Video processing failed.', 'error');
                        }
                        
                        // Refresh the activity history
                        loadActivityHistory();
                        
                        // Reset the current upload ID
                        currentUploadId = null;
                    }
                }
            } catch (error) {
                console.error('Error polling for updates:', error);
            }
        }
    }, 2000);
});

