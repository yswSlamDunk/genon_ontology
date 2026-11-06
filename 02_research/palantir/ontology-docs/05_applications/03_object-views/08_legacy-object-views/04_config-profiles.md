# 프로필 구성하기 (Configure profiles)

- 원문: https://www.palantir.com/docs/foundry/object-views/config-profiles/
- 사이드바 위치: Applications > Object Views > Legacy Object Views > Configure profiles

이 페이지는 사용자 역할에 따라 Object View의 탭을 다르게 보여 주는 프로필(profile) 기능을 설명합니다. 사용자 그룹을 프로필로 등록하는 방법, 탭에 프로필을 지정하는 방법, 사용자와 편집자가 프로필을 전환하는 방법, 기본 프로필을 정하는 방법을 다룹니다.

**프로필(Profiles)을** 사용하면 서로 다른 역할을 가진 사용자에게 Object View를 어떻게 보여 줄지 구성할 수 있습니다. 프로필로 사용자마다 Object View [탭](02_config-tabs.md)의 표시 여부를 제어해, 각자 필요에 맞는 뷰를 보게 할 수 있습니다.

**설명**: 예를 들어 Patient 객체 타입의 Object View에 "진료 기록", "보험 청구", "병상 배정" 탭이 있다고 합시다. "의사" 프로필에는 진료 기록 탭을, "원무과" 프로필에는 보험 청구 탭을 보이게 하면 같은 환자 객체를 열어도 역할에 따라 보이는 탭이 달라집니다. 프로필은 화면 구성을 바꾸는 기능이며, 데이터 접근 권한 자체를 제한하는 보안 기능은 아닙니다.

<a id="configure-a-profile"></a>
### 프로필 구성하기 (Configure a profile)

Object Explorer는 `Hubble`이라는 서비스로 구동됩니다. 그룹을 Object View의 프로필로 사용하려면, Platform Settings의 [**Groups** 탭](https://www.palantir.com/docs/foundry/security/users-and-groups/)에서 다음 Hubble 속성(attribute)을 추가합니다.

* `hubble:isProfile` : `true`
* `hubble:displayName` : `Set a name you want end user to see`(최종 사용자에게 보일 이름을 지정)
* \[선택 사항(OPTIONAL)] `hubble:isDiscoverable` : `true`
  * `hubble:isDiscoverable` 속성을 `true`로 설정하면 그룹 자체의 구성원이 아닌 사용자에게도 프로필이 보이게 됩니다. 이 속성을 생략하면 그룹에 속한 사용자만 이 프로필에 지정된 뷰에 접근할 수 있습니다.

<img alt="Object View 프로필 구성하기" src="https://www.palantir.com/docs/resources/foundry/object-views/custom-object-views_profiles_multipass_ui.png"/>

새로 만든 프로필이 Object View 편집기에서 사용 가능해지기까지 최대 5분이 걸릴 수 있습니다.

**설명**: 프로필은 별도로 만드는 객체가 아니라 기존 사용자 그룹에 키-값 형태의 속성을 붙여 "이 그룹은 프로필로도 쓴다"고 표시하는 방식입니다. `hubble:isProfile = true`가 그 표시이고, `hubble:displayName`은 화면에 보일 이름입니다.

<a id="assign-a-profile-to-an-object-view"></a>
### Object View에 프로필 지정하기 (Assign a profile to an Object View)

프로필은 탭 수준에서 지정합니다. 즉, 탭마다 특정 프로필을 지정할 수 있습니다. 탭에 프로필을 추가하려면 편집기 사이드바로 들어가 **Tab** 설정에서 탭을 클릭하고, **Visibility**를 선택한 다음 **Add a profile**을 클릭합니다.

![Object View 탭에 프로필 추가하기](https://www.palantir.com/docs/resources/foundry/object-views/add-profile-to-object-view-tab.png)

<a id="switch-profiles-as-a-user"></a>
### 사용자로서 프로필 전환하기 (Switch profiles as a user)

Object View에 프로필을 추가하면 프로필 사이를 전환할 수 있습니다. Object View 헤더에서 프로필 유형을 선택하면 사용 가능한 프로필이 담긴 드롭다운 메뉴가 열립니다. Object View 상단의 **Viewing Object As:**(다음 자격으로 객체 보기)를 클릭해도 같은 드롭다운 메뉴를 찾을 수 있습니다.

![Object View에서 프로필 뷰 전환하기](https://www.palantir.com/docs/resources/foundry/object-views/switch-object-view-profiles.png)

<a id="switch-profiles-as-an-editor"></a>
### 편집자로서 프로필 전환하기 (Switch profiles as an editor)

Object View를 편집하는 중에도 여러 프로필에 접근할 수 있습니다. 그러면 각 프로필에서 어떤 탭이 보이는지 확인할 수 있습니다.

![Object View에서 편집자로서 프로필 뷰 전환하기](https://www.palantir.com/docs/resources/foundry/object-views/switch-profile-view-editor.png)

<a id="set-a-default-profile-for-a-user"></a>
### 사용자의 기본 프로필 설정하기 (Set a default profile for a user)

사용자나 사용자 그룹의 기본 프로필을 설정하려면, 그 사용자를 프로필의 기반이 되는 그룹에 구성원으로 추가합니다. 이 방법은 사용자가 단 하나의 프로필에만 속해 있을 때만 동작합니다.

**주의**: Object View 하나에는 최대 10개의 프로필을 추가할 수 있습니다.

## 정리

- 프로필은 사용자 역할에 따라 Object View 탭의 표시 여부를 다르게 하는 기능입니다.
- 사용자 그룹에 `hubble:isProfile`, `hubble:displayName`(선택적으로 `hubble:isDiscoverable`) 속성을 붙이면 그 그룹이 프로필이 되며, 반영까지 최대 5분이 걸릴 수 있습니다.
- 프로필은 탭 단위로 **Visibility > Add a profile**에서 지정합니다.
- 사용자는 헤더나 **Viewing Object As:** 메뉴로, 편집자는 편집기에서 프로필을 전환해 볼 수 있습니다.
- 기본 프로필은 사용자를 해당 그룹에 추가해 정하며(프로필이 하나일 때만), Object View당 프로필은 최대 10개입니다.
