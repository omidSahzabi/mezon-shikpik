import { readdirSync, readFileSync } from "node:fs";
import ts from "typescript";

const root = new URL("../src/components/app/", import.meta.url);
const showcase = new URL("../src/app/review-ui/app-components-showcase.tsx", import.meta.url);
const names = readdirSync(root, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();
const failures = [];

const source = ts.createSourceFile(showcase.pathname, readFileSync(showcase, "utf8"), ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const registrations = new Set();
const productionImports = new Set();

for (const statement of source.statements) {
  if (ts.isVariableStatement(statement)) {
    for (const declaration of statement.declarationList.declarations) {
      if (declaration.name.getText(source) !== "appPreviews" || !declaration.initializer || !ts.isObjectLiteralExpression(declaration.initializer)) continue;
      for (const property of declaration.initializer.properties) {
        if (!ts.isPropertyAssignment(property) || !ts.isIdentifier(property.name)) {
          failures.push("appPreviews entries must use explicit component names.");
          continue;
        }
        if (registrations.has(property.name.text)) failures.push(`Duplicate preview: ${property.name.text}`);
        registrations.add(property.name.text);
      }
    }
  }
  if (ts.isImportDeclaration(statement) && ts.isStringLiteral(statement.moduleSpecifier)) {
    const match = statement.moduleSpecifier.text.match(/^@\/components\/app\/(App[A-Z]\w*)\/\1$/);
    const bindings = statement.importClause?.namedBindings;
    if (match && bindings && ts.isNamedImports(bindings)
      && bindings.elements.some((element) => !element.isTypeOnly && element.name.text === match[1] && !element.propertyName)) {
      productionImports.add(match[1]);
    }
  }
}

if (names.length === 0) failures.push("No App Component folders found.");

for (const name of names) {
  if (!/^App[A-Z]\w*$/.test(name)) failures.push(`Invalid component folder: ${name}`);
  const folder = new URL(`${name}/`, root);
  const files = readdirSync(folder, { withFileTypes: true });
  const expected = [`${name}.md`, `${name}.styles.ts`, `${name}.tsx`].sort();
  if (files.some((file) => !file.isFile()) || files.map((file) => file.name).sort().join() !== expected.join()) {
    failures.push(`${name} must contain exactly ${expected.join(", ")}.`);
  } else if (!readFileSync(new URL(`${name}.md`, folder), "utf8").trim()) {
    failures.push(`${name} documentation is empty.`);
  }
  if (!registrations.has(name)) failures.push(`${name} is missing from appPreviews.`);
  if (!productionImports.has(name)) failures.push(`${name} must be imported directly from its production module.`);
}

for (const name of registrations) {
  if (!names.includes(name)) failures.push(`Unknown component in appPreviews: ${name}`);
}

if (failures.length) {
  console.error(failures.join("\n"));
  process.exitCode = 1;
} else {
  console.log(`Checked structure and playground registration for ${names.length} App Components.`);
}
