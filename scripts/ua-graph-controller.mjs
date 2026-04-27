#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const args = parseArgs(process.argv.slice(2));
const cwd = process.cwd();
const policyPath = args.policy || join(cwd, "config", "understand-anything-policy.json");
const policy = loadPolicy(policyPath);
const mode = args.mode || "manual";
const base = args.base || policy.baseBranch || "main";
const head = args.head || "HEAD";
const changedFiles = args.files ? readFilesArg(args.files) : getChangedFiles(base, head);
const classification = classify(changedFiles, policy);
const recommendation = recommend({ mode, changedFiles, classification, policy, forceFull: Boolean(args.full) });

const result = {
  generatedAt: new Date().toISOString(),
  mode,
  base,
  head,
  changedFileCount: changedFiles.length,
  changedFiles,
  classification,
  recommendation
};

printResult(result);

if (args.writeLog) {
  const logDir = join(cwd, ".agentops", "runs", "understand-anything");
  mkdirSync(logDir, { recursive: true });
  const stamp = result.generatedAt.replace(/[:.]/g, "-");
  const out = join(logDir, `${stamp}-${mode}.json`);
  writeFileSync(out, `${JSON.stringify(result, null, 2)}\n`);
  console.log(`\n実行ログを書き込みました: ${out}`);
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i += 1) {
    const value = argv[i];
    if (value === "--mode") out.mode = argv[++i];
    else if (value === "--base") out.base = argv[++i];
    else if (value === "--head") out.head = argv[++i];
    else if (value === "--policy") out.policy = argv[++i];
    else if (value === "--files") out.files = argv[++i];
    else if (value === "--full") out.full = true;
    else if (value === "--write-log") out.writeLog = true;
    else if (value === "--help" || value === "-h") {
      printHelp();
      process.exit(0);
    }
  }
  return out;
}

function printHelp() {
  console.log(`使い方:
  node scripts/ua-graph-controller.mjs [options]

Options:
  --mode pr|post-merge|manual|release|schedule
  --base <ref>          git diffの基準ref。標準はpolicyのbaseBranchまたはmain。
  --head <ref>          git diffの比較先ref。標準はHEAD。
  --files <csv>         comma区切りのfile list。git diffを使わない。
  --policy <path>       policy JSONのpath。
  --full                full更新を推奨する。
  --write-log           .agentops/runs/understand-anything/*.json に記録する。
`);
}

function loadPolicy(path) {
  if (!existsSync(path)) return {};
  return JSON.parse(readFileSync(path, "utf8"));
}

function readFilesArg(value) {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

function getChangedFiles(base, head) {
  const attempts = [
    ["diff", "--name-only", `${base}...${head}`],
    ["diff", "--name-only", `${base}..${head}`],
    ["diff", "--name-only"]
  ];

  for (const attempt of attempts) {
    try {
      const output = execFileSync("git", attempt, { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] });
      return output.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
    } catch {
      // 次のdiff方式を試す。
    }
  }

  return [];
}

function classify(files, policy) {
  const lightweight = files.filter((file) => matchesAny(file, policy.lightweightPatterns || []));
  const structural = files.filter((file) => matchesAny(file, policy.structuralPatterns || []));
  const domain = files.filter((file) => matchesAny(file, policy.domainPatterns || []));
  const toolVersion = files.filter((file) => matchesAny(file, policy.toolVersionPatterns || []));

  return {
    isEmpty: files.length === 0,
    isDocOnly: files.length > 0 && lightweight.length === files.length,
    lightweight,
    structural,
    domain,
    toolVersion,
    hasStructuralChange: structural.length > 0,
    hasDomainChange: domain.length > 0,
    hasToolVersionChange: toolVersion.length > 0
  };
}

