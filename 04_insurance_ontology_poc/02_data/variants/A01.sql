-- A01: 접수 권한 검사용 — 계약에 역할이 없는 청구인 IP-0003 (계약 시스템 고객 C-10003, 토큰 TKN-C)
INSERT INTO contract.customer (cust_no, display_name, identity_token) VALUES ('C-10003', '가상 인물 C', 'TKN-C');
INSERT INTO intake.claimant (claimant_no, display_name, identity_token) VALUES ('IP-0003', '가상 인물 C', 'TKN-C');
