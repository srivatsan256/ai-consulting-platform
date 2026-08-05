#!/bin/bash
# Full API Test Script for AI Consulting Platform
BASE="http://localhost:8000/api"
PASS=0
FAIL=0
WARN=0

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
CYAN='\033[0;36m'
NC='\033[0m'

pass() { echo -e "${GREEN}✅ PASS${NC}: $1"; ((PASS++)); }
fail() { echo -e "${RED}❌ FAIL${NC}: $1 — $2"; ((FAIL++)); }
warn() { echo -e "${YELLOW}⚠️  WARN${NC}: $1 — $2"; ((WARN++)); }
info() { echo -e "   ${CYAN}ℹ  $1${NC}"; }
section() { echo -e "\n${BLUE}═══════════════════════════════════════${NC}"; echo -e "${BLUE}  $1${NC}"; echo -e "${BLUE}═══════════════════════════════════════${NC}"; }

# ──────────────────────────────────────────────────────────────
section "1. BACKEND HEALTH"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/")
[ "$STATUS" = "401" ] && pass "API root reachable (401 = auth required, expected)" || fail "API root" "Expected 401, got $STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/docs/")
[ "$STATUS" = "200" ] && pass "Swagger docs at /api/docs/ (200)" || fail "Swagger docs" "Got $STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/schema/")
[ "$STATUS" = "200" ] && pass "OpenAPI schema at /api/schema/ (200)" || fail "OpenAPI schema" "Got $STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/admin/")
[ "$STATUS" = "200" ] && pass "Django admin panel accessible (200)" || fail "Django admin" "Got $STATUS"

# ──────────────────────────────────────────────────────────────
section "2. AUTHENTICATION — LOGIN"

LOGIN_RESP=$(curl -s -X POST "$BASE/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email":"srivatsanr256@gmail.com","password":"TestAdmin123!"}')

TOKEN=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access',''))" 2>/dev/null)
REFRESH=$(echo "$LOGIN_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('refresh',''))" 2>/dev/null)

if [ -n "$TOKEN" ]; then
  pass "POST /auth/login/ — received access + refresh tokens"
  info "Token prefix: ${TOKEN:0:40}..."
else
  fail "POST /auth/login/" "No token in response: $LOGIN_RESP"
fi

AUTH="Authorization: Bearer $TOKEN"

# Refresh token
if [ -n "$REFRESH" ]; then
  REFRESH_RESP=$(curl -s -X POST "$BASE/auth/refresh/" \
    -H "Content-Type: application/json" \
    -d "{\"refresh\":\"$REFRESH\"}")
  NEW_TOKEN=$(echo "$REFRESH_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access',''))" 2>/dev/null)
  [ -n "$NEW_TOKEN" ] && pass "POST /auth/refresh/ — token refresh works" || fail "POST /auth/refresh/" "$REFRESH_RESP"
fi

# ──────────────────────────────────────────────────────────────
section "3. CURRENT USER & PROFILE"

ME_RESP=$(curl -s -H "$AUTH" "$BASE/auth/me/")
USERNAME=$(echo "$ME_RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('username','') or d.get('email',''))" 2>/dev/null)
if [ -n "$USERNAME" ]; then
  pass "GET /auth/me/ — user: $USERNAME"
else
  fail "GET /auth/me/" "$(echo $ME_RESP | head -c 200)"
fi

# Login history
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/auth/login-history/")
[ "$STATUS" = "200" ] && pass "GET /auth/login-history/ ($STATUS)" || warn "GET /auth/login-history/" "Got $STATUS"

# ──────────────────────────────────────────────────────────────
section "4. ACCOUNTS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/accounts/")
[ "$STATUS" = "200" ] && pass "GET /accounts/ ($STATUS)" || fail "GET /accounts/" "Got $STATUS"

# ──────────────────────────────────────────────────────────────
section "5. COMPANIES & MEMBERS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/companies/")
[ "$STATUS" = "200" ] && pass "GET /companies/ ($STATUS)" || fail "GET /companies/" "Got $STATUS"

