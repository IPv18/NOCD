class LineChart {
	constructor(ctx){
		this.MaxElementsDisplayed = 10 - 1;
		this.atEnd = true; 
		this.atStart = true;
		this.json;
		this.TotalLen = 0;
		this.old = 0;
		this.ctx = ctx;	
		this.time = 10;

		this.gradient = this.ctx.createLinearGradient(0, 0, 0, 400);
		this.gradient.addColorStop(0, 'rgba(58, 123, 231, 1)');
		this.gradient.addColorStop(1, 'rgba(0, 210, 255, 0.3)');

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
			datasets: [
				
			]
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
					min: -1,
					max: this.MaxElementsDisplayed,
				  },
				  y: {
					display: true,
					title: {
					  display: false,
					  text: "Value"
					},
					beginAtZero: true
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

		this.LastMin = this.myChart.config.options.scales.x.min;
    	this.LastMax = this.myChart.config.options.scales.x.max;

		this.rightWheelEvent = new WheelEvent('wheel', {
			deltaY: 1,
			deltaMode: 1
		});
		
		this.leftWheelEvent = new WheelEvent('wheel', {
			deltaY: -1,
			deltaMode: 1
		});

		this.speed = 1;

		// this.myChart.canvas.addEventListener('wheel', (w) => {
		// 	scroller(w);
		// });

		const toStart = document.getElementById('toStart');
			toStart.addEventListener("click", (c) => {
			// console.log(c);
			this.myChart.config.options.scales.x.min = 0;
			this.myChart.config.options.scales.x.max = this.MaxElementsDisplayed;

			this.atEnd = false; 
			this.atStart = true;

			this.LastMin = this.myChart.config.options.scales.x.min;
			this.LastMax = this.myChart.config.options.scales.x.max;
		});

		const toEnd = document.getElementById('toEnd');
			toEnd.addEventListener("click", (c) => {
			console.log(c);
			this.myChart.config.options.scales.x.min = this.myChart.data.labels.length - this.MaxElementsDisplayed - 1;
			this.myChart.config.options.scales.x.max = this.myChart.data.labels.length;

			this.atEnd = true; 
			this.atStart = false;
		});

		const jumpBackward = document.getElementById('jumpBackward');
			jumpBackward.addEventListener("click", (c) => {
			// console.log(c);
			if(this.atEnd){
				this.LastMin = this.myChart.config.options.scales.x.min;
				this.LastMax = this.myChart.config.options.scales.x.max;
			}
			this.myChart.config.options.scales.x.min = Math.max(this.LastMin - this.MaxElementsDisplayed, -1);
			this.LastMin = Math.max(this.LastMin - this.MaxElementsDisplayed, -1);

			this.myChart.config.options.scales.x.max = Math.max(this.LastMax - this.MaxElementsDisplayed, this.MaxElementsDisplayed);
			this.LastMax =  Math.max(this.LastMax - this.MaxElementsDisplayed, this.MaxElementsDisplayed);

			this.atEnd = false; 
		});

		let Len = null;

		const jumpForward = document.getElementById('jumpForward');
		jumpForward.addEventListener("click", (c) => {
		  // console.log(c);
		  if(!this.atEnd){
			Len = this.myChart.data.labels.length;
			this.myChart.config.options.scales.x.min = Math.min(this.LastMin + this.MaxElementsDisplayed + 1, Len - this.MaxElementsDisplayed - 1);
			this.LastMin = Math.min(this.LastMin + this.MaxElementsDisplayed, Len - this.MaxElementsDisplayed - 1);
	
			this.myChart.config.options.scales.x.max = Math.min(this.LastMax + this.MaxElementsDisplayed + 1, Len);
			this.LastMax = Math.min(this.LastMax + this.MaxElementsDisplayed, Len);
		  }
		  if (this.LastMax == Len)
		  	this.atEnd = true; 
		});

		this.fetchData();

	}

	scroller(wheel){
		// console.log(wheel);
		if(wheel.deltaY > 0){
			if(this.myChart.config.options.scales.x.max >= this.myChart.data.labels.length - 1){
				this.myChart.config.options.scales.x.min = this.myChart.data.labels.length - this.MaxElementsDisplayed - 1;
				this.myChart.config.options.scales.x.max = this.myChart.data.labels.length;

				this.atEnd = true;
				this.atStart = false;
			}
			else{
				this.myChart.config.options.scales.x.min += 1 * this.speed;
				this.myChart.config.options.scales.x.max += 1 * this.speed;

				this.atEnd = false;
			}
		}
		else if (wheel.deltaY < 0){
			if(this.myChart.config.options.scales.x.min <= 0){
				this.myChart.config.options.scales.x.min = 0;
				this.myChart.config.options.scales.x.max = this.MaxElementsDisplayed;
			
				this.atEnd = false;
				this.atStart = true;
			}
			else{
				this.myChart.config.options.scales.x.min -= 1 * this.speed;
				this.myChart.config.options.scales.x.max -= 1 * this.speed;

				this.atEnd = false;
			}
		}
		else{
			// nothing yet !!
		}
	}

	getTime(){
		const date = new Date();
		const currentTimeString = date.toLocaleTimeString();
		return `${currentTimeString}`;
	}

	updateMainLable(label){
		if (this.myChart.data.labels.length % 5 !== 0){
			label = "";
		}

		this.myChart.data.labels.push(label);
	}

	addData(metrics) {

		if (this.myChart.data.datasets.length == 0){
			for (let [key, value] of Object.entries(metrics)) {
				this.addDataSet(key);
			}
		}
		else {
			let flag = 0;
			for (let [key, value] of Object.entries(metrics)) {
				this.myChart.data.datasets.forEach((dataset) => {
					if (dataset.label == key){
						flag = 1;
					}
				});
				if (flag == 0){
					this.addDataSet(key);	
				}
				flag = 0;
			}
		}

		setTimeout(function () { }, 1000);

		let flag = 0;
		this.myChart.data.datasets.forEach((dataset) => {
			for (let [key, value] of Object.entries(metrics)) {
				if (dataset.label == key){
					dataset.data.push(value);
					flag = 1;
					break;
				}
			}
			if (!flag){
				dataset.data.push(0);
			}

			flag = 0;
		});

		if(this.atEnd)
        	this.scroller(this.rightWheelEvent);
		
		this.myChart.update();
		this.TotalLen += 1;
	}

	addDataSet(processName){
		let dataset = {
			label: processName,
			data: new Array(this.TotalLen).fill(0),
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
		};

		this.myChart.data.datasets.push(dataset);
	}
	
	removeData() {
		this.myChart.data.labels.pop();
		this.myChart.data.datasets.forEach((dataset) => {
			dataset.data.pop();
		});
		// scroller(this.leftWheelEvent);
		this.myChart.update();
	}  

	debug(repeat=1){
		let i = 0;
		setInterval(() => {
			this.updateMainLable(this.getTime());

			let Rand = Math.random() * 1000 + 1;
			this.addData({'test' : Rand, 'test2' : Rand + 100});

		}, repeat * 1000);
	}

	fetchData() {
		
		let metrics = {};

		var xhr = new XMLHttpRequest();
		xhr.open('GET', 'traffic_control/interface_metrics/?interface=wlp0s20f3');
		xhr.setRequestHeader('Cache-Control', 'no-cache');
		xhr.send();
  
		var old = 0;
		xhr.onprogress = () => { 
			length = xhr.responseText.length;
			var n = length - old;
			old = xhr.responseText.length;
	
			// setTimeout(function () { }, 1000);
	
			this.json = JSON.parse(xhr.responseText.slice(-n));
			this.json.forEach((L) => {
				if (L['program'] != ""){
					metrics[L['program']] = Number(L['pkt_count']);
				}
			});
			
			if(Object.keys(metrics).length != 0){
				this.updateMainLable(this.getTime());
				this.addData(metrics);
			}
			metrics = {};
	
			// setTimeout(function() {}, 1000);
		};
	}
}
