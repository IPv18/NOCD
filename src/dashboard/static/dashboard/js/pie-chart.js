class PieChart {
	constructor(ctx, url){
		this.data = {
			labels: [],
			datasets: [{
				label: '# of pkts',
				data: [],
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
		
		this.config = {
			type: 'pie',
			data: this.data,
			options: {
				responsive: true,
				maintainAspectRatio: false,
				aspectRatio: 1,
				cutout: 40,
				// cutoutPercentage: 40,
				circumference: 360,
				plugins: {
					legend: {
						display: true,
						position: 'right',
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
						display: false,
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

		this.ctx = ctx;	
		this.url = url;
		this.myChart = new Chart(
			this.ctx,
			this.config
		);

		this.Fetcher(2);
	}

	Fetcher(repeat=1) {
		setInterval(() => {
			fetch(this.url)
			.then(response => response.json())
			.then(data => {
				Object.entries(data).forEach(([key, value]) => {
					this.updateData(key, value);
				});
			})
			.catch(error => {
				console.error('Error:', error);
			});
		}, repeat * 1000);
	}

	addData(label, data, color) {
		this.myChart.data.labels.push(label);
		this.myChart.data.datasets.forEach((dataset) => {
			dataset.data.push(data);
			dataset.backgroundColor.push(color);
		});
		this.myChart.update();
	}

	removeData(label) {
		const index = this.myChart.data.labels.indexOf(label);
		if (index !== -1) {
			this.myChart.data.labels.splice(index, 1);
			this.myChart.data.datasets.forEach((dataset) => {
				dataset.data.splice(index, 1);
				dataset.backgroundColor.splice(index, 1);
			});
			this.myChart.update();
		}
	}

	changeColor(label, color) {
		const index = this.myChart.data.labels.indexOf(label);
		if (index !== -1) {
			this.myChart.data.datasets[0].backgroundColor[index] = color;
			this.myChart.update();
		}
	}

	hideLabel(label) {
		const index = this.myChart.data.labels.indexOf(label);
		if (index !== -1) {
			var meta = this.myChart.getDatasetMeta(0);
			meta.data[index].hidden = true;
			this.myChart.update();
		}
	}

	showLabel(label) {
		const index = this.myChart.data.labels.indexOf(label);
		if (index !== -1) {
			var meta = this.myChart.getDatasetMeta(0);
			meta.data[index].hidden = false;
			this.myChart.update();
		}
	}

	handleLabelClick(event) {
		const activeElements = this.myChart.getElementsAtEventForMode(event, 'nearest', { intersect: true });
		if (activeElements.length > 0) {
			const clickedElement = activeElements[0];
			const clickedIndex = clickedElement.index;
			const clickedLabel = this.myChart.data.labels[clickedIndex];
			console.log(`Clicked on label: ${clickedLabel}`);
			// Do something with the clicked label here
			return clickedLabel;
		}
	}

	handleLegendClick(legendItem) {
		const index = legendItem.index;
		const meta = this.myChart.getDatasetMeta(0);
		const metaIndex = meta.data.findIndex(item => item._index === index);
		const dataset = this.myChart.data.datasets[0];

		if (metaIndex !== -1) {
			dataset.hidden = !dataset.hidden;
			meta.data[metaIndex].hidden = !meta.data[metaIndex].hidden;
			this.myChart.update();
		}
	}

	updateData(label, data, color='gray') {
		const index = this.myChart.data.labels.indexOf(label);
		if (index !== -1) {
			this.myChart.data.datasets.forEach((dataset) => {
				dataset.data[index] = data;
			});
			this.myChart.update();
		}
		else {
			this.addData(label, data, color);
		}
	}

	debug(repeat=1){
		setInterval(() => {
			let Rand = Math.random() * 100 + 1;
			this.updateData('Debug', Rand);
		}, repeat * 1000);
	}	
}