CO_DATA=$(curl -s -H "$AUTH" "$BASE/companies/")
CO_COUNT=$(echo "$CO_DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else d.get('count','?'))" 2>/dev/null)
info "Companies in DB: $CO_COUNT"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/memberships/")
[ "$STATUS" = "200" ] && pass "GET /memberships/ ($STATUS)" || fail "GET /memberships/" "Got $STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/memberships/current/")
[ "$STATUS" = "200" ] && pass "GET /memberships/current/ ($STATUS)" || warn "GET /memberships/current/" "Got $STATUS"

# ──────────────────────────────────────────────────────────────
section "6. ROLES, PERMISSIONS, DEPARTMENTS, TEAMS"

for endpoint in roles permissions departments teams; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/$endpoint/")
  [ "$STATUS" = "200" ] && pass "GET /$endpoint/ ($STATUS)" || fail "GET /$endpoint/" "Got $STATUS"
done

# ──────────────────────────────────────────────────────────────
section "7. PROJECTS & PROJECT MEMBERS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/projects/")
[ "$STATUS" = "200" ] && pass "GET /projects/ ($STATUS)" || fail "GET /projects/" "Got $STATUS"

PROJ_DATA=$(curl -s -H "$AUTH" "$BASE/projects/")
PROJ_COUNT=$(echo "$PROJ_DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else d.get('count','?'))" 2>/dev/null)
info "Projects in DB: $PROJ_COUNT"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/project-members/")
[ "$STATUS" = "200" ] && pass "GET /project-members/ ($STATUS)" || fail "GET /project-members/" "Got $STATUS"

# ──────────────────────────────────────────────────────────────
section "8. DASHBOARD"

DASH_RESP=$(curl -s -H "$AUTH" "$BASE/dashboard/")
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/dashboard/")
[ "$STATUS" = "200" ] && pass "GET /dashboard/ ($STATUS)" || fail "GET /dashboard/" "Got $STATUS"
info "Dashboard data: $(echo $DASH_RESP | head -c 200)..."

# ──────────────────────────────────────────────────────────────
section "9. DISCOVERY / REQUIREMENTS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/discovery/")
[ "$STATUS" = "200" ] && pass "GET /discovery/ ($STATUS)" || fail "GET /discovery/" "Got $STATUS"

# ──────────────────────────────────────────────────────────────
section "10. AI ENGINE"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/ai-engine/")
[ "$STATUS" = "200" ] && pass "GET /ai-engine/ ($STATUS)" || fail "GET /ai-engine/" "Got $STATUS"

AI_RESP=$(curl -s -H "$AUTH" "$BASE/ai-engine/")
info "AI Engine endpoints: $(echo $AI_RESP | head -c 300)..."

# ──────────────────────────────────────────────────────────────
section "11. CHAT"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/chat/")
[ "$STATUS" = "200" ] && pass "GET /chat/ ($STATUS)" || fail "GET /chat/" "Got $STATUS"

CHAT_DATA=$(curl -s -H "$AUTH" "$BASE/chat/")
ROOMS=$(echo "$CHAT_DATA" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d)" 2>/dev/null | head -c 300)
info "Chat data: $ROOMS"

# ──────────────────────────────────────────────────────────────
section "12. KNOWLEDGE BASE"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/knowledge-base/")
[ "$STATUS" = "200" ] && pass "GET /knowledge-base/ ($STATUS)" || fail "GET /knowledge-base/" "Got $STATUS"

# ──────────────────────────────────────────────────────────────
section "13. TASKS & WORKFLOWS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/tasks/")
[ "$STATUS" = "200" ] && pass "GET /tasks/ ($STATUS)" || fail "GET /tasks/" "Got $STATUS"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/workflows/")
[ "$STATUS" = "200" ] && pass "GET /workflows/ ($STATUS)" || fail "GET /workflows/" "Got $STATUS"

# ──────────────────────────────────────────────────────────────
section "14. REVIEWS, APPROVALS, RISKS, ISSUES"

for endpoint in reviews approvals risks issues; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/$endpoint/")
  [ "$STATUS" = "200" ] && pass "GET /$endpoint/ ($STATUS)" || fail "GET /$endpoint/" "Got $STATUS"
done

# ──────────────────────────────────────────────────────────────
section "15. ARCHITECTURE, SECURITY, DEPLOYMENTS, MONITORING"