function recommend({ mode, changedFiles, classification, policy, forceFull }) {
  const actions = [];
  const deferredActions = [];
  const reasons = [];
  const commandHints = [];
  const deferredCommandHints = [];
  const fullThreshold = Number(policy.fullRebuildFileThreshold || 50);

  if (forceFull) {
    actions.push("full");
    reasons.push("--full が指定されました。");
  } else if (classification.isEmpty) {
    actions.push("skip");
    reasons.push("変更ファイルが検出されませんでした。");
  } else if ((mode === "release" || mode === "schedule") && policy.fullRebuildOnRelease !== false) {
    actions.push("full");
    reasons.push(`${mode} modeでは新しいfull graphを優先します。`);
  } else if (changedFiles.length > fullThreshold) {
    actions.push("full");
    reasons.push(`変更ファイル数 ${changedFiles.length} が閾値 ${fullThreshold} を超えています。`);
  } else if (classification.hasToolVersionChange && mode !== "pr") {
    actions.push("full");
    reasons.push("ツールまたはgraph policyが変更されています。");
  } else if (classification.isDocOnly && !classification.hasDomainChange) {
    actions.push(policy.docOnlyAction || "skip");
    reasons.push("軽量なドキュメントのみの変更です。");
  } else if (mode === "pr") {
    actions.push(policy.prDefaultAction || "diff");
    reasons.push("PR中は重いgraph更新を避けます。");
    if (classification.hasDomainChange) {
      deferredActions.push("domain");
      reasons.push("domain-sensitiveなファイルが変更されています。merge後にdomain graph更新を検討してください。");
    }
    if (classification.hasStructuralChange) {
      deferredActions.push("incremental");
      reasons.push("構造に関わるファイルが変更されています。merge後にincremental更新を検討してください。");
    }
  } else {
    actions.push(policy.postMergeDefaultAction || "incremental");
    reasons.push("post-merge/manual modeではincremental更新が可能です。");
    if (classification.hasDomainChange) {
      actions.push("domain");
      reasons.push("domain-sensitiveなファイルが変更されています。");
    }
  }

  const uniqueActions = [...new Set(actions)];
  for (const action of uniqueActions) {
    if (action === "diff") commandHints.push("/understand-diff");
    if (action === "incremental") commandHints.push("/understand --auto-update");
    if (action === "domain") commandHints.push("/understand-domain");
    if (action === "full") commandHints.push("/understand --full");
  }

  const uniqueDeferredActions = [...new Set(deferredActions)];
  for (const action of uniqueDeferredActions) {
    if (action === "incremental") deferredCommandHints.push("/understand --auto-update");
    if (action === "domain") deferredCommandHints.push("/understand-domain");
    if (action === "full") deferredCommandHints.push("/understand --full");
  }

  return {
    actions: uniqueActions,
    deferredActions: uniqueDeferredActions,
    commandHints,
    deferredCommandHints,
    reasons
  };
}

function matchesAny(file, patterns) {
  return patterns.some((pattern) => globToRegExp(pattern).test(file));
}

function globToRegExp(pattern) {
  let source = "^";
  for (let i = 0; i < pattern.length; i += 1) {
    const char = pattern[i];
    const next = pattern[i + 1];
    const afterNext = pattern[i + 2];
    if (char === "*" && next === "*" && afterNext === "/") {
      source += "(?:.*/)?";
      i += 2;
    } else if (char === "*" && next === "*") {
      source += ".*";
      i += 1;
    } else if (char === "*") {
      source += "[^/]*";
    } else if (char === "?") {
      source += "[^/]";
    } else {
      source += escapeRegExp(char);
    }
  }
  source += "$";
  return new RegExp(source);
}

function escapeRegExp(value) {
  return value.replace(/[|\\{}()[\]^$+?.]/g, "\\$&");
}

function printResult(result) {
  console.log("Understand-Anything graph更新の推奨");
  console.log(`Mode: ${result.mode}`);
  console.log(`Base: ${result.base}`);
  console.log(`Head: ${result.head}`);
  console.log(`変更ファイル数: ${result.changedFileCount}`);

  if (result.changedFiles.length) {
    console.log("\n変更ファイル:");
    for (const file of result.changedFiles) console.log(`- ${file}`);
  }

  console.log("\n分類:");
  console.log(`- ドキュメントのみ: ${result.classification.isDocOnly}`);
  console.log(`- 構造変更: ${result.classification.structural.length}`);
  console.log(`- domain変更: ${result.classification.domain.length}`);
  console.log(`- tool/policy変更: ${result.classification.toolVersion.length}`);

  console.log("\n推奨action:");
  for (const action of result.recommendation.actions) console.log(`- ${action}`);

  if (result.recommendation.deferredActions.length) {
    console.log("\nmerge後に検討するaction:");
    for (const action of result.recommendation.deferredActions) console.log(`- ${action}`);
  }

  if (result.recommendation.commandHints.length) {
    console.log("\ncommand候補:");
    for (const command of result.recommendation.commandHints) console.log(`- ${command}`);
  }

  if (result.recommendation.deferredCommandHints.length) {
    console.log("\nmerge後のcommand候補:");
    for (const command of result.recommendation.deferredCommandHints) console.log(`- ${command}`);
  }

  console.log("\n理由:");
  for (const reason of result.recommendation.reasons) console.log(`- ${reason}`);
}
