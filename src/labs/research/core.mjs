export const GRAPH_QUERIES = {
	topics: {
		title: "연구자별 연구 주제",
		cypher:
			"MATCH (r:ResearchLab:Researcher {lab_id: $lab})\n      -[:WORKS_ON]->(t:ResearchLab:Topic {lab_id: $lab})\nRETURN r.name AS researcher, t.name AS topic\nORDER BY researcher",
	},
	shared: {
		title: "같은 주제를 연구하는 사람",
		cypher:
			"MATCH (a:ResearchLab:Researcher {lab_id: $lab})\n      -[:WORKS_ON]->(t:ResearchLab:Topic {lab_id: $lab})\n      <-[:WORKS_ON]-(b:ResearchLab:Researcher {lab_id: $lab})\nWHERE a.id < b.id\nRETURN a.name AS researcher_a, b.name AS researcher_b, t.name AS topic\nORDER BY researcher_a, researcher_b",
	},
	path: {
		title: "민지 → 소라 최단 경로",
		cypher:
			"MATCH (a:ResearchLab {lab_id: $lab, id: 'minji'}),\n      (b:ResearchLab {lab_id: $lab, id: 'sora'})\nMATCH p = shortestPath((a)-[*1..6]-(b))\nWHERE all(n IN nodes(p) WHERE n:ResearchLab AND n.lab_id = $lab)\nRETURN [n IN nodes(p) | n.name] AS path, length(p) AS hops",
	},
};

export function shortestGraphPath(graph, source, target) {
	const ids = new Set(graph.nodes.map((node) => node.id));
	if (!ids.has(source) || !ids.has(target)) return [];
	const queue = [[source]];
	const visited = new Set([source]);
	for (let head = 0; head < queue.length; head++) {
		const path = queue[head];
		const current = path.at(-1);
		if (current === target) return path;
		for (const edge of graph.edges) {
			const next =
				edge.source === current
					? edge.target
					: edge.target === current
						? edge.source
						: null;
			if (next && !visited.has(next)) {
				visited.add(next);
				queue.push([...path, next]);
			}
		}
	}
	return [];
}

export function queryGraph(graph, kind) {
	const nodes = new Map(graph.nodes.map((node) => [node.id, node]));
	if (kind === "path") {
		const path = shortestGraphPath(graph, "minji", "sora");
		return {
			columns: ["경로", "관계 수"],
			rows: path.length
				? [[path.map((id) => nodes.get(id).name).join(" → "), path.length - 1]]
				: [],
			path,
		};
	}
	const works = graph.edges.filter((edge) => edge.type === "WORKS_ON");
	if (kind === "topics") {
		return {
			columns: ["연구자", "연구 주제"],
			rows: works.map((edge) => [
				nodes.get(edge.source).name,
				nodes.get(edge.target).name,
			]),
			path: [],
		};
	}
	if (kind !== "shared") throw new Error("Unknown graph exercise");
	const rows = [];
	for (const first of works) {
		for (const second of works) {
			if (first.target === second.target && first.source < second.source)
				rows.push([
					nodes.get(first.source).name,
					nodes.get(second.source).name,
					nodes.get(first.target).name,
				]);
		}
	}
	return { columns: ["연구자 A", "연구자 B", "공통 주제"], rows, path: [] };
}

export function csvText(columns, rows) {
	const quote = (value) => {
		const text = String(value);
		const safe = /^[=+\-@\t\r]/.test(text) ? `'${text}` : text;
		return `"${safe.replaceAll('"', '""')}"`;
	};
	return `\uFEFF${[columns, ...rows].map((row) => row.map(quote).join(",")).join("\r\n")}\r\n`;
}

export function seededRandom(seed = 7) {
	let state = seed >>> 0;
	return () => {
		state = (Math.imul(1664525, state) + 1013904223) >>> 0;
		return state / 4294967296;
	};
}

export function lineDataset(count, seed, side = 12) {
	const random = seededRandom(seed);
	return Array.from({ length: count }, (_, index) => {
		const label = index % 2;
		const pixels = Array.from({ length: side * side }, () => random() * 0.12);
		const offset = 3 + Math.floor(random() * (side - 6));
		for (let position = 2; position < side - 2; position++) {
			for (let thickness = 0; thickness < 2; thickness++) {
				const x = label === 0 ? offset + thickness : position;
				const y = label === 0 ? position : offset + thickness;
				pixels[y * side + x] = 0.85 + random() * 0.15;
			}
		}
		return { pixels, label };
	});
}

