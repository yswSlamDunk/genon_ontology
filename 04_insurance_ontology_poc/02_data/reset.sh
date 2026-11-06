#!/usr/bin/env bash
# 보험 PoC DB를 B0 상태로 되돌린다. 테스트 전에 매번 실행한다 (명세 10.1, 11.1절).
#
#   ./reset.sh            # B0
#   ./reset.sh T09        # B0 + variants/T09.sql
#   ./reset.sh T18 SECOND # 변형 여러 개를 순서대로
#
# 접속 정보는 libpq 환경 변수로 받는다: PGHOST PGPORT PGUSER PGPASSWORD (DB를 만들 수 있는 관리자 계정)
# 그 밖의 설정:
#   INS_DB     대상 DB 이름 (기본 insurance)
#   PSQL       psql 경로 (기본: PATH의 psql)
# 계정 비밀번호(ins_reader, ins_service)는 처음 실행할 때 만들어 .env.local 에 저장한다 (권한 600).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DB="${INS_DB:-insurance}"
PSQL="${PSQL:-psql}"

ENV_FILE="$HERE/.env.local"
if [[ ! -f "$ENV_FILE" ]]; then
  umask 077
  {
    echo "INS_READER_PASSWORD=$(openssl rand -base64 18 | tr -d '/+=' )"
    echo "INS_SERVICE_PASSWORD=$(openssl rand -base64 18 | tr -d '/+=' )"
  } > "$ENV_FILE"
  echo "계정 비밀번호를 만들었습니다: $ENV_FILE"
fi
# shellcheck disable=SC1090
source "$ENV_FILE"

run() { "$PSQL" -X -q -v ON_ERROR_STOP=1 "$@"; }

# 1. DB가 없으면 만든다
if ! run -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DB'" | grep -q 1; then
  run -d postgres -c "CREATE DATABASE \"$DB\""
  echo "DB를 만들었습니다: $DB"
fi

# 2. 네 시스템의 스키마를 지우고 다시 만든다
run -d "$DB" -c "DROP SCHEMA IF EXISTS contract, intake, review, payment CASCADE"
for f in "$HERE"/schema/0[1-4]_*.sql; do
  run -d "$DB" -f "$f"
done
run -d "$DB" -v reader_pw="$INS_READER_PASSWORD" -v service_pw="$INS_SERVICE_PASSWORD" -f "$HERE/schema/09_grants.sql"

# 3. B0 — 문서·규칙 해시는 실제 파일에서 계산한다 (명세 10.1절)
DOC_HASH="$(shasum -a 256 "$HERE/seed/documents/DC-001.txt" | cut -d' ' -f1)"
RULE_HASH="$(shasum -a 256 "$HERE/seed/rules/INPATIENT-DAILY-1.0.yaml" | cut -d' ' -f1)"
LOGIC_FILE="$HERE/../03_systems/services/evaluation.py"   # 평가 로직 해시 (03_systems/서버_설계서.md 7.4절)
LOGIC_HASH="$([[ -f "$LOGIC_FILE" ]] && shasum -a 256 "$LOGIC_FILE" | cut -d' ' -f1 || true)"
run -d "$DB" -v doc_dc001_hash="$DOC_HASH" -v rule_rv001_hash="$RULE_HASH" -v logic_hash="$LOGIC_HASH" -f "$HERE/seed/b0.sql"

# 4. 테스트별 변형 (여러 개면 순서대로)
for VARIANT in "$@"; do
  VF="$HERE/variants/$VARIANT.sql"
  [[ -f "$VF" ]] || { echo "변형 파일이 없습니다: $VF" >&2; exit 1; }
  run -d "$DB" -f "$VF"
  echo "변형 적용: $VARIANT"
done

# 5. 결과 요약
run -d "$DB" -c "
SELECT s.schema, s.tbl, s.n FROM (
  SELECT 'contract' AS schema, 'customer' AS tbl, count(*) AS n FROM contract.customer UNION ALL
  SELECT 'contract', 'policy', count(*) FROM contract.policy UNION ALL
  SELECT 'contract', 'policy_role', count(*) FROM contract.policy_role UNION ALL
  SELECT 'contract', 'coverage', count(*) FROM contract.coverage UNION ALL
  SELECT 'intake', 'claimant', count(*) FROM intake.claimant UNION ALL
  SELECT 'intake', 'claim_receipt', count(*) FROM intake.claim_receipt UNION ALL
  SELECT 'intake', 'document', count(*) FROM intake.document UNION ALL
  SELECT 'intake', 'receipt_document', count(*) FROM intake.receipt_document UNION ALL
  SELECT 'review', 'rule_set_version', count(*) FROM review.rule_set_version UNION ALL
  SELECT 'review', 'insurance_event', count(*) FROM review.insurance_event UNION ALL
  SELECT 'review', 'document_verification', count(*) FROM review.document_verification UNION ALL
  SELECT 'review', 'claim', count(*) FROM review.claim UNION ALL
  SELECT 'review', 'assessment', count(*) FROM review.assessment UNION ALL
  SELECT 'review', 'review_task', count(*) FROM review.review_task UNION ALL
  SELECT 'review', 'payment_order', count(*) FROM review.payment_order UNION ALL
  SELECT 'review', 'action_log', count(*) FROM review.action_log UNION ALL
  SELECT 'payment', 'payment_request', count(*) FROM payment.payment_request
) s"
echo "완료: $DB = B0${*:+ + $*}"
