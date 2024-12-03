import React from 'react';
import Chart from 'react-apexcharts';

const CandleChart = ({ data }) => {
  const options = {
    chart: { type: 'candlestick', height: 350 },
    xaxis: { type: 'datetime' },
    yaxis: { tooltip: { enabled: true } },
  };

  const series = [{ name: 'Price', data }];

  return <Chart options={options} series={series} type="candlestick" height={350} />;
};

export default CandleChart;
