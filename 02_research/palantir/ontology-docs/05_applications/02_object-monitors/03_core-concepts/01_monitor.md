# 모니터 (Monitors)

- 원문: https://www.palantir.com/docs/foundry/object-monitors/monitor/
- 사이드바 위치: Applications > Object Monitors [Sunset] > Core concepts > Monitors

이 페이지는 Object Monitors의 핵심 단위인 모니터(monitor)가 무엇이고, 어디에 저장되며, 활동 기록을 얼마나 보관하고, 언제 만료되는지를 설명합니다. 모니터가 영구적으로 동작하지 않고 최대 3개월의 만료일을 가진다는 점이 실무에서 특히 중요합니다.

**주의**: 단계적 종료(Sunset). Object Monitors는 [Automate](https://www.palantir.com/docs/foundry/automate/overview/)로 대체되었습니다. Automate는 이전 버전과 완전히 호환되는 제품으로, 플랫폼의 모든 비즈니스 자동화를 위한 단일 진입점을 제공합니다.

모니터는 하나 이상의 입력에 대한 조건과, 그 입력 조건이 충족될 때 실행되어야 하는 액션이나 알림을 정의하는 리소스입니다.

**설명**: 모니터 하나는 "무엇을 볼지(입력), 언제 반응할지(조건), 어떻게 반응할지(액션, 알림)"의 세 부분으로 이루어진 설정 묶음입니다. 예를 들어 입력은 "재고 10개 미만인 창고" 탐색, 조건은 "결과에 객체가 새로 추가됨", 반응은 "담당자에게 이메일"처럼 구성됩니다.

<a id="storage"></a>
## 저장 (Storage)

객체 모니터는 Foundry 프로젝트 계층 구조에 저장되며, 저장, 공유, 이동, 삭제, 역할 기반 접근 제어 같은 표준 리소스 작업을 지원합니다.

[Foundry 파일 시스템](https://www.palantir.com/docs/foundry/compass/move-and-share-resources/)에 대해 알아봅니다.

객체 모니터는 다음 형식의 고유 리소스 식별자로 식별됩니다.

```
ri.object-sentinel.main.monitor.0cabb748-cf89-4404-be3c-c8f198cb2a0b
```

**설명**: 이 문자열은 RID(Resource Identifier)이며, `ri.<서비스>.<인스턴스>.<리소스 종류>.<UUID>` 구조로 되어 있습니다. 여기서 `object-sentinel`은 모니터를 관리하는 서비스 이름, `monitor`는 리소스 종류, 마지막 부분은 전역적으로 유일한 UUID입니다. 데이터셋이나 탐색처럼 모니터도 이 RID로 플랫폼 어디서든 하나로 특정됩니다.

<a id="retention"></a>
## 보존 (Retention)

객체 모니터의 과거 활동은 6개월 동안 보존되며, 그 이후에는 영구 삭제됩니다. 이 기간 이후에도 과거 활동을 보관해야 한다면, 액션을 사용해 [Foundry 온톨로지](../../../01_ontology-building/01_overview.md)의 다른 사용자 생성 객체와 똑같이 관리되고 통제되는 장기 보존용 객체에 데이터를 저장할 수 있습니다.

데이터가 삭제되면 Object Monitor 애플리케이션의 모니터 활동 **History** 탭에서도 제거됩니다. **History** 탭은 먼저 모니터를 클릭해 개요 패널을 펼친 다음 **History**를 클릭해 찾을 수 있습니다.

**설명**: 예를 들어 감사(audit) 목적으로 경보 기록을 몇 년간 남겨야 한다면, 모니터가 발동될 때마다 실행되는 액션이 `AlertLog`라는 객체 타입에 "발생 시각, 대상 객체, 조건 이름"을 담은 객체를 하나씩 만들도록 구성할 수 있습니다. 이렇게 만든 객체는 일반 온톨로지 데이터이므로 6개월 보존 기한의 영향을 받지 않습니다.

<a id="expiration"></a>
## 만료 (Expiration)

객체 모니터에는 항상 만료일이 있습니다. 허용되는 가장 늦은 만료일은 현재로부터 3개월 뒤이며, 모니터에 대해 `Editor` 역할을 가진 사용자는 언제든 만료일을 갱신할 수 있습니다.

만료일은 Object Monitors 애플리케이션 화면에서 확인하고 연장할 수 있습니다. 모니터를 클릭하면 화면 오른쪽에 모니터 개요 패널이 표시됩니다. 그런 다음 **Details** 탭을 클릭합니다.

![Details 탭의 모니터 만료일](https://www.palantir.com/docs/resources/foundry/object-monitors/view_and_extend_monitor_expiration.png)

[Object Explorer](../02_create_new_object_monitor.md#create-from-object-explorer)나 [Object Monitors](../02_create_new_object_monitor.md#create-from-object-monitors-application) 애플리케이션에서 새 객체 모니터를 만드는 방법을 알아봅니다.

## 정리

- 모니터는 입력, 조건, 그리고 조건 충족 시의 액션이나 알림을 정의하는 리소스입니다.
- 모니터는 프로젝트 계층에 저장되는 일반 리소스로, 저장, 공유, 이동, 삭제와 역할 기반 접근 제어를 지원하며 `ri.object-sentinel...` 형식의 RID로 식별됩니다.
- 과거 활동은 6개월 뒤 영구 삭제되므로, 더 오래 보관하려면 액션으로 별도 객체에 기록합니다.
- 모니터는 최대 3개월 뒤까지의 만료일을 가지며, `Editor` 역할을 가진 사용자가 Details 탭에서 연장할 수 있습니다.
