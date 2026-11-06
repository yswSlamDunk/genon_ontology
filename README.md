# 온톨로지 솔루션 조사

오픈소스 온톨로지 솔루션의 UI 중심 기능 조사 → 기존 보고서(PPT) 뒤에 붙일 슬라이드 작성.

```
ontology/
├── 00_papers/                 # 온톨로지 구축 방법론 논문 (원문 + 번역·요약)
│   ├── methontology/          # METHONTOLOGY (Fernández 외, 1997) — 원문.pdf, 요약, 상세해설 (md/pdf)
│   ├── neon/                  # NeOn Methodology (Gómez-Pérez·Suárez-Figueroa, 2009 / D5.4.1·D5.4.3) — 원문.pdf, 요약, 상세해설 (md)
│   └── ontology101/           # Ontology Development 101 (Noy & McGuinness) — 원문.pdf, 요약, 상세해설 (md/pdf)
├── 01_ontological-studio/        # 주요 조사 대상 (uEngine Ontology Studio)
│   ├── repo/                  # git clone: github.com/uengine-oss/ontology-studio
│   ├── tutorials/             # 공식 튜토리얼 00~23장 md + images/ + 병합본(full.md / full.pdf)
│   ├── notes/                 # 조사·분석 노트 (md)
│   └── images/                # UI 캡처 / PPT용 이미지
├── 02_research/               # 기존 조사 자료 (비교 대상)
│   ├── protege/               # Protégé Desktop · WebProtégé
│   │   ├── protege-ui-features.md
│   │   ├── protege-install-run-guide.md
│   │   ├── images/            # protege-desktop/, webprotege/
│   │   └── demo/              # 로컬 실행본, docker-compose, 샘플(pizza.owl), 시연 캡처
│   └── palantir/              # Palantir Foundry Ontology (상용, 참고)
│       ├── palantir-report.md
│       ├── images/
│       └── ontology-docs/     # 공식 문서 "Ontology building" 399페이지 한국어 번역 (README.md 목차, 00_전체요약.md)
├── 03_ppt/
│   ├── base/                  # 원본 보고서 (v2.7, 수정하지 않음)
│   ├── 01_오픈소스_조사/       # 오픈소스 조사 보고서: md(원본), pdf, pptx, 예상 질의응답
│   ├── 02_보험_온톨로지_PoC/   # 보험 청구 심사 PoC 보고서: md(원본). PPT 양식은 오픈소스 조사 v2.pptx
│   ├── new/                   # (정리 중) 오픈소스 조사 v2.pptx — PowerPoint를 닫은 뒤 01_오픈소스_조사/로 옮김
│   └── merged/                # base + 새 보고서 병합본
└── 04_insurance_ontology_poc/ # 보험 온톨로지 PoC 작업 폴더 (명세, 데이터, 업무 시스템, Studio 구축 기록, 앱)
```

## 참고 링크
- Ontology Studio repo: https://github.com/uengine-oss/ontology-studio
- Ontology Studio 소개: https://www.uengine.org/en/contents/ontologystudio.html
