document.addEventListener('DOMContentLoaded', function () {
    var scrapeBtn = document.getElementById('scrapeBtn');
    if (scrapeBtn) {
        scrapeBtn.addEventListener('click', function () {
            scrapeBtn.textContent = 'Scraping...';
            scrapeBtn.disabled = true;
        });
    }
});
