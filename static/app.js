document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfoCard = document.getElementById('fileInfoCard');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const convertBtn = document.getElementById('convertBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');

    const statsCard = document.getElementById('statsCard');
    const statType = document.getElementById('statType');
    const statWords = document.getElementById('statWords');
    const statChars = document.getElementById('statChars');
    const statLines = document.getElementById('statLines');

    const downloadMdBtn = document.getElementById('downloadMdBtn');
    const downloadJsonBtn = document.getElementById('downloadJsonBtn');

    const placeholderState = document.getElementById('placeholderState');
    const mdRenderedContent = document.getElementById('mdRenderedContent');
    const rawMdContent = document.getElementById('rawMdContent');
    const jsonAstContent = document.getElementById('jsonAstContent');

    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    let selectedFile = null;

    // Drag & Drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });

    function handleFileSelect(file) {
        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);
        fileInfoCard.classList.remove('hidden');
    }

    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Convert button handler
    convertBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        // UI Loading state
        convertBtn.disabled = true;
        btnText.textContent = "Converting...";
        btnSpinner.classList.remove('hidden');

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Conversion failed');
            }

            const data = await response.json();

            // Update stats
            statType.textContent = data.metadata.file_type || 'DOCUMENT';
            statWords.textContent = data.metadata.word_count || 0;
            statChars.textContent = data.metadata.char_count || 0;
            statLines.textContent = data.metadata.line_count || 0;
            statsCard.classList.remove('hidden');

            // Update download links
            downloadMdBtn.href = data.download_md_url;
            downloadJsonBtn.href = data.download_json_url;

            // Render Markdown using marked.js
            placeholderState.classList.add('hidden');
            mdRenderedContent.classList.remove('hidden');
            if (window.marked) {
                mdRenderedContent.innerHTML = marked.parse(data.markdown);
            } else {
                mdRenderedContent.innerText = data.markdown;
            }

            // Raw Markdown View
            rawMdContent.textContent = data.markdown;

            // JSON AST View
            try {
                const jsonObj = typeof data.json === 'string' ? JSON.parse(data.json) : data.json;
                jsonAstContent.textContent = JSON.stringify(jsonObj, null, 2);
            } catch (e) {
                jsonAstContent.textContent = data.json;
            }

        } catch (error) {
            alert('Error converting file: ' + error.message);
        } finally {
            convertBtn.disabled = false;
            btnText.textContent = "Convert File";
            btnSpinner.classList.add('hidden');
        }
    });

    // Tab switcher logic
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetTab = btn.getAttribute('data-tab');
            document.getElementById(targetTab).classList.add('active');
        });
    });
});
