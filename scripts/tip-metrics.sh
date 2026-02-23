#!/usr/bin/env bash
# tip-metrics.sh - Track TIP health metrics

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIPS_DIR="$(dirname "$SCRIPT_DIR")/tips"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== TIP Metrics ===${NC}\n"

# Count TIPs by kind
meta_count=$(find "$TIPS_DIR/meta" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
domain_dir="$TIPS_DIR/domain"
if [[ -d "$domain_dir" ]]; then
    domain_count=$(find "$domain_dir" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
else
    domain_count=0
fi
total=$((meta_count + domain_count))

echo -e "TIP Count:"
echo -e "  Total:     ${GREEN}$total${NC}"
echo -e "  Meta:      $meta_count"
echo -e "  Domain:    $domain_count"
echo ""

# Status breakdown
proposed=0
accepted=0
deprecated=0

while IFS= read -r tip; do
    if [[ -f "$tip" ]]; then
        status=$(grep "status:" "$tip" 2>/dev/null | head -1 | awk '{print $2}' || echo "unknown")
        case "$status" in
            proposed) proposed=$((proposed + 1)) ;;
            accepted) accepted=$((accepted + 1)) ;;
            deprecated) deprecated=$((deprecated + 1)) ;;
        esac
    fi
done < <(find "$TIPS_DIR" -name "*.md" -type f 2>/dev/null)

echo -e "Status Breakdown:"
echo -e "  Accepted:   ${GREEN}$accepted${NC}"
echo -e "  Proposed:   ${YELLOW}$proposed${NC}"
echo -e "  Deprecated: ${RED}$deprecated${NC}"

if [ "$total" -gt 0 ]; then
    acceptance_rate=$((accepted * 100 / total))
    echo -e "\nAcceptance Rate: ${GREEN}${acceptance_rate}%${NC}"
fi

# List TIPs
echo -e "\n${BLUE}All TIPs:${NC}"
while IFS= read -r tip; do
    if [[ -f "$tip" ]]; then
        name=$(basename "$tip" .md)
        kind=$(basename "$(dirname "$tip")")
        status=$(grep "status:" "$tip" 2>/dev/null | head -1 | awk '{print $2}' || echo "unknown")
        echo -e "  [$kind] $name (${status})"
    fi
done < <(find "$TIPS_DIR" -name "*.md" -type f 2>/dev/null | sort)
