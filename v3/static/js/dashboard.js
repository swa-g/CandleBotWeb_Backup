document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('stockSearch');
    const searchResults = document.getElementById('searchResults');
    const selectedStockName = document.getElementById('selectedStockName');
    const chartContainer = document.getElementById('chartContainer');
    let chart = null;
    let candleSeries = null;

    // Initialize the chart
    function initChart() {
        if (chart) {
            chartContainer.innerHTML = '';
        }

        chart = LightweightCharts.createChart(chartContainer, {
            width: chartContainer.clientWidth,
            height: 500,
            layout: {
                background: { color: '#ffffff' },
                textColor: '#333',
            },
            grid: {
                vertLines: { color: '#f0f0f0' },
                horzLines: { color: '#f0f0f0' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: '#d1d4dc',
            },
            timeScale: {
                borderColor: '#d1d4dc',
            },
        });

        candleSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350'
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            chart.applyOptions({
                width: chartContainer.clientWidth
            });
        });
    }

    // Initialize chart on load
    initChart();

    // Search functionality
    let searchTimeout = null;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            searchResults.classList.add('d-none');
            return;
        }

        searchTimeout = setTimeout(() => {
            fetch(`/search_stocks?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = '';
                    data.forEach(stock => {
                        const item = document.createElement('a');
                        item.href = '#';
                        item.className = 'list-group-item list-group-item-action';
                        item.textContent = `${stock.symbol} - ${stock.name}`;
                        item.addEventListener('click', (e) => {
                            e.preventDefault();
                            loadStockData(stock.symbol);
                            searchResults.classList.add('d-none');
                            searchInput.value = `${stock.symbol} - ${stock.name}`;
                        });
                        searchResults.appendChild(item);
                    });
                    searchResults.classList.remove('d-none');
                })
                .catch(error => console.error('Error:', error));
        }, 300);
    });

    // Load stock data
    function loadStockData(symbol) {
        selectedStockName.textContent = symbol;
        
        fetch(`/get_stock_data?symbol=${encodeURIComponent(symbol)}`)
            .then(response => response.json())
            .then(data => {
                candleSeries.setData(data);
            })
            .catch(error => console.error('Error:', error));
    }

    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchResults.contains(e.target) && e.target !== searchInput) {
            searchResults.classList.add('d-none');
        }
    });
});
