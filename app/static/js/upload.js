/**
 * upload.js — Upload Page Logic
 * FishDetect 🐟 — Fish Disease Detection System
 *
 * Handles:
 *   - Drag-and-drop file upload
 *   - Image preview with FileReader API
 *   - File validation (format + size)
 *   - AJAX POST to /predict via Fetch API
 *   - Loading state animation
 *   - Error handling with friendly messages
 */

document.addEventListener('DOMContentLoaded', function () {
    // ============================================================
    // DOM Elements
    // ============================================================
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const previewImg = document.getElementById('previewImg');
    const imagePreview = document.getElementById('imagePreview');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const submitBtn = document.getElementById('submitBtn');
    const changeImage = document.getElementById('changeImage');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const uploadForm = document.getElementById('uploadForm');
    const uploadCard = document.getElementById('uploadCard');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    // ============================================================
    // Constants
    // ============================================================
    const ALLOWED_TYPES = ['image/jpeg', 'image/png'];
    const ALLOWED_EXTS = ['.jpg', '.jpeg', '.png'];
    const MAX_SIZE_MB = 5;
    const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

    // ============================================================
    // Drag & Drop Events
    // ============================================================

    // Prevent default browser behavior for drag events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, function (e) {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    // Visual feedback on drag enter/over
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, function () {
            dropZone.classList.add('drag-over');
        });
    });

    // Remove visual feedback on drag leave/drop
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, function () {
            dropZone.classList.remove('drag-over');
        });
    });

    // Handle dropped file
    dropZone.addEventListener('drop', function (e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    // ============================================================
    // Click to Upload
    // ============================================================
    dropZone.addEventListener('click', function (e) {
        // Don't trigger if clicking the "Ganti Gambar" button
        if (e.target === changeImage || changeImage.contains(e.target)) {
            return;
        }
        fileInput.click();
    });

    // File input change
    fileInput.addEventListener('change', function () {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });

    // ============================================================
    // Change Image Button
    // ============================================================
    changeImage.addEventListener('click', function (e) {
        e.stopPropagation();
        resetUpload();
        fileInput.click();
    });

    // ============================================================
    // File Handler — Validate + Preview
    // ============================================================
    function handleFile(file) {
        hideError();

        // Validate file type (MIME type check)
        if (!ALLOWED_TYPES.includes(file.type)) {
            showError(
                'Format file tidak didukung. Gunakan file JPG atau PNG saja.'
            );
            return;
        }

        // Validate file extension (extra safety)
        const ext = '.' + file.name.split('.').pop().toLowerCase();
        if (!ALLOWED_EXTS.includes(ext)) {
            showError(
                'Ekstensi file tidak valid. Gunakan file .jpg, .jpeg, atau .png.'
            );
            return;
        }

        // Validate file size
        if (file.size > MAX_SIZE_BYTES) {
            const sizeMB = (file.size / 1024 / 1024).toFixed(1);
            showError(
                `Ukuran file terlalu besar (${sizeMB} MB). Maksimal ${MAX_SIZE_MB} MB.`
            );
            return;
        }

        // Set file to input (for drag-drop case)
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        fileInput.files = dataTransfer.files;

        // Show preview
        showPreview(file);
    }

    // ============================================================
    // Preview Image
    // ============================================================
    function showPreview(file) {
        const reader = new FileReader();

        reader.onload = function (e) {
            previewImg.src = e.target.result;
            imagePreview.classList.remove('d-none');
            uploadPlaceholder.classList.add('d-none');
            submitBtn.disabled = false;

            // File info
            fileName.textContent = file.name;
            const sizeMB = (file.size / 1024 / 1024).toFixed(2);
            fileSize.textContent = `${sizeMB} MB`;
        };

        reader.onerror = function () {
            showError('Gagal membaca file gambar. Silakan coba lagi.');
        };

        reader.readAsDataURL(file);
    }

    // ============================================================
    // Reset Upload State
    // ============================================================
    function resetUpload() {
        fileInput.value = '';
        previewImg.src = '';
        imagePreview.classList.add('d-none');
        uploadPlaceholder.classList.remove('d-none');
        submitBtn.disabled = true;
        fileName.textContent = '';
        fileSize.textContent = '';
        hideError();
    }

    // ============================================================
    // Error Display
    // ============================================================
    function showError(msg) {
        errorMessage.textContent = msg;
        errorAlert.classList.remove('d-none');

        // Scroll to error
        errorAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function hideError() {
        errorAlert.classList.add('d-none');
    }

    // ============================================================
    // Form Submit — AJAX POST to /predict
    // ============================================================
    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();
        hideError();

        // Validate file is selected
        if (!fileInput.files || fileInput.files.length === 0) {
            showError('Pilih gambar ikan terlebih dahulu.');
            return;
        }

        // Show loading state
        showLoading();

        // Build FormData
        const formData = new FormData(uploadForm);

        // AJAX POST
        fetch(uploadForm.action, {
            method: 'POST',
            body: formData
        })
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                if (data.status === 'success') {
                    // Redirect to result page
                    window.location.href = data.redirect_url;
                } else {
                    // Show error from server
                    hideLoading();
                    showError(data.message || 'Terjadi kesalahan saat menganalisis gambar.');
                }
            })
            .catch(function (err) {
                console.error('Upload error:', err);
                hideLoading();
                showError(
                    'Terjadi kesalahan koneksi ke server. ' +
                    'Pastikan server berjalan dan coba lagi.'
                );
            });
    });

    // ============================================================
    // Loading State
    // ============================================================
    function showLoading() {
        // Hide form content, show loading overlay
        uploadForm.classList.add('d-none');
        loadingOverlay.classList.remove('d-none');

        // Animate card
        uploadCard.style.transition = 'all 0.3s ease';
    }

    function hideLoading() {
        // Show form content, hide loading overlay
        uploadForm.classList.remove('d-none');
        loadingOverlay.classList.add('d-none');

        // Re-enable submit button
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="bi bi-search me-2"></i> Deteksi Penyakit';
    }
});
