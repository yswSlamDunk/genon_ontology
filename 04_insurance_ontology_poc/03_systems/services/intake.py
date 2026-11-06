"""접수 시스템 (ins-intake, :18102) — 청구인, 청구 접수 원본, 첨부 서류 원문. 인증: Basic (env INS_INTAKE_BASIC = 사용자:비밀번호).

접수된 그대로의 원본을 다룬다. 확인된 사실과 심사 상태는 심사 시스템에 있다 (명세 4.2, 12.2절).
식별자: 청구인 IP-…, 접수 번호 RC-…, 사고번호 ACC-…, 서류 DC-…, 연결 AT-…. 계약은 대외 계약 번호(policy_number)로 가리킨다.
쓰기: A01 1단계(createReceipt, 보상 cancelReceipt), A02 1단계(attachDocument, 보상 revertAttachment), registerDocument.
"""

from __future__ import annotations

import datetime as dt

from fastapi import Depends, Query
from psycopg.types.json import Jsonb
from pydantic import BaseModel, Field

from common import (LIMIT, DependencyError, IdemKey, Reject, call, basic_auth, db, db_write, idem_begin, idem_finish, make_app, next_id, one,
                    plain, rows, where)

app = make_app(
    title="접수 시스템",
    description="보험금 청구 접수 시스템. 청구인, 청구 접수 원본(신고된 입퇴원일 포함), 첨부 서류 원문과 추출값 후보를 다룬다. "
                "여기 값은 확인 전 값이다. 쓰기: 청구 접수 생성·취소, 서류 등록, 접수에 서류 연결·교체·되돌리기. "
                "데이터는 insurance DB의 intake 스키마다.",
    schema="intake",
)
auth = basic_auth("INS_INTAKE_BASIC")
AUTH = [Depends(auth)]
S = "intake"

CLAIMANT = "SELECT claimant_no, display_name, identity_token, created_at FROM intake.claimant"
RECEIPT = ("SELECT receipt_no, request_key, policy_number, coverage_code, submitter_no, patient_no, accident_no, "
           "provider_code, admission_date, discharge_date, received_at, cancelled_at, cancel_reason, created_at "
           "FROM intake.claim_receipt")
DOCUMENT = ("SELECT doc_id, document_type, storage_ref, content_hash, extracted_facts, uploaded_at, created_at "
            "FROM intake.document")
ATTACH = ("SELECT rd.attachment_id, rd.receipt_no, rd.doc_id, d.document_type, d.content_hash, rd.attached_at, "
          "rd.detached_at, rd.detach_reason, rd.replaces_attachment_id "
          "FROM intake.receipt_document rd JOIN intake.document d USING (doc_id)")


# ── 조회 ─────────────────────────────────────────────────────────────────────

@app.get("/claimants/{claimant_no}", operation_id="getClaimant", summary="청구인 조회", dependencies=AUTH,
         description="접수 시스템 청구인 번호(예: IP-0001)로 1명을 돌려준다.")
def get_claimant(claimant_no: str):
    with db() as conn:
        return one(conn, CLAIMANT + " WHERE claimant_no = %s", (claimant_no,), f"청구인 {claimant_no}")


@app.get("/claimants", operation_id="listClaimants", summary="청구인 목록", dependencies=AUTH,
         description="identity_token 을 주면 그 토큰의 청구인만 돌려준다 (계약 시스템 고객과 동일인 대조).")
def list_claimants(identity_token: str | None = Query(None, description="동일인 대조 토큰 (예: TKN-B)"), limit: int = LIMIT):
    w, p = where({"identity_token": identity_token})
    with db() as conn:
        return rows(conn, CLAIMANT + w + " ORDER BY claimant_no LIMIT %s", (*p, limit))


@app.get("/receipts/{receipt_no}", operation_id="getReceipt", summary="청구 접수 조회 (첨부 서류 포함)", dependencies=AUTH,
         description="접수 번호(예: RC-0001)로 접수 원본 1건과 서류 연결 이력을 돌려준다. detached_at 이 비어 있으면 현재 연결된 서류다.")
