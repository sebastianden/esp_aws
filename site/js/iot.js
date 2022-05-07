let range = null;
let response = null;
google.charts.load('current', { packages: ['corechart', 'line'] });
google.charts.setOnLoadCallback(sendRequest(24));
window.addEventListener('resize', function () { drawBasic(response) });

function sendRequest(hours) {
    if (range != hours) {
        let url = "<API_URL>iot-query-dynamodb-lambda";

        let xhr = new XMLHttpRequest();
        xhr.onload = function () {
            response = JSON.parse(xhr.response).data;
            console.log(response);
            drawBasic(response);
        };
        xhr.open("POST", url);
        xhr.setRequestHeader("Accept", "application/json");
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4) {
                console.log(xhr.status);
            }
        };

        let to = parseInt(Date.now() / 1000);
        let from = to - 3600 * hours;

        let data = `{
            "from": ${from},
            "to": ${to},
            "device": "nodemcu"
            }`;

        xhr.send(data);
    }
    range = hours;
}

function drawBasic(response) {
    let data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Time');
    data.addColumn('number', 'Temperature');
    data.addColumn('number', 'Humidity');

    document.getElementById("p1").innerHTML = "Humidity: " + response.humidity[response.humidity.length - 1] + " %";
    document.getElementById("p2").innerHTML = "Temperature: " + Math.round(response.temperature[response.temperature.length - 1]) + " °C";

    for (let i = 0; i < response.timestamp.length; i++) {
        data.addRow([new Date(response.timestamp[i] * 1000), response.temperature[i], response.humidity[i]]);
    }

    let options = {
        backgroundColor: '#232323',
        curveType: 'function',
        colors: ['red', 'blue'],
        width: window.innerWidth,
        height: .45 * window.innerWidth,
        textStyle: {
            color: '#909090'
        },
        legend: {
            textStyle: {
                color: '#909090'
            }
        },
        series: {
            0: { targetAxisIndex: 0 },
            1: { targetAxisIndex: 1 }
        },
        hAxis: {
            title: 'Time',
            titleColor: '#909090',
            color: '#909090',
            textStyle: {
                color: '#909090'
            }
        },
        vAxes: {
            0: {
                title: 'Temperature in °C',
                titleColor: '#909090',
                color: '#909090',
                gridlines: {
                multiple: 5,
                },
                viewWindow: {
                min: 10,
                max: 30
                },
                textStyle: {
                color: '#909090'
                }
            },
            1: {
                title: 'Humidity in %',
                titleColor: '#909090',
                color: '#909090',
                gridlines: {
                multiple: 25,
                },
                viewWindow: {
                min: 0,
                max: 100
                },
                textStyle: {
                color: '#909090'
                }
            }
        }
    };

    let chart = new google.visualization.AreaChart(document.getElementById('point'));
    chart.draw(data, options);

}