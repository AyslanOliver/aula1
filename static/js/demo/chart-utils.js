// Função para formatar números com separador de milhares
function number_format(number, decimals = 2, dec_point = ',', thousands_sep = '.') {
    // Garante que number seja um número
    number = (number + '').replace(',', '').replace(' ', '');
    var n = !isFinite(+number) ? 0 : +number,
        prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
        dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
        s = '',
        toFixedFix = function(n, prec) {
            var k = Math.pow(10, prec);
            return '' + Math.round(n * k) / k;
        };
    
    // Fix para IE parseFloat(0.55).toFixed(0) = 0;
    s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
    if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
        s[1] = s[1] || '';
        s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
}

// Configurações padrão para gráficos
const chartDefaults = {
    font: {
        family: 'Nunito, -apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif',
        color: '#858796'
    },
    colors: {
        primary: '#4e73df',
        success: '#1cc88a',
        info: '#36b9cc',
        warning: '#f6c23e',
        danger: '#e74a3b',
        secondary: '#858796',
        light: '#f8f9fc',
        dark: '#5a5c69'
    },
    tooltipDefaults: {
        backgroundColor: "rgb(255,255,255)",
        bodyColor: "#858796",
        titleColor: '#6e707e',
        titleFont: { size: 14 },
        borderColor: '#dddfeb',
        borderWidth: 1,
        padding: 15,
        displayColors: false,
        intersect: false,
        mode: 'index',
        caretPadding: 10
    }
};