def get_receipt(receipt_no: str):
    with db() as conn:
        receipt = one(conn, RECEIPT + " WHERE receipt_no = %s", (receipt_no,), f"접수 {receipt_no}")
        receipt["documents"] = rows(conn, ATTACH + " WHERE rd.receipt_no = %s ORDER BY rd.attached_at, rd.attachment_id",
                                    (receipt_no,))
        return receipt


@app.get("/receipts", operation_id="listReceipts", summary="청구 접수 목록", dependencies=AUTH,
         description="대외 계약 번호, 사고번호, 입원한 사람(청구인 번호)으로 접수를 찾는다. 같은 사고의 다른 청구를 찾을 때 쓴다.")
def list_receipts(policy_number: str | None = Query(None, description="대외 계약 번호"),
                  accident_no: str | None = Query(None, description="접수 사고번호 (예: ACC-0001)"),
                  patient_no: str | None = Query(None, description="입원한 사람의 청구인 번호"),
                  limit: int = LIMIT):
    w, p = where({"policy_number": policy_number, "accident_no": accident_no, "patient_no": patient_no})
    with db() as conn:
        return rows(conn, RECEIPT + w + " ORDER BY received_at, receipt_no LIMIT %s", (*p, limit))


@app.get("/documents/{doc_id}", operation_id="getDocument", summary="첨부 서류 조회", dependencies=AUTH,
         description="서류 ID(예: DC-001)로 원문 위치, 해시, 추출값 후보를 돌려준다. 추출값은 확인값이 아니다.")
def get_document(doc_id: str):
    with db() as conn:
        return one(conn, DOCUMENT + " WHERE doc_id = %s", (doc_id,), f"서류 {doc_id}")


@app.get("/documents/{doc_id}/receipts", operation_id="listDocumentReceipts", summary="서류가 연결된 접수 목록",
         dependencies=AUTH, description="서류가 연결된(또는 연결됐던) 접수와 연결 이력을 돌려준다. detached_at 이 비어 있으면 현재 연결.")
def list_document_receipts(doc_id: str):
    with db() as conn:
        one(conn, "SELECT 1 FROM intake.document WHERE doc_id = %s", (doc_id,), f"서류 {doc_id}")
        return rows(conn, ATTACH + " WHERE rd.doc_id = %s ORDER BY rd.attached_at, rd.attachment_id", (doc_id,))


# ── 쓰기 ─────────────────────────────────────────────────────────────────────

class ReceiptIn(BaseModel):
    request_key: str = Field(..., description="접수 요청 키 (중복 접수 방지). 같은 키로 다시 오면 기존 접수를 돌려준다")
    policy_number: str = Field(..., description="대외 계약 번호 (예: TEST-POLICY-001)")
    coverage_code: str = Field(..., description="청구한 보장 코드 (예: INPATIENT-DAILY-A)")
    submitter_no: str = Field(..., description="제출자 청구인 번호 (예: IP-0001)")
    patient_no: str = Field(..., description="입원한 사람의 청구인 번호 (예: IP-0002)")
    accident_no: str = Field(..., description="접수 사고번호 (예: ACC-0002)")
    provider_code: str | None = Field(None, description="신고된 의료기관 코드")
    admission_date: dt.date | None = Field(None, description="신고된 입원일 (확인 전 값)")
    discharge_date: dt.date | None = Field(None, description="신고된 퇴원일 (확인 전 값)")
    received_at: dt.datetime | None = Field(None, description="접수 시각 (없으면 지금)")
    actor_id: str = Field(..., description="실행자 (접수 담당자)")


class CancelIn(BaseModel):
    reason: str = Field(..., description="취소 사유")
    actor_id: str = Field(..., description="실행자")


class DocumentIn(BaseModel):
    document_type: str = Field(..., description="HOSPITALIZATION_CERTIFICATE 또는 OTHER")
    storage_ref: str = Field(..., description="원문 위치")
    content_hash: str = Field(..., description="원문 SHA-256")
    extracted_facts: dict | None = Field(None, description="추출값 후보와 신뢰도 (확인값 아님)")
    uploaded_at: dt.datetime | None = Field(None, description="올린 시각 (없으면 지금)")
    actor_id: str = Field(..., description="실행자")


