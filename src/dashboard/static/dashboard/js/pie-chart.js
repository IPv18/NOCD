const data = {
	labels: ['TCP', 'UDP', 'ICMP', 'ARP', 'DHCP', 'HTTP', 'SSL/TLS'],
	datasets: [{
		label: 'Weekly Sales',
		data: [100, 12, 6, 100, 12, 3, 9],
		backgroundColor: [
		'rgba(255, 26, 104, 1)',
		'rgba(54, 162, 235, 1)',
		'rgba(255, 206, 86, 1)',
		'rgba(75, 192, 192, 1)',
		'rgba(153, 102, 255, 1)',
		'rgba(255, 159, 64, 1)',
		'rgba(0, 0, 0, 1)'
		],
		hoverOffset: 20,
		borderWidth: 2,
		borderColor: 'white',}
	]
};

const config = {
	type: 'pie',
	data: data,
	options: {
		responsive: true,
		maintainAspectRatio: true,
		aspectRatio: 1,
		cutout: 40,
		// cutoutPercentage: 40,
		circumference: 360,
		plugins: {
			legend: {
				display: true,
				position: 'top',
				align: 'center',
				labels: {
					boxWidth: 20,
					boxHeight: 20,
					padding: 10,
					usePointStyle: false,
					font: {
						size: 12,
						family: undefined,
						style: 'normal',
						lineHeight: 1.2
					},
					color: undefined,
					textAlign: 'left',
					generateLabels: undefined
				}
			},
			title: {
				display: true,
				text: 'Chart Title',
				font: {
					size: 20,
					family: undefined,
					style: 'normal',
					lineHeight: 1.2
				},
				color: undefined,
				padding: 10
			},
			tooltip: {
				enabled: true,
				backgroundColor: 'rgba(0,0,0,0.8)',
				titleFont: {
					size: 16,
					family: undefined,
					style: 'normal',
					lineHeight: 1.2
				},
				titleColor: '#aaa',
				titleAlign: 'left',
				bodyFont: {
					size: 12,
					family: undefined,
					style: 'normal',
					lineHeight: 1.2
				},
				bodyColor: '#fff',
				bodyAlign: 'left',
				footerFont: {
					size: 12,
					family: undefined,
					style: 'normal',
					lineHeight: 1.2
				},
				footerColor: '#fff',
				footerAlign: 'left',
				padding: 8,
				caretPadding: 2,
				caretSize: 5,
				cornerRadius: 6,
				displayColors: true,
				borderColor: 'rgba(0,0,0,0)',
				borderWidth: 0
			},
		}, 
		// animation: {
		// 	duration: 1000,
		// 	easing: 'easeOutQuart',
		// 	from: 1,
		// 	delay: 0,
		// 	loop: true
		// }
	}
};

function addDataPie(chart, label, data, color) {
	chart.data.labels.push(label);
	chart.data.datasets.forEach((dataset) => {
		dataset.data.push(data);
		dataset.backgroundColor.push(color);
	});
	chart.update();
}

function removeDataPie(chart, label) {
	const index = chart.data.labels.indexOf(label);
	if (index !== -1) {
		chart.data.labels.splice(index, 1);
		chart.data.datasets.forEach((dataset) => {
			dataset.data.splice(index, 1);
			dataset.backgroundColor.splice(index, 1);
		});
		chart.update();
	}
}

function updateDataPie(chart, label, data) {
	const index = chart.data.labels.indexOf(label);
	if (index !== -1) {
		chart.data.datasets.forEach((dataset) => {
			dataset.data[index] = data;
		});
		chart.update();
	}
}

function hideLabelPie(chart, label) {
	const index = chart.data.labels.indexOf(label);
	if (index !== -1) {
		var meta = chart.getDatasetMeta(0);
		meta.data[index].hidden = true;
		chart.update();
	}
}

function showLabelPie(chart, label) {
	const index = chart.data.labels.indexOf(label);
	if (index !== -1) {
		var meta = chart.getDatasetMeta(0);
		meta.data[index].hidden = false;
		chart.update();
	}
}

function handleLabelClickPie(event, chart) {
	const activeElements = chart.getElementsAtEventForMode(event, 'nearest', { intersect: true });
	if (activeElements.length > 0) {
		const clickedElement = activeElements[0];
		const clickedIndex = clickedElement.index;
		const clickedLabel = chart.data.labels[clickedIndex];
		console.log(`Clicked on label: ${clickedLabel}`);
		// Do something with the clicked label here
	}
}

function handleLegendClickPie(event, legendItem, legend) {
	const index = legendItem.index;
	const meta = chart.getDatasetMeta(0);
	const metaIndex = meta.data.findIndex(item => item._index === index);
	const dataset = chart.data.datasets[0];

	if (metaIndex !== -1) {
		dataset.hidden = !dataset.hidden;
		meta.data[metaIndex].hidden = !meta.data[metaIndex].hidden;
		chart.update();
	}
}


function createPieChart(ctx){
	const myChart = new Chart(
		ctx,
		config
	);

	return myChart;
}