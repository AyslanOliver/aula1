// Importar configurações padrão
Chart.defaults.font.family = chartDefaults.font.family;
Chart.defaults.color = chartDefaults.font.color;

// Gráfico de Pizza - Despesas por Categoria
var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: expenses_data.categories || ["Sem dados"],
    datasets: [{
      data: expenses_data.values || [1],
      backgroundColor: [
        chartDefaults.colors.primary,
        chartDefaults.colors.success,
        chartDefaults.colors.info,
        chartDefaults.colors.warning,
        chartDefaults.colors.danger,
        chartDefaults.colors.secondary
      ],
      hoverBackgroundColor: [
        chartDefaults.colors.primary + "dd",
        chartDefaults.colors.success + "dd",
        chartDefaults.colors.info + "dd",
        chartDefaults.colors.warning + "dd",
        chartDefaults.colors.danger + "dd",
        chartDefaults.colors.secondary + "dd"
      ],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    plugins: {
      tooltip: {
        ...chartDefaults.tooltipDefaults,
        callbacks: {
          label: function(context) {
            var label = context.label || '';
            var value = context.parsed || 0;
            var total = context.dataset.data.reduce((a, b) => a + b, 0);
            var percentage = total > 0 ? Math.round((value / total) * 100) : 0;
            return label + ': R$ ' + number_format(value) + ' (' + percentage + '%)';
          }
        }
      },
      legend: {
        display: true,
        position: 'bottom',
        labels: {
          padding: 20,
          boxWidth: 12
        }
      }
    },
    cutout: '80%',
  },
});