class AttachIn(BaseModel):
    doc_id: str = Field(..., description="연결할 서류 ID")
    replaces_doc_id: str | None = Field(None, description="교체할 서류 ID (선택). 주면 그 연결을 해제한다")
    actor_id: str = Field(..., description="실행자 (접수 담당자 또는 담당 심사자)")


class RevertIn(BaseModel):
    reason: str | None = Field(None, description="되돌리는 사유")
    actor_id: str = Field(..., description="실행자")


def _write(action_type: str, actor_id: str, key: str, payload: dict, fn):
    with db_write() as conn:
        prev = idem_begin(conn, S, action_type, actor_id, key, payload)
        if prev is not None:
            return prev
        return idem_finish(conn, S, action_type, actor_id, key, fn(conn))


CLOSED = {"APPROVED", "REJECTED", "PAID"}


def _claims_of(receipt_no: str) -> list[dict]:
    """심사 시스템에서 이 접수로 등록된 청구. 조회하지 못하면 되돌리지 않는다 (503)."""
    try:
        status, data = call("review", "GET", "/claims", params={"receipt_no": receipt_no})
    except DependencyError as exc:
        raise Reject("DEPENDENCY_UNAVAILABLE", f"심사 시스템을 조회하지 못해 되돌리지 않습니다: {exc.detail}", 503)
    if status >= 400:
        raise Reject("DEPENDENCY_UNAVAILABLE", f"심사 시스템 청구 조회 실패 HTTP {status}", 503)
    return data


def _receipt(conn, receipt_no: str, lock: bool = False) -> dict:
    return one(conn, RECEIPT + " WHERE receipt_no = %s" + (" FOR UPDATE" if lock else ""), (receipt_no,), f"접수 {receipt_no}")


@app.post("/receipts", operation_id="createReceipt", summary="청구 접수 생성 (A01 1단계)", dependencies=AUTH,
          description="청구 접수 원본을 만든다. 같은 request_key 가 이미 있으면 내용이 같을 때 기존 접수를, 다르면 409 IDEMPOTENCY_CONFLICT. "
                      "다음 단계는 심사 시스템 registerClaim(receipt_no). 실패 시 보상은 cancelReceipt.")
def create_receipt(body: ReceiptIn, idem: str = IdemKey):
    fields = body.model_dump(exclude={"actor_id", "received_at"})

    def run(conn):
        prev = conn.execute(RECEIPT + " WHERE request_key = %s", (body.request_key,)).fetchone()
        if prev:
            if any(plain(prev[k]) != plain(v) for k, v in fields.items()):
                raise Reject("IDEMPOTENCY_CONFLICT", f"접수 요청 키 {body.request_key} 는 다른 내용으로 이미 접수됐습니다")
            return prev
        for who in {body.submitter_no, body.patient_no}:
            if not conn.execute("SELECT 1 FROM intake.claimant WHERE claimant_no = %s", (who,)).fetchone():
                raise Reject("REFERENCE_NOT_FOUND", f"청구인 {who} 가 없습니다")
        no = next_id(conn, "intake.receipt_seq", "RC-", 4)
        conn.execute("INSERT INTO intake.claim_receipt (receipt_no, request_key, policy_number, coverage_code, submitter_no, "
                     "patient_no, accident_no, provider_code, admission_date, discharge_date, received_at) "
                     "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, coalesce(%s, now()))",
                     (no, body.request_key, body.policy_number, body.coverage_code, body.submitter_no, body.patient_no,
                      body.accident_no, body.provider_code, body.admission_date, body.discharge_date, body.received_at))
        return _receipt(conn, no)
    return _write("createReceipt", body.actor_id, idem, body.model_dump(), run)


