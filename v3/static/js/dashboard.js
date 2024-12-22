document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('stockSearch');
    const searchResults = document.getElementById('searchResults');
    const selectedStockName = document.getElementById('selectedStockName');
    const chartContainer = document.getElementById('chartContainer');
    let chart = null;
    let candleSeries = null;
    let currentSymbol = null;
    let priceUpdateInterval = null;

    // Format price with Indian Rupee symbol
    function formatPrice(price) {
        return '₹' + price.toLocaleString('en-IN', {
            maximumFractionDigits: 2,
            minimumFractionDigits: 2
        });
    }

    // Format percentage
    function formatPercent(percent) {
        return (percent > 0 ? '+' : '') + percent.toFixed(2) + '%';
    }

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
                format: formatPrice,
            },
            timeScale: {
                borderColor: '#d1d4dc',
                timeVisible: true,
                secondsVisible: false,
            },
            localization: {
                priceFormatter: formatPrice,
            },
        });

        candleSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderVisible: false,
            wickUpColor: '#26a69a',
            wickDownColor: '#ef5350',
            priceFormat: {
                type: 'price',
                formatter: formatPrice,
            },
        });

        // Add price scale legend
        chart.priceScale('right').applyOptions({
            scaleMargins: {
                top: 0.1,
                bottom: 0.2,
            },
            borderVisible: true,
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            chart.applyOptions({
                width: chartContainer.clientWidth
            });
        });

        // Add tooltip
        chart.subscribeCrosshairMove(param => {
            if (param.time) {
                const data = param.seriesData.get(candleSeries);
                if (data) {
                    const tooltip = document.getElementById('tooltip') || createTooltip();
                    tooltip.style.display = 'block';
                    tooltip.style.left = param.point.x + 'px';
                    tooltip.style.top = param.point.y + 'px';
                    tooltip.innerHTML = `
                        <div>Open: ${formatPrice(data.open)}</div>
                        <div>High: ${formatPrice(data.high)}</div>
                        <div>Low: ${formatPrice(data.low)}</div>
                        <div>Close: ${formatPrice(data.close)}</div>
                        <div>Volume: ${data.volume.toLocaleString('en-IN')}</div>
                    `;
                }
            }
        });
    }

    // Create tooltip element
    function createTooltip() {
        const tooltip = document.createElement('div');
        tooltip.id = 'tooltip';
        tooltip.className = 'chart-tooltip';
        chartContainer.appendChild(tooltip);
        return tooltip;
    }

    // Update latest price
    function updateLatestPrice() {
        if (!currentSymbol) return;

        fetch(`/get_latest_price?symbol=${encodeURIComponent(currentSymbol)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                    return;
                }

                // Update price display
                const priceInfo = document.getElementById('priceInfo') || createPriceInfo();
                const changeClass = data.change >= 0 ? 'text-success' : 'text-danger';
                const changeIcon = data.change >= 0 ? '▲' : '▼';

                priceInfo.innerHTML = `
                    <div class="current-price">${formatPrice(data.price)}</div>
                    <div class="${changeClass}">
                        ${changeIcon} ${formatPrice(Math.abs(data.change))} (${formatPercent(data.changePercent)})
                    </div>
                    <div class="text-muted">
                        Volume: ${data.volume.toLocaleString('en-IN')}
                    </div>
                    <div class="text-muted small">
                        Last updated: ${data.time}
                    </div>
                `;
            })
            .catch(error => console.error('Error:', error));
    }

    // Create price info element
    function createPriceInfo() {
        const priceInfo = document.createElement('div');
        priceInfo.id = 'priceInfo';
        priceInfo.className = 'price-info card mt-3 p-3';
        selectedStockName.parentNode.appendChild(priceInfo);
        return priceInfo;
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
        currentSymbol = symbol;
        
        // Clear existing interval if any
        if (priceUpdateInterval) {
            clearInterval(priceUpdateInterval);
        }

        fetch(`/get_stock_data?symbol=${encodeURIComponent(symbol)}`)
            .then(response => response.json())
            .then(data => {
                candleSeries.setData(data);
                // Start updating prices
                updateLatestPrice();
                priceUpdateInterval = setInterval(updateLatestPrice, 60000); // Update every minute
            })
            .catch(error => console.error('Error:', error));
    }

    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchResults.contains(e.target) && e.target !== searchInput) {
            searchResults.classList.add('d-none');
        }
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (priceUpdateInterval) {
            clearInterval(priceUpdateInterval);
        }
    });
});