for endpoint in architecture security deployments monitoring; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/$endpoint/")
  [ "$STATUS" = "200" ] && pass "GET /$endpoint/ ($STATUS)" || fail "GET /$endpoint/" "Got $STATUS"
done

# ──────────────────────────────────────────────────────────────
section "16. DOCUMENTS, DOCUMENT TEMPLATES, MEETINGS"

for endpoint in documents document-templates meetings; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/$endpoint/")
  [ "$STATUS" = "200" ] && pass "GET /$endpoint/ ($STATUS)" || fail "GET /$endpoint/" "Got $STATUS"
done

# ──────────────────────────────────────────────────────────────
section "17. REPORTS, NOTIFICATIONS, AUDIT LOGS"

for endpoint in reports notifications audit-logs; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/$endpoint/")
  [ "$STATUS" = "200" ] && pass "GET /$endpoint/ ($STATUS)" || fail "GET /$endpoint/" "Got $STATUS"
done

# ──────────────────────────────────────────────────────────────
section "18. SETTINGS, SUBSCRIPTIONS, INTEGRATIONS"

for endpoint in settings subscriptions integrations; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "$AUTH" "$BASE/$endpoint/")
  [ "$STATUS" = "200" ] && pass "GET /$endpoint/ ($STATUS)" || fail "GET /$endpoint/" "Got $STATUS"
done

# ──────────────────────────────────────────────────────────────
section "19. CORS HEADERS (Frontend Integration Check)"

CORS_RESP=$(curl -s -I -X OPTIONS "http://localhost:8000/api/auth/login/" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization")
if echo "$CORS_RESP" | grep -qi "Access-Control-Allow-Origin"; then
  pass "CORS headers present for http://localhost:3000"
else
  warn "CORS headers" "May not be set correctly — check django-cors-headers"
  info "Response headers: $(echo "$CORS_RESP" | head -c 300)"
fi

# ──────────────────────────────────────────────────────────────
section "20. LOGOUT"

if [ -n "$REFRESH" ]; then
  LOGOUT_RESP=$(curl -s -X POST "$BASE/auth/logout/" \
    -H "$AUTH" \
    -H "Content-Type: application/json" \
    -d "{\"refresh\":\"$REFRESH\"}")
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/auth/logout/" \
    -H "$AUTH" \
    -H "Content-Type: application/json" \
    -d "{\"refresh\":\"$REFRESH\"}")
  [[ "$STATUS" =~ ^(200|204|205) ]] && pass "POST /auth/logout/ ($STATUS)" || warn "POST /auth/logout/" "Got $STATUS: $LOGOUT_RESP"
fi

# ──────────────────────────────────────────────────────────────
section "21. FRONTEND SERVER"

STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000/")
[ "$STATUS" = "200" ] && pass "Frontend (Vite dev server) at :3000 (200)" || fail "Frontend server" "Got $STATUS"

# Check if main JS bundle loads
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:3000/src/main.jsx" 2>/dev/null || echo "404")
HTML_CONTENT=$(curl -s "http://localhost:3000/" | head -c 500)
if echo "$HTML_CONTENT" | grep -q "RequirementAI\|root\|vite\|react"; then
  pass "Frontend HTML contains app content"
else
  warn "Frontend HTML" "Unexpected content"
fi

# ──────────────────────────────────────────────────────────────
section "FINAL SUMMARY"
echo ""
TOTAL=$((PASS + FAIL + WARN))
echo -e "   Total checks : $TOTAL"
echo -e "   ${GREEN}✅ Passed${NC}   : $PASS"
echo -e "   ${RED}❌ Failed${NC}   : $FAIL"
echo -e "   ${YELLOW}⚠️  Warnings${NC} : $WARN"
echo ""

if [ "$FAIL" = "0" ]; then
  echo -e "${GREEN}🎉 ALL TESTS PASSED! Platform is healthy.${NC}"
elif [ "$FAIL" -le 3 ]; then
  echo -e "${YELLOW}⚠️  Minor issues found ($FAIL failed). Review above.${NC}"
else
  echo -e "${RED}🚨 $FAIL test(s) failed. Backend/Frontend may have critical issues.${NC}"
fi
