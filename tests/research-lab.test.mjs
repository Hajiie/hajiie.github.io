import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";

const bundle = JSON.parse(
	readFileSync(new URL("../src/labs/research/bundle.json", import.meta.url)),
);
const digest = (data) => createHash("sha256").update(data).digest("hex");

test("download archive digest matches the bytes served by the page", () => {
	const zip = Buffer.from(bundle.base64, "base64");
	assert.equal(zip.readUInt32LE(), 0x04034b50);
	assert.equal(digest(zip), bundle.sha256);
});

test("archive contains fourteen daily lesson folders with local instructions", () => {
	const names = new Set(bundle.files.map((file) => file.name));
	assert.equal(names.size, bundle.files.length);
	for (let day = 1; day <= 14; day++) {
		const folder = `day${String(day).padStart(2, "0")}`;
		for (const name of ["lab.py", "README.md", "requirements.txt"])
			assert.ok(names.has(`${folder}/${name}`));
		if (day !== 12) assert.ok(names.has(`${folder}/lab.ipynb`));
	}
	for (const name of [
		"compose.yaml",
		".env.example",
		"graph.json",
		"seed.cypher",
		"queries.cypher",
	])
		assert.ok(names.has(`day12/${name}`));
	assert.ok(!names.has("classical_lab.py") && !names.has("train_cnn.py"));
});

test("downloaded curriculum matches the article", () => {
	const article = readFileSync(
		new URL("../src/content/posts/ResearchLab/ResearchLab.md", import.meta.url),
		"utf8",
	);
	const curriculum = `${article.split("<!-- curriculum:start -->")[1].split("<!-- curriculum:end -->")[0].trim()}\n`;
	assert.equal(
		digest(curriculum),
		bundle.files.find((file) => file.name === "curriculum.md").sha256,
	);
});
