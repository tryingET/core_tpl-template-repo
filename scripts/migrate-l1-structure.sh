#!/usr/bin/env bash
# migrate-l1-structure.sh - Migrate old <company>-templates/ structure to new <company>/ structure
#
# Usage:
#   ./scripts/migrate-l1-structure.sh <company_slug> [company_name]
#
# Example:
#   ./scripts/migrate-l1-structure.sh softwareco "Software Company"
#
# This script:
#   1. Creates new company structure from L0 template
#   2. Migrates git history from <company>-templates/
#   3. Moves owned/, contrib/, infra/, agents/ folders
#   4. Swaps old for new
#
# WARNING: Run this with a clean git state in both the old templates repo
#          and the company folder.

set -euo pipefail

company_slug="${1:-}"
company_name="${2:-${company_slug}}"

if [ -z "$company_slug" ]; then
  echo "usage: migrate-l1-structure.sh <company_slug> [company_name]" >&2
  echo "  example: ./scripts/migrate-l1-structure.sh softwareco 'Software Company'" >&2
  exit 2
fi

workspace_root="${AI_SOCIETY_WORKSPACE:-$HOME/ai-society}"
repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

old_templates_dir="$workspace_root/$company_slug/${company_slug}-templates"
old_company_dir="$workspace_root/$company_slug"
new_company_dir="$workspace_root/${company_slug}-new"

# Validate preconditions
echo "=== L1 Structure Migration: $company_slug ==="
echo ""

if [ ! -d "$old_templates_dir" ]; then
  echo "error: old templates dir not found: $old_templates_dir" >&2
  exit 2
fi

if [ ! -d "$old_templates_dir/.git" ]; then
  echo "error: old templates dir is not a git repo: $old_templates_dir" >&2
  exit 2
fi

# Check for uncommitted changes
cd "$old_templates_dir"
if ! git diff --quiet HEAD 2>/dev/null; then
  echo "error: uncommitted changes in $old_templates_dir - commit or stash first" >&2
  git status --short
  exit 2
fi
cd "$repo_root"

echo "Step 1: Generate new structure from L0..."
rm -rf "$new_company_dir"
./scripts/new-l1-from-copier.sh "$new_company_dir" \
  -d repo_slug="$company_slug" \
  -d company_slug="$company_slug" \
  -d company_name="$company_name" \
  --defaults --overwrite

echo "Step 2: Copy git history from old templates..."
rm -rf "$new_company_dir/.git"
cp -a "$old_templates_dir/.git" "$new_company_dir/.git"

echo "Step 3: Copy .copier-answers.yml..."
cp "$old_templates_dir/.copier-answers.yml" "$new_company_dir/.copier-answers.yml"

echo "Step 4: Migrate company-level AGENTS.md (if exists)..."
if [ -f "$old_company_dir/AGENTS.md" ]; then
  cp "$old_company_dir/AGENTS.md" "$new_company_dir/AGENTS.md"
  echo "  (preserved existing AGENTS.md)"
fi

echo "Step 5: Create L2 project folders..."
mkdir -p "$new_company_dir/owned"
mkdir -p "$new_company_dir/contrib"
mkdir -p "$new_company_dir/infra"
mkdir -p "$new_company_dir/agents"

echo "Step 6: Move L2 projects..."
# Move owned/
if [ -d "$old_company_dir/owned" ]; then
  mv "$old_company_dir/owned"/* "$new_company_dir/owned/" 2>/dev/null || true
  echo "  moved owned/"
fi

# Move contrib/
if [ -d "$old_company_dir/contrib" ]; then
  mv "$old_company_dir/contrib"/* "$new_company_dir/contrib/" 2>/dev/null || true
  echo "  moved contrib/"
fi

# Move infra/
if [ -d "$old_company_dir/infra" ]; then
  mv "$old_company_dir/infra"/* "$new_company_dir/infra/" 2>/dev/null || true
  echo "  moved infra/"
fi

# Move agents/
if [ -d "$old_company_dir/agents" ]; then
  mv "$old_company_dir/agents"/* "$new_company_dir/agents/" 2>/dev/null || true
  echo "  moved agents/"
fi

echo "Step 7: Remove tpl-owned-repo if present..."
rm -rf "$new_company_dir/copier/tpl-owned-repo"

echo "Step 8: Stage all changes in new repo..."
cd "$new_company_dir"
git add -A

echo ""
echo "=== Migration prepared ==="
echo ""
echo "New structure at: $new_company_dir"
echo ""
echo "To complete migration:"
echo "  1. cd $new_company_dir"
echo "  2. git status  # review changes"
echo "  3. git commit -m 'migrate: restructure to company-level repo'"
echo "  4. bash ./scripts/check-template-ci.sh"
echo ""
echo "If checks pass:"
echo "  5. mv $old_company_dir $workspace_root/${company_slug}-old"
echo "  6. mv $new_company_dir $old_company_dir"
echo ""
echo "To rollback before swap:"
echo "  rm -rf $new_company_dir"
