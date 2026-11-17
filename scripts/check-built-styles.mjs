import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { resolve } from "node:path";

// Verify the generated page's styles, so a missing layout import fails the build.
const output = resolve(process.argv[2] || "dist");
const html = await readFile(resolve(output, "index.html"), "utf8");
const styles = [...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/g)].map(
	(match) => match[1],
);
for (const [link] of html.matchAll(/<link\b[^>]*>/g)) {
	if (!/rel=["']stylesheet["']/.test(link)) continue;
	const href = link.match(/href=["']([^"']+)["']/)?.[1];
	if (!href || /^(?:https?:)?\/\//.test(href)) continue;
	const pathname = decodeURIComponent(
		new URL(href, "https://preview.invalid/").pathname,
	);
	styles.push(await readFile(resolve(output, `.${pathname}`), "utf8"));
}
const css = styles.join("\n");
for (const variable of ["radius-large", "page-bg", "card-bg", "btn-content"]) {
	assert.ok(
		new RegExp(`--${variable}\\s*:\\s*[^;}]+`).test(css),
		`Built page is missing --${variable}`,
	);
}
for (const selector of ["card-base", "float-panel-closed", "btn-regular"]) {
	assert.ok(
		new RegExp(`\\.${selector}\\s*\\{[^}]+\\}`).test(css),
		`Built page is missing .${selector}`,
	);
}
assert.ok(
	/@keyframes\s+fade-in-up\s*\{/.test(css),
	"Built page is missing entrance animations",
);
console.log("Built theme styles verified.");
