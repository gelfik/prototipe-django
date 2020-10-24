function decodeHTMLEntities(text) {
    var entities = [
        ['amp', '&'],
        ['\r\n', ' '],
        ['apos', '\"'],
        ['#x27', '\"'],
        ['#x2F', '/'],
        ['#39', '\"'],
        ['#47', '/'],
        ['lt', '<'],
        ['gt', '>'],
        ['nbsp', ' '],
        ['quot', '"']
    ];

    for (var i = 0, max = entities.length; i < max; ++i)
        text = text.replace(new RegExp('&' + entities[i][0] + ';', 'g'), entities[i][1]);

    return text;
}

function generBlock_stats(data_spisok) {
    data_spisok = JSON.parse(decodeHTMLEntities(data_spisok))
    let local_count = 0
    data_spisok.forEach(function (item, i, data_spisok) {
        local_count += 1
        if ((local_count / 3) === 0) {
            $('#statics').append('<div class="row align-items-center"></div>')
        }
        $('#statics').children(".row").last().append('<div class="col-4 align-self-center"><canvas id="marksChart_' + i + '" width="600" height="400"></canvas></div>')

        var radarChart = new Chart(document.getElementById("marksChart_" + i), {
            type: 'radar',
            data: {
                labels: ['A', 'B', 'C', 'POL', 'CHL'],
                datasets: [{
                    label: item['name'],
                    backgroundColor: "rgba(200,0,0,0.2)",
                    data: item['result']
                }]
            },
            options: {
                scale: {
                    display: true,
                    ticks: {
                        display: false,
                        beginAtZero: true,
                        max: 100,
                        min: 0,
                        stepSize: 1,
                        showLabelBackdrop: false,
                    },
                }
            }
        });
    });
}