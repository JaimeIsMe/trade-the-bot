import React, { useMemo } from 'react';
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { BarChart3 } from 'lucide-react';

const PriceChart = ({ candles, symbol }) => {
  const chartData = useMemo(() => {
    if (!candles || candles.length === 0) return [];

    return candles.map((candle) => {
      const date = new Date(candle.time);
      const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      return {
        time: timeStr,
        fullTime: date.toLocaleString(),
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
        volume: candle.volume,
        // For candlestick body (between open and close)
        candleBody: candle.close >= candle.open 
          ? [candle.open, candle.close]  // Green candle (bullish)
          : [candle.close, candle.open],  // Red candle (bearish)
        isGreen: candle.close >= candle.open,
        // For wicks (high/low)
        highWick: candle.high,
        lowWick: candle.low
      };
    });
  }, [candles]);

  // Sample every nth candle for x-axis labels (to avoid crowding)
  const sampledData = useMemo(() => {
    if (chartData.length <= 20) return chartData;
    const step = Math.floor(chartData.length / 12);  // Show ~12 labels
    return chartData.map((d, i) => ({
      ...d,
      time: i % step === 0 ? d.time : ''
    }));
  }, [chartData]);

  const CustomCandlestick = (props) => {
    const { x, y, width, height, payload } = props;
    
    if (!payload) return null;
    
    const { open, high, low, close, isGreen } = payload;
    const color = isGreen ? '#10b981' : '#ef4444';  // green / red
    
    // Calculate positions
    const candleHeight = Math.abs(y - (y + height));
    const wickX = x + width / 2;
    const highY = y - ((high - close) / (high - low)) * candleHeight;
    const lowY = y + ((close - low) / (high - low)) * candleHeight;
    
    return (
      <g>
        {/* High wick */}
        <line
          x1={wickX}
          y1={highY}
          x2={wickX}
          y2={y}
          stroke={color}
          strokeWidth={1}
        />
        {/* Candle body */}
        <rect
          x={x}
          y={y}
          width={width}
          height={height}
          fill={color}
          opacity={0.8}
        />
        {/* Low wick */}
        <line
          x1={wickX}
          y1={y + height}
          x2={wickX}
          y2={lowY}
          stroke={color}
          strokeWidth={1}
        />
      </g>
    );
  };

  const latestCandle = chartData[chartData.length - 1];
  const priceChange = latestCandle 
    ? ((latestCandle.close - chartData[0].open) / chartData[0].open * 100).toFixed(2)
    : 0;

  // Calculate dynamic Y-axis range (±20% of price range for better visibility)
  const priceRange = useMemo(() => {
    if (chartData.length === 0) return { min: 0, max: 100 };
    
    const prices = chartData.flatMap(c => [c.high, c.low]);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const range = maxPrice - minPrice;
    const center = (minPrice + maxPrice) / 2;
    
    // Add 20% padding around the actual range
    const padding = range * 0.2;
    
    return {
      min: minPrice - padding,
      max: maxPrice + padding
    };
  }, [chartData]);

  return (
    <div className="bg-[#1a1a1a] rounded-2xl p-5 border border-gray-800/50">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-purple-500/10 to-purple-600/10">
            <BarChart3 className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">{symbol}</h2>
            <p className="text-xs text-gray-500">24 hours • 5-minute candles</p>
          </div>
        </div>
        
        {latestCandle && (
          <div className="text-right">
            <div className="text-2xl font-bold text-white tracking-tight">
              ${latestCandle.close.toFixed(2)}
            </div>
            <div className="flex items-center justify-end space-x-1 text-sm mt-0.5">
              <span className={parseFloat(priceChange) >= 0 ? 'text-green-400' : 'text-red-400'}>
                {parseFloat(priceChange) >= 0 ? '↑' : '↓'}
              </span>
              <span className={parseFloat(priceChange) >= 0 ? 'text-green-400' : 'text-red-400'}>
                {parseFloat(priceChange) >= 0 ? '+' : ''}{priceChange}%
              </span>
            </div>
          </div>
        )}
      </div>

      {chartData.length === 0 ? (
        <div className="text-center text-gray-500 py-24">
          Loading chart data...
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={sampledData}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
              </linearGradient>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
            
            <XAxis 
              dataKey="time" 
              stroke="#64748b"
              style={{ fontSize: '10px' }}
              interval="preserveStartEnd"
            />
            
            <YAxis 
              yAxisId="price"
              domain={[priceRange.min, priceRange.max]}
              stroke="#64748b"
              style={{ fontSize: '12px' }}
              tickFormatter={(value) => `$${value.toFixed(2)}`}
            />
            
            <Tooltip
              contentStyle={{
                backgroundColor: '#1e293b',
                border: '1px solid #8b5cf6',
                borderRadius: '8px',
                color: '#f1f5f9',
                fontSize: '12px'
              }}
              content={({ active, payload }) => {
                if (active && payload && payload[0]) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-slate-800 border border-purple-500/30 rounded-lg p-3">
                      <div className="text-xs text-gray-400 mb-2">{data.fullTime}</div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-400">Open:</span>
                          <span className="text-white ml-2">${data.open.toFixed(2)}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Close:</span>
                          <span className={data.isGreen ? 'text-green-400 ml-2' : 'text-red-400 ml-2'}>
                            ${data.close.toFixed(2)}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-400">High:</span>
                          <span className="text-white ml-2">${data.high.toFixed(2)}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Low:</span>
                          <span className="text-white ml-2">${data.low.toFixed(2)}</span>
                        </div>
                      </div>
                      <div className="mt-2 pt-2 border-t border-gray-700">
                        <span className="text-gray-400 text-xs">Volume:</span>
                        <span className="text-white ml-2 text-xs">{data.volume.toFixed(0)}</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />
            
            {/* Candlestick bars */}
            <Bar 
              yAxisId="price"
              dataKey="candleBody" 
              fill="#8b5cf6"
              maxBarSize={10}
            >
              {sampledData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.isGreen ? '#10b981' : '#ef4444'} />
              ))}
            </Bar>

            {/* Price line (connects closes) */}
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="close"
              stroke="#8b5cf6"
              strokeWidth={1}
              dot={false}
              opacity={0.5}
            />
          </ComposedChart>
        </ResponsiveContainer>
      )}
      
      <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
        <div>
          Last 24 hours • {chartData.length} candles (5-min) • Updated every 10 minutes
        </div>
        <div className="flex space-x-4">
          <span className="flex items-center">
            <span className="w-3 h-3 bg-green-500 rounded-sm mr-1"></span>
            Bullish
          </span>
          <span className="flex items-center">
            <span className="w-3 h-3 bg-red-500 rounded-sm mr-1"></span>
            Bearish
          </span>
        </div>
      </div>
    </div>
  );
};

export default PriceChart;

