import {
	createCNN,
	csvText,
	evaluateCNN,
	forwardCNN,
	GRAPH_QUERIES,
	lineDataset,
	queryGraph,
	trainEpoch,
} from "./core.mjs";

function attachPlayground(root) {
	const { graph, archive } = JSON.parse(
		root.querySelector("[data-lab-payload]").textContent,
	);
	const view = (name) => root.querySelector(`[data-view="${name}"]`);
	const action = (name) => root.querySelector(`[data-action="${name}"]`);
	const input = (name) => root.querySelector(`[data-input="${name}"]`);
	const svgNamespace = "http://www.w3.org/2000/svg";
	const svgElement = (name, attributes, text) => {
		const element = document.createElementNS(svgNamespace, name);
		for (const [key, value] of Object.entries(attributes))
			element.setAttribute(key, String(value));
		if (text !== undefined) element.textContent = text;
		return element;
	};
	const save = (content, name, type) => {
		const url = URL.createObjectURL(new Blob([content], { type }));
		const anchor = document.createElement("a");
		anchor.href = url;
		anchor.download = name;
		anchor.click();
		setTimeout(() => URL.revokeObjectURL(url), 1000);
	};
	const showTable = (target, columns, rows) => {
		const table = document.createElement("table");
		const head = document.createElement("thead");
		const heading = document.createElement("tr");
		for (const column of columns) {
			const cell = document.createElement("th");
			cell.scope = "col";
			cell.textContent = column;
			heading.append(cell);
		}
		head.append(heading);
		const body = document.createElement("tbody");
		for (const row of rows) {
			const line = document.createElement("tr");
			for (const value of row) {
				const cell = document.createElement("td");
				cell.textContent = String(value);
				line.append(cell);
			}
			body.append(line);
		}
		table.append(head, body);
		target.replaceChildren(table);
	};
	let graphResult = null;
	function drawGraph(path = []) {
		const svg = view("graph");
		svg.replaceChildren();
		const definitions = svgElement("defs", {});
		const marker = svgElement("marker", {
			id: "research-lab-arrow",
			viewBox: "0 0 10 10",
			refX: 8,
			refY: 5,
			markerWidth: 5,
			markerHeight: 5,
			orient: "auto-start-reverse",
		});
		marker.append(
			svgElement("path", { d: "M 0 0 L 10 5 L 0 10 z", fill: "#929ab4" }),
		);
		definitions.append(marker);
		svg.append(definitions);
		const nodes = new Map(graph.nodes.map((node) => [node.id, node]));
		for (const edge of graph.edges) {
			const from = nodes.get(edge.source);
			const to = nodes.get(edge.target);
			const index = path.indexOf(from.id);
			const reverse = path.indexOf(to.id);
			const highlighted =
				(index >= 0 && path[index + 1] === to.id) ||
				(reverse >= 0 && path[reverse + 1] === from.id);
			const distance = Math.hypot(to.x - from.x, to.y - from.y);
			const dx = (to.x - from.x) / distance;
			const dy = (to.y - from.y) / distance;
			svg.append(
				svgElement("line", {
					x1: from.x + dx * 28,
					y1: from.y + dy * 28,
					x2: to.x - dx * 32,
					y2: to.y - dy * 32,
					stroke: highlighted ? "#d18b24" : "#929ab4",
					"stroke-width": highlighted ? 5 : 1.5,
					opacity: highlighted ? 1 : 0.6,
					"marker-end": "url(#research-lab-arrow)",
				}),
			);
			svg.append(
				svgElement(
					"text",
					{
						x: (from.x + to.x) / 2,
						y: (from.y + to.y) / 2 - 6,
						"text-anchor": "middle",
						"font-size": 9,
						fill: "#7f879f",
					},
					edge.type,
				),
			);
		}
		for (const node of graph.nodes) {
			const group = svgElement("g", {
				tabindex: 0,
				role: "button",
				"aria-label": `${node.name}, ${node.label}`,
				cursor: "pointer",
			});
			const color = {
				Researcher: "#6477db",
				Topic: "#d18b24",
				Paper: "#258d79",
			}[node.label];
			group.append(
				svgElement("circle", {
					cx: node.x,
					cy: node.y,
					r: path.includes(node.id) ? 27 : 22,
					fill: color,
					stroke: "#fff",
					"stroke-width": 2,
				}),
			);
			group.append(
				svgElement(
					"text",
					{
						x: node.x,
						y: node.y + 43,
						"text-anchor": "middle",
						"font-size": 15,
						fill: color,
						"font-weight": 650,
					},
					node.name,
				),
			);
			const select = () => {
				view("node-detail").textContent =
					`label: ${node.label} · id: ${node.id} · name: ${node.name}`;
			};
			group.addEventListener("click", select);
			group.addEventListener("keydown", (event) => {
				if (event.key === "Enter" || event.key === " ") {
					event.preventDefault();
					select();
				}
			});
			svg.append(group);
		}
	}
	const selectGraphQuery = () => {
		view("cypher").textContent =
			GRAPH_QUERIES[input("graph-query").value].cypher;
	};
	input("graph-query").addEventListener("change", selectGraphQuery);
	action("run-graph").addEventListener("click", () => {
		graphResult = queryGraph(graph, input("graph-query").value);
		showTable(view("graph-results"), graphResult.columns, graphResult.rows);
		drawGraph(graphResult.path);
		view("graph-status").textContent =
			`${graphResult.rows.length}행${graphResult.path.length ? " · 방향을 무시한 최단 경로" : ""}`;
		action("download-graph").disabled = false;
	});
	action("download-graph").addEventListener("click", () => {
		if (graphResult)
			save(
				csvText(graphResult.columns, graphResult.rows),
				"graph-results.csv",
				"text/csv;charset=utf-8",
			);
	});
	action("download-zip").addEventListener("click", () => {
		const bytes = Uint8Array.from(atob(archive.base64), (character) =>
			character.charCodeAt(0),
		);
		save(bytes, "research-lab.zip", "application/zip");
	});
	drawGraph();
	selectGraphQuery();

	const train = lineDataset(80, 11);
	const validation = lineDataset(40, 902);
	let model = createCNN(7);
	let sampleIndex = 0;
	let history = [];
	let busy = false;
	let cancelRequested = false;
	root.stopLab = () => {
		cancelRequested = true;
	};
	function drawPixels(canvas, values, side, signed = false) {
		const context = canvas.getContext("2d");
		const maximum = Math.max(0.01, ...values.map((value) => Math.abs(value)));
		const cell = canvas.width / side;
		for (let index = 0; index < values.length; index++) {
			const value = values[index];
			const scaled = Math.min(
				1,
				Math.abs(value) / (signed ? maximum : Math.max(1, maximum)),
			);
			context.fillStyle = signed
				? value >= 0
					? `rgb(${Math.round(240 - scaled * 160)},${Math.round(245 - scaled * 120)},240)`
					: `rgb(245,${Math.round(240 - scaled * 130)},${Math.round(230 - scaled * 180)})`
				: `rgb(${Math.round(scaled * 255)},${Math.round(scaled * 255)},${Math.round(scaled * 255)})`;
			context.fillRect(
				(index % side) * cell,
				Math.floor(index / side) * cell,
				cell,
				cell,
			);
		}
	}
	function drawChart() {
		const svg = view("loss-chart");
		svg.replaceChildren();
		const highest =
			Math.max(
				1,
				...history.flatMap((row) => [row.trainLoss, row.validationLoss]),
			) * 1.1;
		svg.append(
			svgElement("line", {
				x1: 40,
				y1: 185,
				x2: 380,
				y2: 185,
				stroke: "#929ab4",
			}),
		);
		svg.append(
			svgElement(
				"text",
				{ x: 9, y: 22, fill: "#929ab4", "font-size": 11 },
				highest.toFixed(1),
			),
		);
		svg.append(
			svgElement(
				"text",
				{ x: 9, y: 189, fill: "#929ab4", "font-size": 11 },
				"0",
			),
		);
		svg.append(
			svgElement(
				"text",
				{ x: 310, y: 210, fill: "#929ab4", "font-size": 11 },
				"epoch →",
			),
		);
		for (const [key, color] of [
			["trainLoss", "#6477db"],
			["validationLoss", "#d18b24"],
		]) {
			const points = history
				.map(
					(row, index) =>
						`${40 + (index / Math.max(1, history.length - 1)) * 340},${185 - (row[key] / highest) * 165}`,
				)
				.join(" ");
			svg.append(
				svgElement("polyline", {
					points,
					fill: "none",
					stroke: color,
					"stroke-width": 2.5,
				}),
			);
		}
	}
	function refreshCNN(epoch = history.length ? history.at(-1).epoch : 0) {
		const training = evaluateCNN(model, train);
		const testing = evaluateCNN(model, validation);
		view("train-loss").textContent = training.loss.toFixed(4);
		view("accuracy").textContent = `${(testing.accuracy * 100).toFixed(1)}%`;
		view("epoch").textContent = String(epoch);
		const sample = validation[sampleIndex];
		const forward = forwardCNN(model, sample.pixels);
		drawPixels(view("sample"), sample.pixels, 12);
		view("prediction").textContent =
			`검증 #${sampleIndex + 1} · 정답: ${sample.label === 0 ? "세로선" : "가로선"} · 세로 ${(forward.probabilities[0] * 100).toFixed(1)}% / 가로 ${(forward.probabilities[1] * 100).toFixed(1)}%`;
		for (let filter = 0; filter < model.filters; filter++)
			drawPixels(
				view(`kernel-${filter}`),
				Array.from(model.kernels.slice(filter * 9, filter * 9 + 9)),
				3,
				true,
			);
		drawPixels(
			view("feature-map"),
			Array.from(forward.activations.slice(0, 100)),
			10,
		);
		showTable(
			view("confusion"),
			["정답 / 예측", "세로선", "가로선"],
			[
				["세로선", ...testing.confusion[0]],
				["가로선", ...testing.confusion[1]],
			],
		);
		drawChart();
		return { training, testing };
	}
	function setBusy(value) {
		busy = value;
		for (const name of ["train", "reset", "next-sample"])
			action(name).disabled = value;
		for (const name of ["epochs", "learning-rate"])
			input(name).disabled = value;
		action("stop").disabled = !value;
		for (const name of ["download-metrics", "download-model"])
			action(name).disabled = value || history.length === 0;
	}
	action("train").addEventListener("click", async () => {
		if (busy) return;
		model = createCNN(7);
		history = [];
		const initial = refreshCNN(0);
		history = [
			{
				epoch: 0,
				trainLoss: initial.training.loss,
				validationLoss: initial.testing.loss,
				validationAccuracy: initial.testing.accuracy,
			},
		];
		cancelRequested = false;
		const epochs = Number(input("epochs").value);
		const rate = Number(input("learning-rate").value);
		view("progress").max = epochs;
		view("progress").value = 0;
		setBusy(true);
		try {
			for (let epoch = 1; epoch <= epochs; epoch++) {
				if (cancelRequested || !root.isConnected) break;
				trainEpoch(model, train, rate, epoch);
				const metrics = refreshCNN(epoch);
				history.push({
					epoch,
					trainLoss: metrics.training.loss,
					validationLoss: metrics.testing.loss,
					validationAccuracy: metrics.testing.accuracy,
				});
				view("progress").value = epoch;
				drawChart();
				view("training-status").textContent =
					`학습 ${epoch} / ${epochs} epoch · 검증 ${(metrics.testing.accuracy * 100).toFixed(1)}%`;
				await new Promise((resolve) => requestAnimationFrame(resolve));
			}
			view("training-status").textContent =
				`${cancelRequested ? "중단" : "완료"}: ${history.at(-1).epoch} epoch · 학습 80개 / 별도 검증 40개`;
		} catch (error) {
			view("training-status").textContent = `학습 오류: ${error.message}`;
		} finally {
			setBusy(false);
		}
	});
	action("stop").addEventListener("click", () => {
		cancelRequested = true;
	});
	action("reset").addEventListener("click", () => {
		if (busy) return;
		model = createCNN(7);
		history = [];
		view("progress").value = 0;
		view("training-status").textContent = "seed 7 · 초기 가중치 복원";
		refreshCNN(0);
		setBusy(false);
	});
	action("next-sample").addEventListener("click", () => {
		sampleIndex = (sampleIndex + 1) % validation.length;
		refreshCNN();
	});
	action("download-metrics").addEventListener("click", () =>
		save(
			csvText(
				["epoch", "train_loss", "validation_loss", "validation_accuracy"],
				history.map((row) => [
					row.epoch,
					row.trainLoss,
					row.validationLoss,
					row.validationAccuracy,
				]),
			),
			"browser-cnn-metrics.csv",
			"text/csv;charset=utf-8",
		),
	);
	action("download-model").addEventListener("click", () => {
		const weights = Object.fromEntries(
			["kernels", "biases", "dense", "outputBias"].map((key) => [
				key,
				Array.from(model[key]),
			]),
		);
		save(
			JSON.stringify(
				{
					dataset: "12x12 synthetic lines",
					seed: 7,
					trainSeed: 11,
					validationSeed: 902,
					architecture: "Conv3x3x4-ReLU-GlobalAverage-Linear2",
					history,
					metrics: evaluateCNN(model, validation),
					weights,
				},
				null,
				2,
			),
			"browser-line-cnn-results.json",
			"application/json",
		);
	});
	refreshCNN(0);
}

if (!customElements.get("research-playground")) {
	customElements.define(
		"research-playground",
		class extends HTMLElement {
			connectedCallback() {
				if (this.dataset.ready) return;
				this.dataset.ready = "true";
				attachPlayground(this);
			}
			disconnectedCallback() {
				this.stopLab?.();
			}
		},
	);
}
