#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, lstatSync, mkdirSync, readdirSync, readlinkSync, rmSync, symlinkSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const REPO_URL = "https://github.com/Lum1104/Understand-Anything.git";
const MINIMUM_SKILLS = ["understand", "understand-chat", "understand-dashboard", "understand-diff", "understand-explain", "understand-onboard"];
const PLATFORM_ROOTS = {
  codex: ".codex/understand-anything",
  opencode: ".opencode/understand-anything",
  gemini: ".gemini/understand-anything"
};

const args = parseArgs(process.argv.slice(2));
const platform = args.platform || "codex";
const installRoot = join(homedir(), PLATFORM_ROOTS[platform] || PLATFORM_ROOTS.codex);
const universalPluginRoot = join(homedir(), ".understand-anything-plugin");
const agentSkillRoot = join(homedir(), ".agents", "skills");
const plannedPluginRoot = join(installRoot, "understand-anything-plugin");
const checkOnly = Boolean(args.checkOnly || args.dryRun);
const actions = [];
const warnings = [];

if (!PLATFORM_ROOTS[platform]) {
  warnings.push(`未知のplatform '${platform}' です。Codex互換の配置 ${installRoot} を使います。`);
}

const existingPluginRoot = resolveExistingPluginRoot();
if (!existingPluginRoot && !checkOnly) {
  cloneOrUpdateInstallRoot();
}

const pluginRoot = resolveExistingPluginRoot() || (existsSync(plannedPluginRoot) ? plannedPluginRoot : "");

if (pluginRoot) {
  ensureUniversalPluginRoot(pluginRoot);
  ensureSkillLinks(pluginRoot);
} else {
  warnings.push("Understand-Anythingは未導入です。");
  actions.push(`${REPO_URL} を ${installRoot} へcloneする予定です。`);
}

printSummary({ platform, installRoot, pluginRoot, checkOnly, actions, warnings });

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i += 1) {
    const value = argv[i];
    if (value === "--platform") out.platform = argv[++i];
    else if (value === "--check-only") out.checkOnly = true;
    else if (value === "--dry-run") out.dryRun = true;
    else if (value === "--update") out.update = true;
    else if (value === "--force") out.force = true;
    else if (value === "--help" || value === "-h") {
      printHelp();
      process.exit(0);
    }
  }
  return out;
}

function printHelp() {
  console.log(`使い方:
  node scripts/ua-bootstrap.mjs [options]

Options:
  --platform codex|opencode|gemini
  --check-only       ファイルを変更せず、導入状態だけを表示する。
  --dry-run          --check-only と同じ。
  --update           既存checkoutがある場合に git pull --ff-only を実行する。
  --force            このscriptが管理する壊れた、または古いsymlinkを置き換える。

標準動作:
  未導入ならCodex互換skillとしてUnderstand-Anythingを導入し、
  ~/.agents/skills と ~/.understand-anything-plugin のlinkを作成します。
`);
}

function resolveExistingPluginRoot() {
  const candidates = [
    universalPluginRoot,
    plannedPluginRoot,
    join(homedir(), ".codex", "understand-anything", "understand-anything-plugin"),
    join(homedir(), ".opencode", "understand-anything", "understand-anything-plugin"),
    join(homedir(), ".gemini", "understand-anything", "understand-anything-plugin")
  ];

  return candidates.find((candidate) => existsSync(join(candidate, "skills", "understand", "SKILL.md"))) || "";
}

function cloneOrUpdateInstallRoot() {
  if (!existsSync(installRoot)) {
    execFileSync("git", ["clone", REPO_URL, installRoot], { stdio: "inherit" });
    actions.push(`${REPO_URL} を ${installRoot} へcloneしました。`);
    return;
  }

  if (args.update) {
    execFileSync("git", ["-C", installRoot, "pull", "--ff-only"], { stdio: "inherit" });
    actions.push(`${installRoot} を更新しました。`);
  } else {
    actions.push(`${installRoot} に既存checkoutがあります。`);
  }
}

function ensureUniversalPluginRoot(pluginRoot) {
  ensureLink(universalPluginRoot, pluginRoot, "共通plugin root");
}

function ensureSkillLinks(pluginRoot) {
  mkdirSync(agentSkillRoot, { recursive: true });
  const skillsDir = join(pluginRoot, "skills");
  const skills = existsSync(skillsDir)
    ? readdirSync(skillsDir, { withFileTypes: true }).filter((entry) => entry.isDirectory()).map((entry) => entry.name)
    : MINIMUM_SKILLS;

  for (const skill of skills) {
    const target = join(skillsDir, skill);
    if (existsSync(target)) ensureLink(join(agentSkillRoot, skill), target, `skill ${skill}`);
  }
}

function ensureLink(linkPath, targetPath, label) {
  if (existsSync(linkPath)) {
    if (isSymlinkTo(linkPath, targetPath)) {
      actions.push(`${label} は既にlink済みのためスキップしました。`);
      return;
    }

    if (!args.force) {
      warnings.push(`${label} が ${linkPath} に既に存在します。置き換える場合は --force を付けてください。`);
      return;
    }

    if (!checkOnly) rmSync(linkPath, { recursive: true, force: true });
    actions.push(`${linkPath} の ${label} を置き換えました。`);
  }

  if (checkOnly) {
    actions.push(`${linkPath} -> ${targetPath} をlinkする予定です。`);
    return;
  }

  symlinkSync(targetPath, linkPath, process.platform === "win32" ? "junction" : "dir");
  actions.push(`${linkPath} -> ${targetPath} をlinkしました。`);
}

function isSymlinkTo(linkPath, targetPath) {
  try {
    const stat = lstatSync(linkPath);
    if (!stat.isSymbolicLink()) return false;
    return readlinkSync(linkPath) === targetPath;
  } catch {
    return false;
  }
}

function printSummary(result) {
  console.log("Understand-Anything導入確認");
  console.log(`Platform: ${result.platform}`);
  console.log(`Install root: ${result.installRoot}`);
  console.log(`Plugin root: ${result.pluginRoot || "(未検出)"}`);
  console.log(`確認のみ: ${result.checkOnly}`);

  if (result.actions.length) {
    console.log("\n実行内容:");
    for (const action of result.actions) console.log(`- ${action}`);
  }

  if (result.warnings.length) {
    console.log("\n警告:");
    for (const warning of result.warnings) console.log(`- ${warning}`);
  }
}