@app.post("/receipts/{receipt_no}/cancel", operation_id="cancelReceipt", summary="청구 접수 취소 (A01 보상)",
          dependencies=AUTH, description="접수를 취소 상태로 둔다(행은 지우지 않는다). 이미 취소됐으면 그대로 돌려준다. "
                                         "취소된 접수로는 청구를 등록할 수 없다. 심사 시스템에 이 접수의 청구가 이미 있으면 409 RECEIPT_IN_USE "
                                         "(성공한 A01 은 취소할 수 없다).")
def cancel_receipt(receipt_no: str, body: CancelIn, idem: str = IdemKey):
    def run(conn):
        r = _receipt(conn, receipt_no, lock=True)
        if r["cancelled_at"] is None:
            claims = _claims_of(receipt_no)
            if claims:
                raise Reject("RECEIPT_IN_USE", f"접수 {receipt_no} 로 청구 {claims[0]['claim_id']} 가 이미 등록돼 취소할 수 없습니다")
            conn.execute("UPDATE intake.claim_receipt SET cancelled_at = now(), cancel_reason = %s WHERE receipt_no = %s",
                         (body.reason, receipt_no))
        return _receipt(conn, receipt_no)
    return _write("cancelReceipt", body.actor_id, idem, {"receipt_no": receipt_no, **body.model_dump()}, run)


@app.post("/documents", operation_id="registerDocument", summary="서류 등록", dependencies=AUTH,
          description="새 서류(원문 위치·해시·추출값 후보)를 등록하고 서류 ID(DC-…)를 돌려준다. 접수에 연결은 attachDocument.")
def register_document(body: DocumentIn, idem: str = IdemKey):
    if body.document_type not in ("HOSPITALIZATION_CERTIFICATE", "OTHER"):
        raise Reject("INVALID_INPUT", "document_type 은 HOSPITALIZATION_CERTIFICATE 또는 OTHER", 422)

    def run(conn):
        doc_id = next_id(conn, "intake.document_seq", "DC-", 3)
        conn.execute("INSERT INTO intake.document (doc_id, document_type, storage_ref, content_hash, extracted_facts, "
                     "uploaded_at) VALUES (%s, %s, %s, %s, %s, coalesce(%s, now()))",
                     (doc_id, body.document_type, body.storage_ref, body.content_hash,
                      Jsonb(body.extracted_facts) if body.extracted_facts is not None else None, body.uploaded_at))
        return one(conn, DOCUMENT + " WHERE doc_id = %s", (doc_id,), doc_id)
    return _write("registerDocument", body.actor_id, idem, body.model_dump(), run)


@app.post("/receipts/{receipt_no}/documents", operation_id="attachDocument", summary="접수에 서류 연결·교체 (A02 1단계)",
          dependencies=AUTH,
          description="서류를 접수에 연결한다. replaces_doc_id 를 주면 그 서류의 현재 연결을 해제하고 새 서류로 바꾼다. "
                      "응답의 attachment_id 는 보상 revertAttachment 에 쓴다. 다음 단계는 심사 시스템 recordEvidenceAttached.")
