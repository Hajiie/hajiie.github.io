import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import {
	createCNN,
	csvText,
	evaluateCNN,
	forwardCNN,
	lineDataset,
	queryGraph,
	sampleGradients,
	shortestGraphPath,
	trainEpoch,
} from "../src/labs/research/core.mjs";

const graph = JSON.parse(
	readFileSync(
		new URL("../src/labs/research/graph-data.json", import.meta.url),
	),
);

test("graph questions handle shared topics, shortest paths and disconnected nodes", () => {
	assert.equal(queryGraph(graph, "topics").rows.length, 3);
	assert.deepEqual(queryGraph(graph, "shared").rows, [
		["준호", "민지", "그래프 DB"],
	]);
	assert.equal(queryGraph(graph, "path").rows[0][1], 3);
	const disconnected = {
		...graph,
		edges: graph.edges.filter(
			(edge) => edge.source !== "sora" && edge.target !== "sora",
		),
	};
	assert.deepEqual(shortestGraphPath(disconnected, "minji", "sora"), []);
	assert.deepEqual(shortestGraphPath(graph, "missing", "sora"), []);
});

test("CNN backpropagation matches finite differences for every trainable parameter", () => {
	const model = createCNN();
	const sample = lineDataset(1, 11)[0];
	const analytic = sampleGradients(model, sample);
	const loss = () =>
		-Math.log(forwardCNN(model, sample.pixels).probabilities[sample.label]);
	const epsilon = 1e-6;
	for (const key of ["kernels", "biases", "dense", "outputBias"]) {
		for (let index = 0; index < model[key].length; index++) {
			const original = model[key][index];
			model[key][index] = original + epsilon;
			const plus = loss();
			model[key][index] = original - epsilon;
			const minus = loss();
			model[key][index] = original;
			assert.ok(
				Math.abs((plus - minus) / (2 * epsilon) - analytic[key][index]) < 1e-5,
				`${key}[${index}] gradient`,
			);
		}
	}
});

test("CNN updates convolution weights and generalizes to separately generated images", () => {
	const training = lineDataset(80, 11);
	const validation = lineDataset(40, 902);
	assert.notDeepEqual(training[0], validation[0]);
	const model = createCNN();
	const before = evaluateCNN(model, validation);
	const initialKernels = Array.from(model.kernels);
	for (let epoch = 1; epoch <= 40; epoch++)
		trainEpoch(model, training, 0.3, epoch);
	const after = evaluateCNN(model, validation);
	assert.notDeepEqual(Array.from(model.kernels), initialKernels);
	assert.ok(after.loss < before.loss * 0.25);
	assert.ok(after.accuracy >= 0.95);
	assert.equal(
		after.confusion.flat().reduce((sum, count) => sum + count, 0),
		40,
	);
});

test("CSV preserves Korean, quotes and multiline values while escaping formulas", () => {
	const csv = csvText(
		["이름", "값"],
		[
			["민지,준호", "=SUM(1,2)"],
			['한"글\n줄', 3],
		],
	);
	assert.ok(csv.startsWith('\uFEFF"이름","값"\r\n'));
	assert.ok(csv.includes('"민지,준호","\'=SUM(1,2)"'));
	assert.ok(csv.includes('"한""글\n줄","3"'));
});

test("download bundle digest and source files match the packaged manifest", () => {
	const bundle = JSON.parse(
		readFileSync(new URL("../src/labs/research/bundle.json", import.meta.url)),
	);
	const digest = (value) => createHash("sha256").update(value).digest("hex");
	assert.equal(digest(Buffer.from(bundle.base64, "base64")), bundle.sha256);
	for (const file of bundle.files) {
		if (file.name === "curriculum.md") {
			const article = readFileSync(
				new URL(
					"../src/content/posts/ResearchLab/ResearchLab.md",
					import.meta.url,
				),
				"utf8",
			);
			const curriculum = `${article.split("<!-- curriculum:start -->")[1].split("<!-- curriculum:end -->")[0].trim()}\n`;
			assert.equal(digest(curriculum), file.sha256);
			continue;
		}
		if (file.name.endsWith(".cypher") || file.name.endsWith(".ipynb")) continue;
		const path =
			file.name === "graph.json" ? "graph-data.json" : `files/${file.name}`;
		assert.equal(
			digest(
				readFileSync(new URL(`../src/labs/research/${path}`, import.meta.url)),
			),
			file.sha256,
			file.name,
		);
	}
});
