// Importar configurações padrão
Chart.defaults.font.family = chartDefaults.font.family;
Chart.defaults.color = chartDefaults.font.color;

// Gráfico de Área - Ganhos vs Despesas
var ctx = document.getElementById("myAreaChart");
var myAreaChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: ["Quinzena Anterior", "Quinzena Atual"],
    datasets: [
      {
        label: "Ganhos",
        lineTension: 0.3,
        backgroundColor: "rgba(78, 115, 223, 0.05)",
        borderColor: chartDefaults.colors.primary,
        pointRadius: 3,
        pointBackgroundColor: chartDefaults.colors.primary,
        pointBorderColor: chartDefaults.colors.primary,
        pointHoverRadius: 3,
        pointHoverBackgroundColor: chartDefaults.colors.primary,
        pointHoverBorderColor: chartDefaults.colors.primary,
        pointHitRadius: 10,
        pointBorderWidth: 2,
        data: [ganhos_data.anterior, ganhos_data.atual],
      },
      {
        label: "Despesas",
        lineTension: 0.3,
        backgroundColor: "rgba(231, 74, 59, 0.05)",
        borderColor: chartDefaults.colors.danger,
        pointRadius: 3,
        pointBackgroundColor: chartDefaults.colors.danger,
        pointBorderColor: chartDefaults.colors.danger,
        pointHoverRadius: 3,
        pointHoverBackgroundColor: chartDefaults.colors.danger,
        pointHoverBorderColor: chartDefaults.colors.danger,
        pointHitRadius: 10,
        pointBorderWidth: 2,
        data: [despesas_data.anterior, despesas_data.atual],
      }
    ],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      x: {
        grid: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 2
        }
      },
      y: {
        ticks: {
          maxTicksLimit: 5,
          padding: 10,
          callback: function(value) {
            return 'R$ ' + number_format(value);
          }
        },
        grid: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      },
    },
    plugins: {
      legend: {
        display: true,
        position: 'top'
      },
      tooltip: {
        ...chartDefaults.tooltipDefaults,
        callbacks: {
          label: function(context) {
            var datasetLabel = context.dataset.label || '';
            return datasetLabel + ': R$ ' + number_format(context.parsed.y);
          }
        }
      }
    }
  }
});
