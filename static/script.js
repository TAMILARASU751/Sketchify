document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const sketchOutput = document.getElementById('sketch-output');
    const sketchImage = document.getElementById('sketchImage');
    const pencilThicknessSlider = document.getElementById('pencil-thickness');
    const edgeSensitivitySlider = document.getElementById('edge-sensitivity');
    const brightnessSlider = document.getElementById('brightness');
    const contrastSlider = document.getElementById('contrast');
    const pencilThicknessValue = document.getElementById('pencil-thickness-value');
    const edgeSensitivityValue = document.getElementById('edge-sensitivity-value');
    const brightnessValue = document.getElementById('brightness-value');
    const contrastValue = document.getElementById('contrast-value');
    const resetButton = document.getElementById('reset-button');
    const conversionSelect = document.getElementById('conversion');
    const imageInput = document.getElementById('image-input');
    const loadingSpinner = document.getElementById('loading-spinner');

    // Update value displays for sliders
    function updateSliderDisplays() {
        pencilThicknessValue.textContent = `Pencil Thickness: ${pencilThicknessSlider.value}`;
        edgeSensitivityValue.textContent = `Edge Sensitivity: ${edgeSensitivitySlider.value}`;
        brightnessValue.textContent = `Brightness: ${brightnessSlider.value}`;
        contrastValue.textContent = `Contrast: ${contrastSlider.value}`;
    }

    // Slider event listeners
    pencilThicknessSlider.addEventListener('input', () => {
        updateSliderDisplays();
        updateSketch(); // Update sketch in real-time
    });

    edgeSensitivitySlider.addEventListener('input', () => {
        updateSliderDisplays();
        updateSketch(); // Update sketch in real-time
    });

    brightnessSlider.addEventListener('input', () => {
        updateSliderDisplays();
        updateSketch(); // Update sketch in real-time
    });

    contrastSlider.addEventListener('input', () => {
        updateSliderDisplays();
        updateSketch(); // Update sketch in real-time
    });

    // Reset slider values
    resetButton.addEventListener('click', () => {
        pencilThicknessSlider.value = 5;
        edgeSensitivitySlider.value = 5;
        brightnessSlider.value = 1;
        contrastSlider.value = 1;
        updateSliderDisplays(); // Update displayed values
        updateSketch(); // Update sketch in real-time
    });

    // Handle image upload
    imageInput.addEventListener('change', () => {
        if (imageInput.files.length > 0) {
            updateSketch(); // Update sketch when an image is uploaded
        }
    });

    // Handle style change
    conversionSelect.addEventListener('change', () => {
        updateSketch(); // Update sketch when style is changed
    });

    // Function to update the sketch based on current inputs
    async function updateSketch() {
        if (imageInput.files.length === 0) {
            return; // No image selected
        }

        // Show loading spinner
        loadingSpinner.style.display = 'block';

        const formData = new FormData(uploadForm);
        const response = await fetch('/convert', {
            method: 'POST',
            body: formData
        });

        // Hide loading spinner
        loadingSpinner.style.display = 'none';

        if (response.ok) {
            const data = await response.json();
            if (data.output_image) {
                sketchImage.src = data.output_image; // Update the image source
                sketchOutput.style.display = 'block'; // Show the output section
            } else {
                alert('Error: No output image returned.');
            }
        } else {
            alert('Error converting image. Please try again.');
        }
    }

    // Download the image
    window.downloadSketch = function() {
        if (sketchImage.src) {
            const link = document.createElement('a');
            link.href = sketchImage.src;
            link.download = 'sketch.png'; // Default name for the downloaded file
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            alert('No sketch available for download.');
        }
    };

    // Toggle About Section
    window.toggleAboutSection = function() {
        const aboutSection = document.getElementById('about-section');
        aboutSection.style.display = aboutSection.style.display === 'none' ? 'block' : 'none';
    };
});
