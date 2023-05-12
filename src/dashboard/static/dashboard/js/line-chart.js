class LineChart {
	constructor(ctx){
		this.MaxElementsDisplayed = 100 - 1;
		this.ctx = ctx;	
		this.time = 10;

		this.gradient = this.ctx.createLinearGradient(0, 0, 0, 400);
		this.gradient.addColorStop(0, 'rgba(58, 123, 231, 1)');
		this.gradient.addColorStop(1, 'rgba(0, 210, 255, 0.3)');

		this.rightWheelEvent = new WheelEvent('wheel', {
			deltaY: 1,
			deltaMode: 1
		});
		
		this.leftWheelEvent = new WheelEvent('wheel', {
			deltaY: -1,
			deltaMode: 1
		});

		this.momentAdapter = {
			date: date => moment(date),
			format: (date, format) => moment(date).format(format),
			add: (date, amount, unit) => moment(date).add(amount, unit),
			diff: (max, min, unit) => moment(max).diff(moment(min), unit),
			startOf: (date, unit, weekday) => moment(date).startOf(unit, weekday),
			endOf: (date, unit) => moment(date).endOf(unit)
		};
		

		this.data = {
			labels: [],
			datasets: [{
			label: 'value',
			data: [],
			backgroundColor: [
				'rgba(255, 26, 104, 0.2)',
				'rgba(54, 162, 235, 0.2)',
				'rgba(255, 206, 86, 0.2)',
				'rgba(75, 192, 192, 0.2)',
				'rgba(153, 102, 255, 0.2)',
				'rgba(255, 159, 64, 0.2)',
				'rgba(0, 0, 0, 0.2)'
			],
			borderColor: [
				'rgba(255, 26, 104, 1)',
				'rgba(54, 162, 235, 1)',
				'rgba(255, 206, 86, 1)',
				'rgba(75, 192, 192, 1)',
				'rgba(153, 102, 255, 1)',
				'rgba(255, 159, 64, 1)',
				'rgba(0, 0, 0, 1)'
			],
			borderWidth: 1,
			fill: true,
			backgroundColor: this.gradient,
			borderColor: '#000',
			radius: 0,
			pointHitRadius: 10,
			tension: 0.4,
			// cubicInterpolationMode: 'monotone'
			}]
		};

		this.config = {
			type: 'line',
			data: this.data,
			options: {
			interaction: {
				mode: 'point'
			},
			maintainAspectRatio: false,
			layout:{
				padding:{
				top: 10,
				bottom: 10
				}
			},
			scales: {
				x: {
					display: true,
					title: {
					  display: false,
					  text: "Time"
					},
					ticks: {
						maxTicksLimit: 100,
						autoSkip: true,
        				autoSkipPadding: 20
					},
					// min: -1,
					// max: this.MaxElementsDisplayed,
				  },
				  y: {
					display: true,
					title: {
					  display: false,
					  text: "Value"
					}
				  }
			},
			plugins: {
				legend: {
					display: false
				}
			},
			animation : true
			}
		};

		this.myChart = new Chart(
			this.ctx,
			this.config
		);		
	}



	getTime(){
		const date = new Date();
		const currentTimeString = date.toLocaleTimeString();
		return `${currentTimeString}`;
	}

	addData(label, data) {
		if (this.myChart.data.labels.length % 5 !== 0){
			label = "";
		}

		this.myChart.data.labels.push(label);
		this.myChart.data.datasets.forEach((dataset) => {
			dataset.data.push(data);
		});
		
		this.myChart.update();
	}
	
	debug(repeat=1){
		setInterval(() => {
			let Rand = Math.random() * 1000 + 1;
			this.addData(this.getTime(), Rand);
		}, repeat * 1000);
	}	
}