def attach_document(receipt_no: str, body: AttachIn, idem: str = IdemKey):
    def run(conn):
        r = _receipt(conn, receipt_no, lock=True)
        if r["cancelled_at"] is not None:
            raise Reject("RECEIPT_CANCELLED", f"접수 {receipt_no} 는 취소됐습니다")
        one(conn, "SELECT 1 FROM intake.document WHERE doc_id = %s", (body.doc_id,), f"서류 {body.doc_id}")
        if conn.execute("SELECT 1 FROM intake.receipt_document WHERE receipt_no = %s AND doc_id = %s AND detached_at IS NULL",
                        (receipt_no, body.doc_id)).fetchone():
            raise Reject("ALREADY_ATTACHED", f"서류 {body.doc_id} 는 이미 접수 {receipt_no} 에 연결돼 있습니다")
        replaced = None
        if body.replaces_doc_id:
            replaced = conn.execute("SELECT attachment_id FROM intake.receipt_document WHERE receipt_no = %s AND doc_id = %s "
                                    "AND detached_at IS NULL", (receipt_no, body.replaces_doc_id)).fetchone()
            if not replaced:
                raise Reject("NOT_ATTACHED", f"교체할 서류 {body.replaces_doc_id} 가 접수 {receipt_no} 에 연결돼 있지 않습니다")
            conn.execute("UPDATE intake.receipt_document SET detached_at = now(), detach_reason = 'REPLACED' "
                         "WHERE attachment_id = %s", (replaced["attachment_id"],))
        att = next_id(conn, "intake.attachment_seq", "AT-", 4)
        conn.execute("INSERT INTO intake.receipt_document (attachment_id, receipt_no, doc_id, attached_at, replaces_attachment_id) "
                     "VALUES (%s, %s, %s, now(), %s)", (att, receipt_no, body.doc_id, replaced and replaced["attachment_id"]))
        return {"attachment_id": att, "receipt_no": receipt_no, "doc_id": body.doc_id,
                "replaced_attachment_id": replaced and replaced["attachment_id"], "replaced_doc_id": body.replaces_doc_id,
                "documents": rows(conn, ATTACH + " WHERE rd.receipt_no = %s AND rd.detached_at IS NULL "
                                                 "ORDER BY rd.attachment_id", (receipt_no,))}
    return _write("attachDocument", body.actor_id, idem, {"receipt_no": receipt_no, **body.model_dump()}, run)


@app.post("/attachments/{attachment_id}/revert", operation_id="revertAttachment", summary="서류 연결 되돌리기 (A02 보상)",
          dependencies=AUTH,
          description="attachDocument 가 만든 연결을 해제한다. 교체였으면 바뀌었던 서류를 다시 연결한다. 이미 되돌렸으면 그대로 돌려준다. "
                      "그 접수의 청구가 종결(APPROVED·REJECTED·PAID)됐으면 409 CLAIM_CLOSED.")
def revert_attachment(attachment_id: str, body: RevertIn, idem: str = IdemKey):
    def run(conn):
        a = one(conn, "SELECT * FROM intake.receipt_document WHERE attachment_id = %s FOR UPDATE", (attachment_id,),
                f"연결 {attachment_id}")
        restored = None
        if a["detached_at"] is None:
            closed = [c["claim_id"] for c in _claims_of(a["receipt_no"]) if c["status"] in CLOSED]
            if closed:
                raise Reject("CLAIM_CLOSED", f"청구 {closed[0]} 가 이미 종결돼 서류 연결을 되돌릴 수 없습니다")
            conn.execute("UPDATE intake.receipt_document SET detached_at = now(), detach_reason = 'REVERTED' "
                         "WHERE attachment_id = %s", (attachment_id,))
            if a["replaces_attachment_id"]:
                old = one(conn, "SELECT * FROM intake.receipt_document WHERE attachment_id = %s",
                          (a["replaces_attachment_id"],), "바뀌었던 연결")
                if not conn.execute("SELECT 1 FROM intake.receipt_document WHERE receipt_no = %s AND doc_id = %s "
                                    "AND detached_at IS NULL", (old["receipt_no"], old["doc_id"])).fetchone():
                    restored = next_id(conn, "intake.attachment_seq", "AT-", 4)
                    conn.execute("INSERT INTO intake.receipt_document (attachment_id, receipt_no, doc_id, attached_at) "
                                 "VALUES (%s, %s, %s, now())", (restored, old["receipt_no"], old["doc_id"]))
        elif a["detach_reason"] != "REVERTED":
            raise Reject("INVALID_STATE", f"연결 {attachment_id} 는 이미 {a['detach_reason']} 로 해제됐습니다")
        return {"attachment_id": attachment_id, "receipt_no": a["receipt_no"], "doc_id": a["doc_id"],
                "restored_attachment_id": restored,
                "documents": rows(conn, ATTACH + " WHERE rd.receipt_no = %s AND rd.detached_at IS NULL "
                                                 "ORDER BY rd.attachment_id", (a["receipt_no"],))}
    return _write("revertAttachment", body.actor_id, idem, {"attachment_id": attachment_id, **body.model_dump()}, run)
