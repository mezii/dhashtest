let selectedFiles = {
    1: null,
    2: null
};

let selectedAntiFile = null;

// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    if (tabName === 'compare') {
        document.getElementById('compareTab').classList.add('active');
        document.querySelectorAll('.tab-button')[0].classList.add('active');
    } else if (tabName === 'anti-dhash') {
        document.getElementById('antiDhashTab').classList.add('active');
        document.querySelectorAll('.tab-button')[1].classList.add('active');
    }
}

// Initialize drag and drop for both image boxes
function initializeDragAndDrop(boxNumber) {
    const dropZone = document.getElementById(`dropZone${boxNumber}`);
    const fileInput = document.getElementById(`fileInput${boxNumber}`);
    const preview = document.getElementById(`preview${boxNumber}`);
    const placeholder = document.getElementById(`placeholder${boxNumber}`);

    // Click to upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0], boxNumber);
        }
    });

    // Drag over
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    // Drag leave
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    // Drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0], boxNumber);
        }
    });
}

function handleFile(file, boxNumber) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }

    // Validate file size (16MB)
    if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
    }

    selectedFiles[boxNumber] = file;

    // Preview image
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById(`preview${boxNumber}`);
        const placeholder = document.getElementById(`placeholder${boxNumber}`);
        
        preview.src = e.target.result;
        preview.style.display = 'block';
        placeholder.style.display = 'none';
    };
    reader.readAsDataURL(file);

    // Hide result section when new image is uploaded
    document.getElementById('resultSection').style.display = 'none';
}

function clearImage(boxNumber) {
    selectedFiles[boxNumber] = null;
    
    const preview = document.getElementById(`preview${boxNumber}`);
    const placeholder = document.getElementById(`placeholder${boxNumber}`);
    const fileInput = document.getElementById(`fileInput${boxNumber}`);
    
    preview.style.display = 'none';
    preview.src = '';
    placeholder.style.display = 'block';
    fileInput.value = '';
    
    // Hide result section
    document.getElementById('resultSection').style.display = 'none';
}

async function compareImages() {
    // Validate that both images are selected
    if (!selectedFiles[1] || !selectedFiles[2]) {
        alert('Please select both images to compare');
        return;
    }

    // Show loading state
    const compareBtn = document.getElementById('compareBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    
    compareBtn.disabled = true;
    btnText.textContent = 'Comparing...';
    btnLoader.style.display = 'inline-block';

    // Create form data
    const formData = new FormData();
    formData.append('image1', selectedFiles[1]);
    formData.append('image2', selectedFiles[2]);

    try {
        // Send request to backend
        const response = await fetch('/compare', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to compare images');
        }

        // Display results
        displayResults(data);

    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Comparison error:', error);
    } finally {
        // Reset button state
        compareBtn.disabled = false;
        btnText.textContent = 'Compare Images';
        btnLoader.style.display = 'none';
    }
}

function displayResults(data) {
    const resultSection = document.getElementById('resultSection');
    const resultCard = document.getElementById('resultCard');
    const statusIcon = document.getElementById('statusIcon');
    const statusText = document.getElementById('statusText');
    const similarityValue = document.getElementById('similarityValue');
    const hammingValue = document.getElementById('hammingValue');
    const similarityFill = document.getElementById('similarityFill');

    // Update result card styling
    resultCard.className = 'result-card ' + (data.are_similar ? 'similar' : 'different');

    // Update status
    statusIcon.textContent = data.are_similar ? '✓' : '✗';
    statusText.textContent = data.message;

    // Update details
    similarityValue.textContent = data.similarity + '%';
    hammingValue.textContent = data.hamming_distance + ' bits';

    // Animate similarity bar
    setTimeout(() => {
        similarityFill.style.width = data.similarity + '%';
    }, 100);

    // Show result section with animation
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Anti-dHash functions
function initializeAntiDhashDragAndDrop() {
    const dropZone = document.getElementById('dropZoneAnti');
    const fileInput = document.getElementById('fileInputAnti');
    const preview = document.getElementById('previewAnti');
    const placeholder = document.getElementById('placeholderAnti');

    // Click to upload
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleAntiFile(e.target.files[0]);
        }
    });

    // Drag over
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    // Drag leave
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    // Drop
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length > 0) {
            handleAntiFile(e.dataTransfer.files[0]);
        }
    });
}

function handleAntiFile(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }

    // Validate file size (16MB)
    if (file.size > 16 * 1024 * 1024) {
        alert('File size must be less than 16MB');
        return;
    }

    selectedAntiFile = file;

    // Preview image
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById('previewAnti');
        const placeholder = document.getElementById('placeholderAnti');
        
        preview.src = e.target.result;
        preview.style.display = 'block';
        placeholder.style.display = 'none';
    };
    reader.readAsDataURL(file);

    // Hide result section
    document.getElementById('antiResultSection').style.display = 'none';
}

function clearAntiImage() {
    selectedAntiFile = null;
    
    const preview = document.getElementById('previewAnti');
    const placeholder = document.getElementById('placeholderAnti');
    const fileInput = document.getElementById('fileInputAnti');
    
    preview.style.display = 'none';
    preview.src = '';
    placeholder.style.display = 'block';
    fileInput.value = '';
    
    // Hide result section
    document.getElementById('antiResultSection').style.display = 'none';
}

async function modifyImage() {
    // Validate that image is selected
    if (!selectedAntiFile) {
        alert('Please select an image to modify');
        return;
    }

    // Show loading state
    const modifyBtn = document.getElementById('modifyBtn');
    const btnText = document.getElementById('modifyBtnText');
    const btnLoader = document.getElementById('modifyBtnLoader');
    
    modifyBtn.disabled = true;
    btnText.textContent = 'Modifying...';
    btnLoader.style.display = 'inline-block';

    // Create form data
    const formData = new FormData();
    formData.append('image', selectedAntiFile);

    try {
        // Send request to backend
        const response = await fetch('/anti-dhash', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to modify image');
        }

        // Display results
        displayAntiResults(data);

    } catch (error) {
        alert('Error: ' + error.message);
        console.error('Modification error:', error);
    } finally {
        // Reset button state
        modifyBtn.disabled = false;
        btnText.textContent = 'Modify Image';
        btnLoader.style.display = 'none';
    }
}

function displayAntiResults(data) {
    const resultSection = document.getElementById('antiResultSection');
    const originalHashValue = document.getElementById('originalHashValue');
    const newHashValue = document.getElementById('newHashValue');
    const antiHammingValue = document.getElementById('antiHammingValue');
    const downloadLink = document.getElementById('downloadLink');

    // Update details
    originalHashValue.textContent = data.original_hash;
    newHashValue.textContent = data.new_hash;
    antiHammingValue.textContent = data.hamming_distance + ' bits';

    // Set download link
    downloadLink.href = data.download_url;

    // Show result section with animation
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeDragAndDrop(1);
    initializeDragAndDrop(2);
    initializeAntiDhashDragAndDrop();
});