export function createCNN(seed = 7) {
	const random = seededRandom(seed);
	const uniform = (length, scale) =>
		Float64Array.from({ length }, () => (random() - 0.5) * scale);
	return {
		side: 12,
		filters: 4,
		kernels: uniform(36, 1.1),
		biases: new Float64Array(4),
		dense: uniform(8, 0.8),
		outputBias: new Float64Array(2),
	};
}

export function forwardCNN(model, pixels) {
	const width = model.side - 2;
	const area = width * width;
	const activations = new Float64Array(model.filters * area);
	const features = new Float64Array(model.filters);
	for (let filter = 0; filter < model.filters; filter++) {
		for (let y = 0; y < width; y++) {
			for (let x = 0; x < width; x++) {
				let sum = model.biases[filter];
				for (let ky = 0; ky < 3; ky++) {
					for (let kx = 0; kx < 3; kx++)
						sum +=
							model.kernels[filter * 9 + ky * 3 + kx] *
							pixels[(y + ky) * model.side + x + kx];
				}
				const activation = Math.max(0, sum);
				activations[filter * area + y * width + x] = activation;
				features[filter] += activation / area;
			}
		}
	}
	const logits = Float64Array.from({ length: 2 }, (_, output) => {
		let value = model.outputBias[output];
		for (let filter = 0; filter < model.filters; filter++)
			value += model.dense[output * model.filters + filter] * features[filter];
		return value;
	});
	const maximum = Math.max(...logits);
	const exponentials = Array.from(logits, (value) => Math.exp(value - maximum));
	const total = exponentials.reduce((sum, value) => sum + value, 0);
	return {
		probabilities: exponentials.map((value) => value / total),
		features,
		activations,
	};
}

export function sampleGradients(model, sample) {
	const forward = forwardCNN(model, sample.pixels);
	const outputGradient = forward.probabilities.map(
		(value, index) => value - Number(index === sample.label),
	);
	const gradients = {
		kernels: new Float64Array(model.kernels.length),
		biases: new Float64Array(model.filters),
		dense: new Float64Array(model.dense.length),
		outputBias: Float64Array.from(outputGradient),
	};
	const width = model.side - 2;
	const area = width * width;
	for (let filter = 0; filter < model.filters; filter++) {
		let featureGradient = 0;
		for (let output = 0; output < 2; output++) {
			gradients.dense[output * model.filters + filter] =
				outputGradient[output] * forward.features[filter];
			featureGradient +=
				model.dense[output * model.filters + filter] * outputGradient[output];
		}
		for (let y = 0; y < width; y++) {
			for (let x = 0; x < width; x++) {
				if (forward.activations[filter * area + y * width + x] <= 0) continue;
				const delta = featureGradient / area;
				gradients.biases[filter] += delta;
				for (let ky = 0; ky < 3; ky++) {
					for (let kx = 0; kx < 3; kx++)
						gradients.kernels[filter * 9 + ky * 3 + kx] +=
							delta * sample.pixels[(y + ky) * model.side + x + kx];
				}
			}
		}
	}
	return gradients;
}

export function trainEpoch(model, samples, learningRate, epoch) {
	const random = seededRandom(epoch + 101);
	const order = samples.map((_, index) => index);
	for (let index = order.length - 1; index > 0; index--) {
		const other = Math.floor(random() * (index + 1));
		[order[index], order[other]] = [order[other], order[index]];
	}
	for (let start = 0; start < order.length; start += 8) {
		const batch = order.slice(start, start + 8);
		const sums = {
			kernels: new Float64Array(model.kernels.length),
			biases: new Float64Array(model.filters),
			dense: new Float64Array(model.dense.length),
			outputBias: new Float64Array(2),
		};
		for (const index of batch) {
			const gradients = sampleGradients(model, samples[index]);
			for (const key of Object.keys(sums)) {
				for (let item = 0; item < sums[key].length; item++)
					sums[key][item] += gradients[key][item];
			}
		}
		for (const key of Object.keys(sums)) {
			for (let item = 0; item < sums[key].length; item++)
				model[key][item] -= (learningRate * sums[key][item]) / batch.length;
		}
	}
	return evaluateCNN(model, samples);
}

export function evaluateCNN(model, samples) {
	let loss = 0;
	let correct = 0;
	const confusion = [
		[0, 0],
		[0, 0],
	];
	for (const sample of samples) {
		const { probabilities } = forwardCNN(model, sample.pixels);
		const predicted = Number(probabilities[1] > probabilities[0]);
		loss -= Math.log(Math.max(1e-12, probabilities[sample.label]));
		correct += Number(predicted === sample.label);
		confusion[sample.label][predicted]++;
	}
	return {
		loss: loss / samples.length,
		accuracy: correct / samples.length,
		confusion,
	};
}
