// Importar configurações padrão
Chart.defaults.font.family = chartDefaults.font.family;
Chart.defaults.color = chartDefaults.font.color;

// Gráfico de Barras - Distribuição de Pacotes
var ctx = document.getElementById("myBarChart");
var myBarChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ["Pacotes Avulsos", "Pacotes Agendados", "Pacotes Expressos"],
    datasets: [{
      label: "Quantidade",
      backgroundColor: [
        chartDefaults.colors.primary,
        chartDefaults.colors.success,
        chartDefaults.colors.info
      ],
      hoverBackgroundColor: [
        chartDefaults.colors.primary + "dd",
        chartDefaults.colors.success + "dd",
        chartDefaults.colors.info + "dd"
      ],
      borderColor: "rgba(0,0,0,0.1)",
      borderWidth: 1,
      data: [
        packages_data.avulsos || 0,
        packages_data.agendados || 0,
        packages_data.expressos || 0
      ],
    }],
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
          maxTicksLimit: 6
        },
        maxBarThickness: 50,
      },
      y: {
        ticks: {
          min: 0,
          maxTicksLimit: 5,
          padding: 10,
          callback: function(value) {
            return number_format(value, 0);
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
        display: false
      },
      tooltip: {
        ...chartDefaults.tooltipDefaults,
        callbacks: {
          label: function(context) {
            var datasetLabel = context.dataset.label || '';
            return datasetLabel + ': ' + number_format(context.parsed.y, 0) + ' pacotes';
          }
        }
      }
    },
  }
});
