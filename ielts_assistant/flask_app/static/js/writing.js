document.getElementById('editor').addEventListener('input', function() {
    var text = this.value.trim();
    var wordCount = text.split(/\s+/).filter(Boolean).length;
    document.getElementById('word-count').textContent = wordCount;
});